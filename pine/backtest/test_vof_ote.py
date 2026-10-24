import email.message
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis as an  # noqa: E402
import vof_ote as v  # noqa: E402

# idx: open, high, low, close. Swing high 110 @3, swing low 100 @8 (confirmed @10), breakout @11, retrace @12.
# Bars 10-11 leave a genuine fair value gap (104 .. 104.2) inside the OTE zone; no score item is forced.
SCENARIO = [
    (104, 106, 103, 105), (105, 107, 104, 106), (106, 108, 105, 107), (107, 110, 106, 108),
    (108, 109, 105, 106), (106, 107, 103, 104), (104, 105, 102, 103), (103, 104, 101, 102),
    (102, 103, 100, 101), (101, 104, 101, 103), (103, 105, 102, 104.5),
    (104.5, 111, 104.2, 110.8), (104.5, 108, 104.0, 107),
]
VOL = [1000.0] * 12 + [2000.0]  # volume spike on the retrace bar 12 -> RVOL 2000 / 1200 = 1.67
# small HTF/volume windows so a 13-bar scenario warms up; HTF bars are 60 min here
P = dict(swing_left=3, swing_right=2, htf_minutes=60, htf_ema_fast=2, htf_ema_slow=3, vol_ma_len=5, cvd_len=3)


def make_df(bars, start="2024-11-11 03:00", freq="1h", vol=1000.0):
    idx = pd.date_range(start, periods=len(bars), freq=freq, tz=v.TZ)
    df = pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx, dtype=float)
    df["volume"] = vol
    return df


def scen(bars=SCENARIO, start="2024-11-11 03:00", vol=VOL):
    """Scenario with the volume spike; volume beyond the VOL list is 1000."""
    return make_df(bars, start, vol=(list(vol) + [1000.0] * len(bars))[:len(bars)])


class Indicators(unittest.TestCase):
    def test_pivot_and_confirmation_delay(self):
        out = v.pivots(np.array([1, 2, 3, 5, 3, 2, 1.0]), 2, 1, True)
        self.assertTrue(np.isnan(out[3]))  # not known on the pivot bar itself
        self.assertEqual(out[4], 5)  # confirmed `right` bars later
        self.assertEqual(np.isnan(out).sum(), 6)

    def test_pivot_low_and_ties(self):
        self.assertEqual(v.pivots(np.array([5, 4, 1, 4, 5.0]), 2, 2, False)[4], 1)
        self.assertTrue(np.isnan(v.pivots(np.array([1, 5, 5, 1.0]), 1, 1, True)).all())

    def test_ema_seed(self):
        out = v.ema(np.array([1, 2, 3, 4, 5.0]), 3)
        self.assertTrue(np.isnan(out[:2]).all())
        self.assertEqual(list(out[2:]), [2.0, 3.0, 4.0])

    def test_sessions(self):
        w = v.in_session_window
        self.assertTrue(w(19 * 60, "1900-0200") and w(60, "1900-0200") and w(23 * 60 + 59, "1900-0200"))
        self.assertFalse(w(2 * 60, "1900-0200") or w(18 * 60, "1900-0200"))
        rows = v.compute_signals(make_df([(1, 2, 0.5, 1.5)] * 17, "2024-11-11 03:00"), **P)
        tags = {r["time"].hour: r["session"] for r in rows}
        self.assertEqual((tags[3], tags[8], tags[9], tags[11], tags[14], tags[17]),
                         ("LON", "LON", "OVERLAP", "NY", "NY PM", "-"))


class Legs(unittest.TestCase):
    def test_breakout_bar_silent_retrace_bar_signals(self):
        rows = v.compute_signals(scen(), **P)
        self.assertTrue(rows[11]["bos_bull"])
        self.assertFalse(rows[11]["long_signal"])
        self.assertFalse(rows[11]["long_in_zone"])
        self.assertTrue(rows[12]["long_signal"])
        self.assertEqual(rows[12]["long_score"], 6)
        self.assertEqual(rows[12]["long_cts"], 10)  # 20 by risk, capped
        self.assertAlmostEqual(rows[12]["long_zone"][1], 111 - 11 * 0.62)
        self.assertEqual([i for i, r in enumerate(rows) if r["long_signal"]], [12])

    def test_all_six_items_genuinely_met(self):
        r = v.compute_signals(scen(), **P)[12]
        self.assertEqual(r["long_items"], dict(htf=True, ote=True, vol=True, cvd=True, bar=True, fvg=True))
        self.assertEqual(r["long_score"], 6)
        self.assertFalse(any(v.compute_signals(scen(), **P)[12]["short_items"][k] for k in ("htf", "ote", "bar")))

    def test_score_threshold_uses_real_items(self):
        flat = v.compute_signals(make_df(SCENARIO), **P)[12]  # no volume spike: RVOL item missing
        self.assertFalse(flat["long_items"]["vol"])
        self.assertEqual((flat["long_score"], flat["long_signal"]), (5, True))
        self.assertFalse(v.compute_signals(make_df(SCENARIO), min_score=6, **P)[12]["long_signal"])
        self.assertFalse(v.compute_signals(scen(), min_score=7, **P)[12]["long_signal"])

    def test_rvol_item_boundary(self):
        # sma5 = (4000 + x) / 5 -> RVOL >= 1.3 needs x >= 1405.4
        for x, want in ((1400.0, False), (1410.0, True)):
            r = v.compute_signals(scen(vol=[1000.0] * 12 + [x]), **P)[12]
            self.assertEqual(r["long_items"]["vol"], want, x)

    def test_once_per_leg(self):
        bars = SCENARIO + [(104.5, 108, 104.0, 107)]
        rows = v.compute_signals(scen(bars), **P)
        self.assertTrue(rows[12]["long_signal"])
        self.assertFalse(rows[13]["long_signal"])

    def test_stale_break_no_activation(self):
        bars = list(SCENARIO)
        bars[9] = (101, 112, 101, 103)  # swing high 110 already exceeded when the anchor is confirmed
        rows = v.compute_signals(scen(bars), **P)
        self.assertFalse(any(r["bos_bull"] or r["long_signal"] for r in rows))

    def test_news_blackout_nfp(self):
        fri = scen(start="2024-11-01 03:00")
        self.assertFalse(any(r["long_signal"] for r in v.compute_signals(fri, **P)))
        self.assertTrue(v.compute_signals(fri, block_nfp=False, **P)[12]["long_signal"])

    def test_session_filter(self):
        off = dict(sess_asia=False, sess_london=False, sess_overlap=False, sess_ny=False, sess_ny_pm=False)
        self.assertFalse(any(r["long_signal"] for r in v.compute_signals(scen(), **off, **P)))
        self.assertTrue(v.compute_signals(scen(), use_session_filter=False, **off, **P)[12]["long_signal"])

    def test_sizing(self):
        p = v._params({})
        # zone 100..101 -> SL 99.95; close 103.52 -> 3.57 pts -> floor(200/7.14)=28 -> capped to 10
        cts, sl, tp = v.size_trade(1, 103.52, 101, 100, p)
        self.assertEqual(cts, 10)
        self.assertAlmostEqual(sl, 99.95)
        self.assertAlmostEqual(tp, 103.52 + 3.57 * 3)
        self.assertEqual(v.size_trade(1, 103.52, 101, 100, v._params(dict(max_contracts=100)))[0], 28)
        self.assertEqual(v.size_trade(1, 200, 101, 100, p)[0], 0)  # stop too wide for $200
        cts, sl, tp = v.size_trade(-1, 96.48, 101, 100, p)  # mirror
        self.assertAlmostEqual(sl, 101.05)
        self.assertAlmostEqual(tp, 96.48 - 4.57 * 3)


class Htf(unittest.TestCase):
    def test_uses_only_completed_htf_bars(self):
        n = 48
        close = np.arange(1, n + 1, dtype=float)
        bars = [(c, c + 0.5, c - 0.5, c) for c in close]
        df = make_df(bars, "2024-11-11 18:00")
        ef, es, hc = v.htf_series(df, 240, 2, 3)
        # 4h bars: [0..3],[4..7],...; bars 0-3 have no completed HTF bar
        self.assertTrue(np.isnan(hc[:4]).all())
        self.assertTrue((hc[4:8] == close[3]).all())  # close of previous HTF bar
        self.assertTrue((hc[8:12] == close[7]).all())
        changed = df.copy()
        changed.iloc[7, changed.columns.get_loc("close")] = 999.0  # last bar of the 2nd HTF bar
        _, _, hc2 = v.htf_series(changed, 240, 2, 3)
        self.assertTrue((hc2[4:8] == hc[4:8]).all())  # no lookahead inside the bar being formed
        self.assertTrue((hc2[8:12] == 999.0).all())
        self.assertTrue(np.isnan(ef[4:8]).all() and not np.isnan(ef[12]))  # EMA(2) needs 2 completed HTF bars


class Simulation(unittest.TestCase):
    def sig(self, side=1, qty=2, sl=95.0, tp=110.0):
        return dict(side=side, qty=qty, sl=sl, tp=tp, score=5, session="NY")

    def run_sim(self, bars, sigs, **kw):
        return v.simulate(make_df(bars), sigs + [None] * (len(bars) - len(sigs)), **kw)

    def test_entry_next_open_slippage_tp_and_commission(self):
        bars = [(100, 101, 99, 100), (100, 103, 99, 101), (101, 111, 100, 110)]
        t = self.run_sim(bars, [self.sig()]).iloc[0]
        self.assertEqual(t.entry, 100.25)
        self.assertEqual(t.exit, 110.0)
        self.assertEqual(t.exit_reason, "TP")
        self.assertAlmostEqual(t.gross_pnl, (110 - 100.25) * 2 * 2)
        self.assertAlmostEqual(t.net_pnl, 39.0 - 0.62 * 2 * 2)
        self.assertEqual(t.entry_time, make_df(bars).index[1])

    def test_short_slippage_and_stop_slippage(self):
        bars = [(100, 101, 99, 100), (100, 106, 99.5, 105)]
        t = self.run_sim(bars, [self.sig(-1, 1, 105.0, 90.0)]).iloc[0]
        self.assertEqual(t.entry, 99.75)
        self.assertEqual(t.exit, 105.25)  # stop fills 1 tick worse
        self.assertAlmostEqual(t.gross_pnl, (99.75 - 105.25) * 2)

    def test_path_rule_both_in_one_bar(self):
        # open closer to high -> high first -> TP
        t = self.run_sim([(100, 101, 99, 100), (100, 106, 90, 100)], [self.sig(sl=95, tp=105)]).iloc[0]
        self.assertEqual(t.exit_reason, "TP")
        # open closer to low -> low first -> SL
        t = self.run_sim([(100, 101, 99, 100), (100, 110, 94, 100)], [self.sig(sl=95, tp=105)]).iloc[0]
        self.assertEqual((t.exit_reason, t.exit), ("SL", 94.75))
        # short mirrors: high first hits the stop
        t = self.run_sim([(100, 101, 99, 100), (100, 106, 90, 100)], [self.sig(-1, 1, 105, 95)]).iloc[0]
        self.assertEqual(t.exit_reason, "SL")

    def test_one_position_at_a_time(self):
        bars = [(100, 101, 99, 100)] * 3 + [(100, 111, 99, 110)] + [(100, 101, 99, 100)] * 3
        t = self.run_sim(bars, [self.sig(), self.sig(), self.sig(), None, self.sig()])
        self.assertEqual(len(t), 2)  # signals on bars 1,2 ignored; bar 4 signal after the TP exit
        self.assertEqual(t.iloc[1].entry_time, make_df(bars).index[5])

    def test_open_at_end_and_last_bar_signal(self):
        bars = [(100, 101, 99, 100), (100, 101, 99, 100.5), (100, 101, 99, 100.75)]
        t = self.run_sim(bars, [self.sig()])
        self.assertEqual((t.iloc[0].exit_reason, t.iloc[0].exit, bool(t.iloc[0].open_at_end)), ("END", 100.75, True))
        self.assertEqual(len(self.run_sim(bars, [None, None, self.sig()])), 0)


class EndToEnd(unittest.TestCase):
    HIT_TP = [(107, 109, 106, 108), (110, 125, 109, 124)]  # entry bar 13, then a bar through the 121.3 target

    def test_run_backtest_scenario_and_summary(self):
        tr, s = v.run_backtest(scen(SCENARIO + self.HIT_TP), start="2024-01-01", **P)
        self.assertEqual(len(tr), 1)
        self.assertEqual((tr.iloc[0].qty, tr.iloc[0].exit_reason), (10, "TP"))
        self.assertEqual((s["trades"], s["open_trades"]), (1, 0))
        for k in ("win_rate", "profit_factor", "max_drawdown", "by_side", "by_session", "by_score", "trades_per_month"):
            self.assertIn(k, s)
        tr, s = v.run_backtest(scen(SCENARIO + self.HIT_TP), start="2030-01-01", **P)
        self.assertEqual((len(tr), s["trades"]), (0, 0))

    def test_open_trade_reported_separately(self):
        bars = SCENARIO + [(107, 109, 106, 108)] * 2
        tr, s = v.run_backtest(scen(bars), start="2024-01-01", **P)
        self.assertEqual((len(tr), s["trades"], s["open_trades"]), (0, 0, 1))
        end_row = v.simulate(scen(bars), [None] * 12 + [dict(side=1, qty=10, sl=102.2165, tp=121.3, score=6, session="NY")]
                             + [None] * 2).iloc[0]
        self.assertTrue(end_row.open_at_end)
        self.assertAlmostEqual(s["open_unrealized_pnl"], end_row.net_pnl)

    def test_end_is_inclusive_to_the_timestamp(self):
        bars = SCENARIO + self.HIT_TP  # signal bar 12 opens 2024-11-11 15:00 NY
        kw = dict(start="2024-01-01", **P)
        self.assertEqual(len(v.run_backtest(scen(bars), end="2024-11-11 15:00", **kw)[0]), 1)
        self.assertEqual(len(v.run_backtest(scen(bars), end="2024-11-11 14:59", **kw)[0]), 0)
        self.assertEqual(len(v.run_backtest(scen(bars), end="2024-11-11", **kw)[0]), 0)  # midnight, not the whole day

    def test_signals_before_htf_valid_are_excluded_and_counted(self):
        bars = SCENARIO + self.HIT_TP
        tr, s = v.run_backtest(scen(bars), start="2024-01-01", **{**P, "htf_ema_slow": 50})  # needs 50 completed bars
        self.assertEqual((len(tr), s["htf_excluded_signals"], s["htf_valid_from"]), (0, 1, None))
        self.assertEqual(s["htf_excluded_bars"], len(bars))
        tr, s = v.run_backtest(scen(bars), start="2024-01-01", **P)
        self.assertEqual((len(tr), s["htf_excluded_signals"], s["htf_excluded_bars"]), (1, 0, 3))
        self.assertEqual(s["htf_valid_from"], str(scen(bars).index[3]))  # 3 completed 60-min bars for EMA(3)

    def test_random_walk_smoke(self):
        rng = np.random.default_rng(1)
        n = 3000
        c = 20000 + np.cumsum(rng.normal(0, 15, n))
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + rng.uniform(0, 10, n)
        l = np.minimum(o, c) - rng.uniform(0, 10, n)
        df = make_df(list(zip(o, h, l, c)), "2024-11-01 00:00")
        df["volume"] = rng.uniform(500, 1500, n)
        tr, s = v.run_backtest(df, min_score=3, start="2024-10-23")
        self.assertEqual(len(tr), s["trades"])


def random_walk(n=3000, freq="15min", seed=1):
    rng = np.random.default_rng(seed)
    c = 20000 + np.cumsum(rng.normal(0, 15, n))
    o = np.r_[c[0], c[:-1]]
    df = make_df(list(zip(o, np.maximum(o, c) + rng.uniform(0, 10, n), np.minimum(o, c) - rng.uniform(0, 10, n), c)),
                 "2024-11-01 00:00", freq)
    df["volume"] = rng.uniform(500, 1500, n)
    return df


class Alignment(unittest.TestCase):
    def test_same_bar_long_and_short_long_wins(self):
        df = make_df([(100, 101, 99, 100)] * 2 + [(100, 111, 99, 110)] * 2)  # bar 2 hits the long's TP
        base = dict(time=None, session="NY", htf_valid=True, long_signal=True, short_signal=True, long_score=4, short_score=6,
                    long_cts=2, short_cts=3, long_sl=95.0, short_sl=105.0, long_tp=110.0, short_tp=90.0,
                    long_meta={"rvol": 1.0}, short_meta={"rvol": 2.0})
        rows = [dict(base, time=t) for t in df.index]
        for r in rows[1:]:
            r.update(long_signal=False, short_signal=False)
        with mock.patch.object(v, "compute_signals", return_value=rows):
            tr, _ = v.run_backtest(df, start="2024-01-01")
        self.assertEqual((len(tr), tr.iloc[0].side, tr.iloc[0].qty, tr.iloc[0].rvol), (1, "long", 2, 1.0))

    def test_chicago_day_for_nfp(self):
        # bar 12 = signal bar. NY Friday 00:30 is still Thursday in Chicago -> not blocked
        thu = make_df(SCENARIO, "2024-10-31 12:30")  # bar 12 = 2024-11-01 00:30 NY = Thu 23:30 Chicago
        self.assertTrue(v.compute_signals(thu, **P)[12]["long_signal"])
        sat = make_df(SCENARIO, "2024-11-01 12:30")  # bar 12 = Sat 00:30 NY = Fri 2024-11-01 23:30 Chicago -> NFP
        self.assertFalse(v.compute_signals(sat, **P)[12]["long_signal"])

    def test_dollars_per_point(self):
        self.assertEqual(v.DPP["MNQ"], 2.0)

    def test_zone_depth_long_and_short(self):
        long_row = v.compute_signals(make_df(SCENARIO), **P)[12]
        top, bot = 111 - 11 * 0.62, 111 - 11 * 0.79
        self.assertAlmostEqual(long_row["long_meta"]["zone_depth"], (top - 107) / (top - bot))  # tap above zone: < 0
        mirror = [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in SCENARIO]
        row = v.compute_signals(make_df(mirror), **P)[12]
        self.assertTrue(row["short_signal"])
        self.assertAlmostEqual(row["short_meta"]["zone_depth"], long_row["long_meta"]["zone_depth"])
        self.assertAlmostEqual(row["short_meta"]["leg_size"], 11)
        self.assertEqual(row["short_meta"]["bars_from_bos"], 1)

    def test_mfe_mae_and_trade_detail(self):
        bars = [(100, 101, 99, 100), (100, 103, 98, 101), (101, 104, 96, 100), (100, 111, 99, 110)]
        sig = dict(side=1, qty=2, sl=95.0, tp=110.0, score=5, session="NY")
        t = v.simulate(make_df(bars), [sig, None, None, None]).iloc[0]
        self.assertAlmostEqual(t.mfe_r, (110 - 100.25) / 5)  # high 111 on the exit bar is capped at the TP; risk = |100 - 95|
        self.assertAlmostEqual(t.mae_r, (100.25 - 96) / 5)
        self.assertEqual((t.bars_held, t.win, t.sl_dist, t.planned_risk, t.entry_slippage), (3, 1, 5.0, 20.0, 1.0))


class BuildingBlocks(unittest.TestCase):
    """Each rule is checked on bars that genuinely meet or fail it (nothing is forced)."""

    def test_fvg_requires_previous_close_above_gap_bottom(self):
        bars = list(SCENARIO)
        bars[10] = (103, 105, 102, 104)  # close[1] = 104 is not above high[2] = 104: bar 11 gaps but no FVG
        r = v.compute_signals(scen(bars), **P)[12]
        self.assertFalse(r["long_items"]["fvg"])
        self.assertEqual(r["long_score"], 5)
        self.assertTrue(v.compute_signals(scen(), **P)[12]["long_items"]["fvg"])  # control: close[1] = 104.5

    def test_fvg_recency_boundary_is_30_bars(self):
        bars = SCENARIO[:12] + [(108, 109, 104.5, 108)] * 40  # FVG on bar 11, then quiet bars (no new gap, above the zone)
        rows = v.compute_signals(scen(bars), **P)
        self.assertTrue(rows[11 + 30]["long_items"]["fvg"])
        self.assertFalse(rows[11 + 31]["long_items"]["fvg"])

    def test_cvd_delta_formula(self):
        d = v.cvd_delta(np.array([10.0, 10.0, 10.0, 5.0]), np.array([0.0, 0.0, 0.0, 5.0]),
                        np.array([8.0, 2.0, 10.0, 5.0]), np.array([100.0, 100.0, 50.0, 70.0]))
        self.assertEqual(list(d), [60.0, -60.0, 50.0, 0.0])  # v*(2c-l-h)/(h-l); zero range -> 0
        self.assertTrue(v.compute_signals(scen(), **P)[12]["long_items"]["cvd"])

    def test_htf_bias_needs_close_above_fast_ema(self):
        closes = np.array([100, 102, 104, 106, 108, 110, 108, 107.0])
        df = make_df([(c, c + .5, c - .5, c) for c in closes])
        ef, es, hc = v.htf_series(df, 60, 2, 3)
        self.assertTrue(ef[7] > es[7] and hc[7] < ef[7])  # fast above slow but last HTF close below the fast EMA
        rows = v.compute_signals(df, **P)
        self.assertFalse(rows[7]["long_items"]["htf"] or rows[7]["short_items"]["htf"])
        self.assertTrue(rows[6]["long_items"]["htf"] and not rows[6]["short_items"]["htf"])  # uptrend control
        down = make_df([(200 - c, 200 - c + .5, 200 - c - .5, 200 - c) for c in closes])
        rows = v.compute_signals(down, **P)
        self.assertTrue(rows[6]["short_items"]["htf"] and not rows[6]["long_items"]["htf"])
        self.assertFalse(rows[7]["short_items"]["htf"])

    def test_htf_warmup_from_longer_source(self):
        src = random_walk(600, "1h")
        late = src.iloc[300:]
        cold = v.htf_series(late, 240, 20, 50)
        warm = v.htf_series(late, 240, 20, 50, src)
        full = v.htf_series(src, 240, 20, 50)
        self.assertTrue(np.isnan(cold[1][:100]).all())
        for w, f in zip(warm, full):
            np.testing.assert_array_equal(w, f[300:])
        changed = src.copy()
        changed.iloc[-1, changed.columns.get_loc("close")] = 1.0  # forming last bar never leaks into earlier bars
        np.testing.assert_array_equal(v.htf_series(late, 240, 20, 50, changed)[2][:-4], warm[2][:-4])

    def test_new_extreme_bar_is_not_in_zone(self):
        bars = SCENARIO + [(105, 112, 104, 111)]  # dips into the zone but also makes a new high
        rows = v.compute_signals(scen(bars), **P)
        self.assertTrue(rows[13]["bos_bull"] is False and rows[13]["long_in_zone"] is False)

    def test_anchor_close_below_invalidates_the_leg(self):
        bars = SCENARIO[:12] + [(101, 102, 95, 96), (104.5, 108, 104, 107)]  # bar 12 closes under the 100 anchor
        rows = v.compute_signals(scen(bars), **P)
        self.assertFalse(rows[13]["long_in_zone"])
        self.assertFalse(any(r["long_signal"] for r in rows))

    def test_zone_needs_previous_bar_active(self):
        bars = list(SCENARIO[:11]) + [(104.5, 111, 101.8, 110.8)]  # activation bar touches the zone, closes above bot
        a = lambda k: np.array([b[k] for b in bars], float)
        leg = v.Leg(a(0), a(1), a(2), a(3), v._params(P))
        for i in range(11):
            leg.step(i)
        leg.prev_ext = 999.0  # not a new extreme vs the previous bar
        leg.step(11)
        self.assertTrue(leg.active)
        self.assertFalse(leg.in_zone)  # the zone was not active on the previous bar
        leg2 = v.Leg(a(0), a(1), a(2), a(3), v._params(P))
        for i in range(11):
            leg2.step(i)
        leg2.prev_ext, leg2.prev_active = 999.0, True  # control: same bar with an active previous bar
        leg2.step(11)
        self.assertTrue(leg2.in_zone)

    def test_same_bar_long_and_short_both_legs_used(self):
        rng = np.random.default_rng(389)  # fixed random walk where both legs fire on bar 37
        n = 120
        c = 100 + np.cumsum(rng.normal(0, 2, n)).round(1)
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + rng.uniform(0, 3, n).round(1)
        l = np.minimum(o, c) - rng.uniform(0, 3, n).round(1)
        rows = v.compute_signals(make_df(list(zip(o, h, l, c))), swing_left=3, swing_right=2, min_score=1,
                                 use_session_filter=False, use_news_filter=False, max_loss=20000.0)
        self.assertTrue(rows[37]["long_signal"] and rows[37]["short_signal"])
        # later bars sit in each leg's zone, sizing and filters pass, so only the "used" flag can block them
        self.assertTrue(rows[39]["short_in_zone"] and not rows[39]["short_signal"] and rows[39]["short_cts"] >= 1)
        self.assertTrue(rows[93]["long_in_zone"] and not rows[93]["long_signal"] and rows[93]["long_cts"] >= 1)


class Fills(unittest.TestCase):
    def sig(self, side=1, qty=1, sl=95.0, tp=110.0):
        return dict(side=side, qty=qty, sl=sl, tp=tp, score=5, session="NY")

    def run_sim(self, exit_bars, **kw):
        """Signal bar 0, entry bar 1 (long entry 100.25, short 99.75), then the bars under test."""
        bars = [(100, 101, 99, 100), (100, 100.5, 99.5, 100.2)] + exit_bars
        return v.simulate(make_df(bars), [self.sig(**kw)] + [None] * (len(bars) - 1)).iloc[0]

    def test_path_tie_goes_low_first(self):
        t = self.run_sim([(100, 105, 95, 100)], sl=95, tp=105)  # open equidistant from high and low
        self.assertEqual((t.exit_reason, t.exit), ("SL", 94.75))
        t = self.run_sim([(100, 105, 95, 100)], side=-1, sl=105, tp=95)
        self.assertEqual((t.exit_reason, t.exit), ("TP", 95.0))

    def test_gap_through_stop_fills_at_open_with_slippage(self):
        t = self.run_sim([(93, 94, 92, 93)])
        self.assertEqual((t.exit_reason, t.exit), ("SL", 92.75))
        self.assertAlmostEqual(t.mae_r, (100.25 - 92.75) / 5)
        t = self.run_sim([(107, 108, 106, 107)], side=-1, sl=105, tp=90)
        self.assertEqual((t.exit_reason, t.exit), ("SL", 107.25))

    def test_gap_beyond_target_fills_at_open_without_slippage(self):
        t = self.run_sim([(112, 113, 111, 112)])
        self.assertEqual((t.exit_reason, t.exit), ("TP", 112.0))
        t = self.run_sim([(88, 89, 87, 88)], side=-1, sl=105, tp=90)
        self.assertEqual((t.exit_reason, t.exit), ("TP", 88.0))
        self.assertAlmostEqual(t.mfe_r, (99.75 - 88) / 5)

    def test_sl_tp_rounded_to_tick(self):
        t = self.run_sim([(100, 120, 80, 100)], sl=95.12, tp=110.13)
        self.assertEqual((t.sl, t.tp), (95.0, 110.25))
        t = self.run_sim([(100, 111, 99.5, 110.5)], sl=95.12, tp=110.13)
        self.assertEqual((t.exit_reason, t.exit), ("TP", 110.25))
        self.assertAlmostEqual(t.gross_pnl, (110.25 - 100.25) * 2)

    def test_exit_bar_excursions_follow_the_path(self):
        # TP bar with high first: the later low is never visited, the high is capped at the target
        t = self.run_sim([(108, 112, 100, 111)])
        self.assertEqual(t.exit_reason, "TP")
        self.assertAlmostEqual(t.mfe_r, (110 - 100.25) / 5)
        self.assertAlmostEqual(t.mae_r, (100.25 - 99.5) / 5)
        # SL bar with high first: the high counts, the low is capped at the stop fill
        t = self.run_sim([(100, 101, 90, 92)])
        self.assertEqual((t.exit_reason, t.exit), ("SL", 94.75))
        self.assertAlmostEqual(t.mfe_r, (101 - 100.25) / 5)
        self.assertAlmostEqual(t.mae_r, (100.25 - 94.75) / 5)
        # SL bar with low first: the bar's high is never reached
        t = self.run_sim([(100, 106, 94, 100)])
        self.assertEqual(t.exit_reason, "SL")
        self.assertAlmostEqual(t.mfe_r, (100.5 - 100.25) / 5)


def yahoo_json(stamps):
    n = len(stamps)
    q = {k: [100.0 + i for i in range(n)] for k in ("open", "high", "low", "close")}
    q["volume"] = [10.0] * n
    return dict(chart=dict(result=[dict(timestamp=stamps, indicators=dict(quote=[q]))]))


def http_error(code, retry_after=None):
    hdr = email.message.Message()
    if retry_after:
        hdr["Retry-After"] = retry_after
    return urllib.error.HTTPError("http://x", code, "err", hdr, None)


def ok_response(stamps):
    return io.BytesIO(json.dumps(yahoo_json(stamps)).encode())


class Yahoo(unittest.TestCase):
    STAMPS = [1731369600, 1731373200, 1731376800 + 59, 1731380400 + 1800]  # xx:00:59 snapshot (dropped), :30 early-close bar (kept)

    def test_retries_with_backoff_and_retry_after(self):
        waits = []
        seq = [http_error(429), http_error(503, "7"), http_error(429), ok_response(self.STAMPS)]
        with mock.patch.object(v.urllib.request, "urlopen", side_effect=seq):
            df = v.fetch_yahoo("MNQ=F", "1h", "730d", sleep=waits.append)
        self.assertEqual(waits, [15, 7.0, 60])
        self.assertEqual(len(df), 3)
        self.assertEqual(df.attrs["snapshot_dropped"], 1)
        self.assertEqual(df.index[-1].minute, 30)

    def test_gives_up_with_one_line_error(self):
        waits = []
        with mock.patch.object(v.urllib.request, "urlopen", side_effect=[http_error(429)] * 5):
            with self.assertRaises(v.YahooUnavailable) as cm:
                v.fetch_yahoo("MNQ=F", "1h", "730d", sleep=waits.append)
        self.assertEqual(waits, [15, 30, 60, 120])
        self.assertIn("rate-limiting", str(cm.exception))
        self.assertNotIn("\n", str(cm.exception))
        with mock.patch.object(v, "run_multi", side_effect=v.YahooUnavailable("Yahoo is rate-limiting; retry later")), \
                mock.patch.object(sys, "argv", ["vof_ote.py", "--yahoo", "MNQ=F"]):
            with self.assertRaises(SystemExit) as cm:
                v.main()
        self.assertIn("rate-limiting", str(cm.exception.code))

    def test_other_http_errors_are_not_retried(self):
        with mock.patch.object(v.urllib.request, "urlopen", side_effect=[http_error(404)]) as m:
            with self.assertRaises(urllib.error.HTTPError):
                v.fetch_yahoo("MNQ=F", "1h", "730d", sleep=lambda s: self.fail("slept"))
        self.assertEqual(m.call_count, 1)

    def test_cache_reused_unless_refresh(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(v.urllib.request, "urlopen", side_effect=lambda *a, **k: ok_response(self.STAMPS)) as m:
                v.fetch_yahoo("MNQ=F", "1h", "730d", cache_dir=d)
                self.assertTrue(os.path.exists(os.path.join(d, "MNQ=F_1h_730d.json")))
                v.fetch_yahoo("MNQ=F", "1h", "730d", cache_dir=d)
                self.assertEqual(m.call_count, 1)
                v.fetch_yahoo("MNQ=F", "1h", "730d", cache_dir=d, refresh=True)
                self.assertEqual(m.call_count, 2)

    def test_run_multi_fetches_1h_once_and_uses_it_for_htf(self):
        calls, hs = [], []
        orig = v.run_and_write

        def fake_fetch(sym, tf, rng, **kw):
            calls.append((tf, rng, kw["cache_dir"].endswith("cache")))
            return random_walk(3000, "15min")

        def spy(df, tf, out, ms, st, en, htf_df=None):
            hs.append((tf, htf_df is not None))
            return orig(df, tf, out, ms, st, en, htf_df)

        with tempfile.TemporaryDirectory() as d, mock.patch.object(v, "fetch_yahoo", side_effect=fake_fetch), \
                mock.patch.object(v, "run_and_write", side_effect=spy):
            v.run_multi("MNQ=F", ["5m", "15m", "1h"], d, min_score=3)
        self.assertEqual(sorted(c[0] for c in calls), ["15m", "1h", "5m"])
        self.assertEqual(calls[0][:2], ("1h", "730d"))
        self.assertTrue(all(h for _, h in hs))


class Analysis(unittest.TestCase):
    def test_wilson(self):
        self.assertAlmostEqual(an.wilson_lb(9, 10), 0.596, places=3)
        self.assertAlmostEqual(an.wilson_lb(60, 100), 0.502, places=3)

    def test_ranking_excludes_small_and_orders_by_wilson(self):
        tr, _ = v.run_backtest(random_walk(6000), min_score=3, start="2024-10-23", timeframe="15m")
        res = an.analyze(tr)
        for key in ("top_win_lb", "bottom_win_lb", "top_avg_r"):
            self.assertTrue(res["rankings"][key])
            self.assertTrue(all(r["trades"] >= 10 for r in res["rankings"][key]))
        lb = [r["wilson_lb"] for r in res["rankings"]["top_win_lb"]]
        self.assertEqual(lb, sorted(lb, reverse=True))
        self.assertLessEqual(len(res["rankings"]["top_win_lb"]), 15)
        self.assertTrue(any(r["small_sample"] for rows in res["dimensions"].values() for r in rows))
        self.assertIn("small sample", an.report_md("t", {}, res, tr, 3))

    def test_report_text_and_item_zone_not_ranked(self):
        tr, summ = v.run_backtest(random_walk(6000), min_score=3, start="2024-10-23", timeframe="15m")
        res = an.analyze(tr)
        self.assertFalse(any(r["dimension"] == "item_zone" for rows in res["rankings"].values() for r in rows))
        md = an.report_md("t", summ, res, tr, 3)
        self.assertNotIn("(9/10", md)
        self.assertIn("9/10 wins gives about 0.60", md)
        self.assertIn("item_zone (always 1", md)
        self.assertIn("open_trades", md)

    def test_multi_timeframe_outputs(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(v, "fetch_yahoo", side_effect=lambda s, tf, r, **kw: random_walk(3000, "15min")):
            out = v.run_multi("MNQ=F", ["5m", "15m", "1h"], d, min_score=3)
            self.assertEqual(len(out), 3)
            for tf in ("5m", "15m", "1h"):
                for f in ("trades.csv", "summary.json", "analysis.json", "report.md"):
                    self.assertTrue(os.path.exists(os.path.join(d, tf, f)), (tf, f))
            with open(os.path.join(d, "comparison.md")) as f:
                self.assertIn("LOW CONFIDENCE", f.read())  # 25 trades < 30


class Csv(unittest.TestCase):
    def write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        f.write(text)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_tradingview_unix_time(self):
        # 1731369600 = 2024-11-12 00:00 UTC = 2024-11-11 19:00 New York
        df = v.load_csv(self.write("time,open,high,low,close,Volume,Volume MA\n"
                                   "1731369600,1,2,0.5,1.5,100,\n1731373200,1.5,2.5,1,2,200,\n"))
        self.assertEqual(str(df.index.tz), v.TZ)
        self.assertEqual(df.index[0].hour, 19)
        self.assertEqual(list(df.columns), ["open", "high", "low", "close", "volume"])
        self.assertEqual(df.volume.iloc[1], 200.0)

    def test_iso_offset_and_case(self):
        df = v.load_csv(self.write("Time,Open,High,Low,Close,Volume\n2024-11-11T19:00:00-05:00,1,2,0.5,1.5,100\n"))
        self.assertEqual((df.index[0].hour, df.index[0].day), (19, 11))


if __name__ == "__main__":
    unittest.main()
