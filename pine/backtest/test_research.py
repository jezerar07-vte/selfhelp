import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import research as r  # noqa: E402
import vof_ote as v  # noqa: E402


def ohlc(closes, half=0.1, start="2024-11-11 03:00", freq="1min"):
    c = np.asarray(closes, float)
    o = np.concatenate(([c[0]], c[:-1]))
    idx = pd.date_range(start, periods=len(c), freq=freq, tz=v.TZ)
    return pd.DataFrame(dict(open=o, high=np.maximum(o, c) + half, low=np.minimum(o, c) - half, close=c, volume=1000.0), index=idx)


def dip_series():
    """250 slowly rising bars (close > SMA200), then two sharp down bars -> RSI2 < 10, then a flat tail."""
    up = 100 + 0.5 * np.arange(250)
    return np.concatenate((up, [up[-1] - 3, up[-1] - 6], np.full(30, up[-1] - 6)))


def run_rsi(df):
    sigs = r.rsi2_signals(df, 0, len(df))
    tr = v.simulate(df, sigs)
    return sigs, tr[~tr.open_at_end.astype(bool)]


class TestIndicators(unittest.TestCase):
    def test_rsi_wilder_hand_computed(self):
        # changes +1 -1 +2 -1; seed (SMA of first 2): au=.5 ad=.5 -> 50; then au=1.25 ad=.25 -> 100-100/6; then .625/.625 -> 50
        out = r.rsi([10, 11, 10, 12, 11], 2)
        self.assertTrue(np.isnan(out[:2]).all())
        np.testing.assert_allclose(out[2:], [50, 100 - 100 / 6, 50])

    def test_atr_wilder(self):
        h, l, c = np.array([2., 3, 4]), np.array([1., 1, 2]), np.array([1.5, 2, 3])
        # tr = 1, 2 (h-l), 2 (max(2, |4-2|, |2-2|)); rma(2): seed (1+2)/2 = 1.5, then (1.5+2)/2
        np.testing.assert_allclose(r.atr(h, l, c, 2)[1:], [1.5, 1.75])

    def test_sizing(self):
        self.assertEqual(r.contracts(50), 2)
        self.assertEqual(r.contracts(100.1), 0)  # skip: < 1 contract
        self.assertEqual(r.contracts(1), 10)  # capped


class TestRsi2(unittest.TestCase):
    def test_signal_and_sma5_exit_next_open(self):
        c = np.concatenate((dip_series()[:252], [dip_series()[251] + 1, dip_series()[251] + 6, 300, 300, 300]))
        df = ohlc(c)
        _, tr = run_rsi(df)
        t = tr.iloc[0]
        rs = r.rsi(c, 2)
        i = next(k for k in range(200, len(c)) if rs[k] < 10)
        self.assertEqual(i, 251)  # RSI2 < 10 after the second down bar
        e = i + 1
        s5 = pd.Series(c).rolling(5).mean().to_numpy()
        j = next(k for k in range(e, len(c)) if c[k] > s5[k])
        self.assertEqual(t.entry_time, df.index[e])
        self.assertEqual(t.exit_reason, "SMA5")
        self.assertEqual(t.exit_time, df.index[j + 1])
        self.assertEqual(t.exit, df.open.iloc[j + 1] - 0.25)  # market exit at the next open, 1 tick slipped
        self.assertEqual(t.side, "long")

    def test_time_stop_after_10_bars(self):
        df = ohlc(dip_series())
        _, tr = run_rsi(df)
        t = tr.iloc[0]
        e = 252
        self.assertEqual(t.entry_time, df.index[e])
        self.assertEqual((t.exit_reason, t.exit_time), ("TIME", df.index[e + 10]))

    def test_protective_stop(self):
        c = dip_series()[:252].copy()
        df = ohlc(np.concatenate((c, [c[-1], c[-1]])))
        df.iloc[253, df.columns.get_loc("low")] -= 50  # crash through the stop on the bar after entry
        sigs, tr = run_rsi(df)
        t = tr.iloc[0]
        self.assertEqual(t.exit_reason, "SL")
        self.assertEqual(t.exit_time, df.index[253])
        self.assertEqual(t.exit, t.sl - 0.25)
        self.assertAlmostEqual(sigs[251]["sl"], df.close.iloc[251] - 2.5 * r.atr(*(df[k].to_numpy() for k in ("high", "low", "close")))[251])

    def test_skip_when_stop_too_wide(self):
        df = ohlc(dip_series(), half=100.0)  # ATR ~ 200 pts -> stop 500 pts -> 0 contracts
        sigs, tr = run_rsi(df)
        self.assertTrue(all(s is None for s in sigs))
        self.assertEqual(len(tr), 0)

    def test_session_gap_blocks(self):
        df = ohlc(dip_series(), start="2024-11-11 12:50")  # signal bars land in the 17:00-19:00 gap
        sigs = r.rsi2_signals(df, 0, len(df))
        self.assertEqual(df.index[251].strftime("%H:%M"), "17:01")
        self.assertTrue(all(x is None for x in sigs))


def mom_df(tf, day1, day2, p10=102.0, early_close=False):
    """Two days of flat bars (range 1 pt) from 03:00 to the last bar before 16:00; day2 trades p10 from 10:00 and its
    last bar closes 2 pts further in the trade direction."""
    step = {"5m": "5min", "1h": "60min"}[tf]
    parts = []
    for d, price in ((day1, 100.0), (day2, None)):
        end = f"{d} 13:00" if early_close and d == day2 else f"{d} 16:00"
        idx = pd.date_range(f"{d} 03:00", end, freq=step, tz=v.TZ, inclusive="left")
        c = np.full(len(idx), 100.0) if price else np.where(idx.hour * 60 + idx.minute >= 600, p10, 100.0)
        if price is None and not early_close:
            c[-1] = p10 + 2 * np.sign(p10 - 100)
        o = c.copy()
        if price is None and not early_close:
            o[-1] = p10  # the last bar moves from p10 to p10 +/- 2
        parts.append(pd.DataFrame(dict(open=o, high=np.maximum(o, c) + .5, low=np.minimum(o, c) - .5, close=c, volume=1000.0), index=idx))
    return pd.concat(parts)


class TestMomentum(unittest.TestCase):
    def check(self, tf, entry, exit_, p10, side):
        df = mom_df(tf, "2024-11-12", "2024-11-13", p10)
        days = r.momentum_days(df, tf)
        self.assertEqual(len(days), 1)
        sp, sd, ex = days[0]
        self.assertEqual((df.index[sp + 1].strftime("%H:%M"), df.index[ex].strftime("%H:%M"), sd), (entry, exit_, side))
        sigs = r.momentum_signals(df, 0, len(df), tf)
        tr = v.simulate(df, sigs)
        tr = tr[~tr.open_at_end.astype(bool)]
        t = tr.iloc[0]
        self.assertEqual((len(tr), t.exit_reason, t.exit_time.strftime("%H:%M")), (1, "EOD", exit_))
        self.assertEqual(t.entry_time.strftime("%H:%M"), entry)
        self.assertEqual(t.exit, df.close.iloc[ex] - side * 0.25)
        self.assertGreater(t.net_pnl, 0)
        self.assertAlmostEqual(t.sl, df.open.iloc[sp + 1] - side * 1.0, places=1)  # 1 x ATR (=1) from the entry-bar open

    def test_5m_long(self):
        self.check("5m", "15:30", "15:55", 102.0, 1)

    def test_5m_short(self):
        self.check("5m", "15:30", "15:55", 98.0, -1)

    def test_1h_long_and_short(self):
        self.check("1h", "15:00", "15:00", 102.0, 1)
        self.check("1h", "15:00", "15:00", 98.0, -1)

    def test_early_close_or_holiday_skipped(self):
        for tf in ("5m", "1h"):
            self.assertEqual(r.momentum_days(mom_df(tf, "2024-11-12", "2024-11-13", early_close=True), tf), [])

    def test_nfp_day_skipped(self):
        # 2024-11-01 is the first Friday (NFP); the identical setup on a non-NFP Friday trades
        self.assertEqual(r.momentum_days(mom_df("5m", "2024-10-31", "2024-11-01"), "5m"), [])
        self.assertEqual(len(r.momentum_days(mom_df("5m", "2024-11-14", "2024-11-15"), "5m")), 1)


class TestNoLeak(unittest.TestCase):
    @staticmethod
    def walk(seed, n, p0=100.0):
        g = np.random.default_rng(seed)
        c = p0 + np.cumsum(g.normal(0, 3, n))
        o = np.concatenate(([p0], c[:-1]))
        idx = pd.date_range("2024-11-11 03:00", periods=n, freq="1h", tz=v.TZ)
        return pd.DataFrame(dict(open=o, high=np.maximum(o, c) + abs(g.normal(0, 1.5, n)),
                                 low=np.minimum(o, c) - abs(g.normal(0, 1.5, n)), close=c, volume=g.uniform(500, 2000, n)), index=idx)

    def test_selection_and_train_ignore_test_bars(self):
        n = 1500
        a = self.walk(1, n)
        _, sp, _ = r.windows(a, None)
        b = a.copy()
        b.iloc[sp:] = self.walk(2, n - sp, a.close.iloc[sp - 1]).to_numpy()  # different TEST bars
        grid = [dict(rr=1.5, min_score=3), dict(rr=2.0, min_score=3, require_fvg_in_ote=False)]
        ca, va = r.run_vof(a, None, "1h", None, grid)
        cb, vb = r.run_vof(b, None, "1h", None, grid)
        self.assertEqual(ca, cb)
        self.assertTrue(any(x["train"]["trades"] > 0 for x in va))
        self.assertEqual([x["train"] for x in va], [x["train"] for x in vb])
        for build in (lambda d: (lambda x, y: r.rsi2_signals(d, x, y)), lambda d: (lambda x, y: r.momentum_signals(d, x, y, "1h"))):
            ra, rb = (r.run_simple(d, "1h", None, build(d)) for d in (a, b))
            self.assertEqual(ra["train"], rb["train"])

    def test_choose_variant_rule(self):
        s = lambda n, pf, ar: dict(trades=n, profit_factor=pf, avg_r=ar)
        self.assertEqual(r.choose_variant([s(30, 1.5, .2), s(19, 3, 1), s(40, 1.19, 2), s(25, 1.3, .3), s(25, None, 9)]), 3)
        self.assertIsNone(r.choose_variant([s(19, 3, 1), s(30, 1.0, 1)]))


class TestVerdict(unittest.TestCase):
    def st(self, **k):
        d = dict(trades=40, net_pnl=100.0, profit_factor=1.5, wilson_lb=.5, breakeven_wr=.4, losses=10)
        return dict(d, **k)

    def test_pass_and_fails(self):
        ok = dict(train=self.st(), test=self.st())
        self.assertTrue(r.verdict("1h", ok)[0])
        self.assertFalse(r.verdict("1h", dict(ok, test=self.st(trades=29)))[0])
        self.assertTrue(r.verdict("5m", dict(ok, test=self.st(trades=15)))[0])
        self.assertFalse(r.verdict("1h", dict(ok, test=self.st(wilson_lb=.39)))[0])
        self.assertFalse(r.verdict("1h", dict(ok, train=self.st(net_pnl=-1)))[0])
        self.assertFalse(r.verdict("1h", dict(ok, test=self.st(profit_factor=1.19)))[0])


if __name__ == "__main__":
    unittest.main()
