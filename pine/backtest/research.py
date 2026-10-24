#!/usr/bin/env python3
"""Pre-registered strategy research on MNQ: VOF-OTE grid vs RSI(2) mean reversion vs intraday momentum.

Every strategy goes through vof_ote.simulate() (same fills/costs). TRAIN = first 60% of the tradable bars, TEST = the
rest; each window is simulated on its own slice of bars so TEST bars can never influence TRAIN results or selection
(indicators are causal and warm up on the full series). See README.md "Research".
"""
import argparse
import itertools
import json
import math
import os

import numpy as np
import pandas as pd

import analysis
import vof_ote as v

TRAIN_FRAC = 0.6
RISK_USD, MAX_CTS = 200.0, 10
TF_MIN = {"5m": 5, "15m": 15, "1h": 60}
MIN_TEST_TRADES = {"1h": 30, "5m": 15, "15m": 15}
SEL_MIN_PF, SEL_MIN_TRADES, PASS_MIN_PF = 1.2, 20, 1.2
VOF_GRID = [dict(rr=rr, min_score=ms, require_fvg_in_ote=fv, sess_asia=asia)
            for rr, ms, fv, asia in itertools.product((1.5, 2.0, 3.0), (3, 4), (True, False), (True, False))]


# ---------------------------------------------------------------- indicators
def rma(x, n):
    """Pine ta.rma: SMA seed over the first n valid values, then alpha = 1/n. NaN before."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    ok = np.flatnonzero(~np.isnan(x))
    if len(ok) < n:
        return out
    s = ok[0] + n - 1
    out[s] = x[ok[0]:s + 1].mean()
    for i in range(s + 1, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def rsi(c, n=2):
    """Pine ta.rsi (Wilder)."""
    d = np.diff(c, prepend=np.nan)
    up, dn = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
    up[0] = dn[0] = np.nan
    up, dn = rma(up, n), rma(dn, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    return np.where(np.isnan(up) | np.isnan(dn), np.nan, out)


def atr(h, l, c, n=14):
    tr = h - l
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])])
    return rma(tr, n)


def contracts(dist_pts):
    """Risk-based size: floor($200 / (stop pts x $2)) capped at 10; 0 means skip."""
    return min(math.floor(RISK_USD / (dist_pts * v.DPP["MNQ"])), MAX_CTS) if dist_pts > 0 else 0


def nfp_blocked(idx):
    c = idx.tz_convert(v.EXCHANGE_TZ)
    return np.asarray((c.dayofweek == 4) & (c.day <= 7))


def session_tags(idx):
    mod = idx.hour * 60 + idx.minute
    out = []
    for m in mod:
        out.append(next((s[1] for s in v.SESSIONS if v.in_session_window(m, s[2])), None))
    return out


# ---------------------------------------------------------------- strategy 2: RSI(2)
def rsi2_signals(df, a, b):
    """Signals for local bars 0..b-a-1 (df bars a..b-1). Indicators use the whole df (causal warm-up)."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    r, s200, s5, at = rsi(c, 2), v.sma(c, 200), v.sma(c, 5), atr(h, l, c, 14)
    tags, nfp = session_tags(df.index), nfp_blocked(df.index)
    sigs = [None] * (b - a)
    for i in range(a, b - 1):
        if np.isnan(r[i]) or np.isnan(s200[i]) or np.isnan(at[i]) or tags[i] is None or nfp[i]:
            continue
        side = 1 if (c[i] > s200[i] and r[i] < 10) else -1 if (c[i] < s200[i] and r[i] > 90) else 0
        if not side:
            continue
        dist = 2.5 * at[i]
        qty = contracts(dist)
        if qty < 1:
            continue
        e = i + 1

        def rule(jl, side=side, e=e):
            j = jl + a
            if (c[j] > s5[j]) if side > 0 else (c[j] < s5[j]):
                return "open", "SMA5"
            return ("open", "TIME") if j - e + 1 >= 10 else None
        sigs[i - a] = dict(side=side, qty=qty, sl=c[i] - side * dist, tp=None, score=0, session=tags[i], rule=rule)
    return sigs


# ---------------------------------------------------------------- strategy 3: intraday momentum
def momentum_days(df, tf):
    """List of (signal_pos, side, exit_pos) per tradable day. Entry bar = signal_pos + 1."""
    tfm = TF_MIN[tf]
    entry_min = 960 - (30 if tfm < 60 else 60)
    exit_min = 960 - tfm  # open of the bar whose close is 16:00
    nfp = nfp_blocked(df.index)
    mod = df.index.hour * 60 + df.index.minute
    dates = df.index.normalize().tz_localize(None)
    pos = {}
    for i, (d, m) in enumerate(zip(dates, mod)):
        pos[(d, m)] = i
    o, c = df["open"].to_numpy(float), df["close"].to_numpy(float)
    out, prev_close = [], None
    for d in sorted(set(dates)):
        ex, en, ten = pos.get((d, exit_min)), pos.get((d, entry_min)), pos.get((d, 600))
        ok = ex is not None and en is not None and ten is not None and en >= 1
        ok = ok and ex - en == (exit_min - entry_min) // tfm and df.index[en - 1] == df.index[en] - pd.Timedelta(minutes=tfm)
        if ok and prev_close is not None and not nfp[en]:
            ret = o[ten] - prev_close
            if ret != 0:
                out.append((en - 1, 1 if ret > 0 else -1, ex))
        if ex is not None:
            prev_close = c[ex]
    return out


def momentum_signals(df, a, b, tf):
    h, l, c, o = (df[k].to_numpy(float) for k in ("high", "low", "close", "open"))
    at = atr(h, l, c, 14)
    sigs = [None] * (b - a)
    for sp, side, ex in momentum_days(df, tf):
        if sp < a or ex >= b or np.isnan(at[sp]):
            continue
        qty = contracts(at[sp])
        if qty < 1:
            continue
        sigs[sp - a] = dict(side=side, qty=qty, sl=o[sp + 1] - side * at[sp], tp=None, score=0, session="MOM",
                            rule=lambda jl, ex=ex: ("close", "EOD") if jl + a == ex else None)
    return sigs


# ---------------------------------------------------------------- metrics, windows
def metrics(tr, first, last):
    s = v.summarize(tr, first, last)
    for k in ("by_side", "by_session", "by_score"):
        s.pop(k)
    s["wilson_lb"] = analysis.wilson_lb(s["wins"], s["trades"])
    s["breakeven_wr"] = -s["avg_loss"] / (s["avg_win"] - s["avg_loss"]) if s["trades"] and s["wins"] and s["avg_loss"] else None
    return s


def windows(df, start):
    """(first tradable pos, split pos, n). TRAIN = [first, split), TEST = [split, n)."""
    first = int(df.index.searchsorted(pd.Timestamp(start, tz=v.TZ))) if start else 0
    return first, first + int((len(df) - first) * TRAIN_FRAC), len(df)


def run_window(df, a, b, tf, build):
    tr = v.simulate(df.iloc[a:b], build(a, b), timeframe=tf)
    tr = tr[~tr.open_at_end.astype(bool)].reset_index(drop=True)
    return tr, metrics(tr, df.index[a], df.index[b - 1])


def vof_window(df, htf_df, rows, a, b, tf, params):
    tr, _ = v.run_backtest(df.iloc[a:b], htf_df, rows=rows[a:b], start=None, timeframe=tf, **params)
    return tr, metrics(tr, df.index[a], df.index[b - 1])


def choose_variant(train_stats):
    """Pre-registered rule, uses TRAIN stats only: PF >= 1.2 and trades >= 20, then highest avg R (ties: first)."""
    ok = [(i, s) for i, s in enumerate(train_stats)
          if s["trades"] >= SEL_MIN_TRADES and s["profit_factor"] is not None and s["profit_factor"] >= SEL_MIN_PF]
    return max(ok, key=lambda t: (t[1]["avg_r"], -t[0]))[0] if ok else None


def run_vof(df, htf_df, tf, start, grid=VOF_GRID):
    a0, sp, n = windows(df, start)
    runs = []
    for g in grid:
        rows = v.compute_signals(df, htf_df, **g)
        tr_tr, st_tr = vof_window(df, htf_df, rows, a0, sp, tf, g)
        runs.append((g, rows, st_tr, tr_tr))
    ci = choose_variant([r[2] for r in runs])  # TEST is not touched before this line
    variants = []
    for k, (g, rows, st_tr, _) in enumerate(runs):
        tr_te, st_te = vof_window(df, htf_df, rows, sp, n, tf, g)
        tr_fu, st_fu = vof_window(df, htf_df, rows, a0, n, tf, g)
        variants.append(dict(params=g, train=st_tr, test=st_te, full=st_fu, chosen=k == ci, test_trades_df=tr_te))
    return ci, variants


def run_simple(df, tf, start, build):
    a0, sp, n = windows(df, start)
    (_, tr_s), (te, te_s), (_, fu_s) = (run_window(df, a, b, tf, build) for a, b in ((a0, sp), (sp, n), (a0, n)))
    return dict(train=tr_s, test=te_s, full=fu_s, test_trades_df=te)


def verdict(tf, r):
    """Pre-registered pass rule. Returns (passed, reasons)."""
    tr, te, why = r["train"], r["test"], []
    if tr["net_pnl"] <= 0:
        why.append(f"TRAIN not profitable (net {tr['net_pnl']:.0f})")
    if te["net_pnl"] <= 0:
        why.append(f"TEST not profitable (net {te['net_pnl']:.0f})")
    pf = te["profit_factor"]
    if te["trades"] and pf is None and te["net_pnl"] > 0:
        pf = math.inf
    if pf is None or pf < PASS_MIN_PF:
        why.append(f"TEST PF {'n/a' if pf is None else f'{pf:.2f}'} < {PASS_MIN_PF}")
    if te["trades"] < MIN_TEST_TRADES[tf]:
        why.append(f"TEST trades {te['trades']} < {MIN_TEST_TRADES[tf]}")
    be = te["breakeven_wr"] if te["breakeven_wr"] is not None else (0.0 if te["trades"] and te["losses"] == 0 else None)
    if be is None or te["wilson_lb"] < be:
        why.append(f"TEST Wilson LB {100 * te['wilson_lb']:.1f}% < breakeven WR {'n/a' if be is None else f'{100 * be:.1f}%'}")
    return not why, why


# ---------------------------------------------------------------- orchestration / output
def run_all(frames, htf_df, starts):
    """frames: {tf: df}. Returns {tf: {strategy: result}}."""
    res = {}
    for tf, df in frames.items():
        st = starts[tf]
        ci, variants = run_vof(df, htf_df, tf, st)
        res[tf] = {
            "VOF-OTE": dict(variants[ci] if ci is not None else {}, chosen_index=ci, variants=variants),
            "RSI2": run_simple(df, tf, st, lambda a, b, df=df: rsi2_signals(df, a, b)),
            "MOMENTUM": run_simple(df, tf, st, lambda a, b, df=df, tf=tf: momentum_signals(df, a, b, tf))}
        a0, sp, n = windows(df, st)
        res[tf]["split"] = dict(tradable_from=str(df.index[a0]), test_from=str(df.index[sp]), end=str(df.index[-1]),
                                train_bars=sp - a0, test_bars=n - sp)
        for name in ("VOF-OTE", "RSI2", "MOMENTUM"):
            r = res[tf][name]
            r["pass"], r["reasons"] = ((False, ["no variant met the TRAIN selection rule (PF >= 1.2, trades >= 20)"])
                                       if not r.get("test") else verdict(tf, r))
    return res


def _f(x, fmt):
    return "-" if x is None else format(x, fmt)


def row(label, tf, s, low=False):
    return (f"| {label} | {tf} | {s['trades']} | {s['trades_per_month']:.1f} | {100 * s['win_rate']:.1f} | "
            f"{100 * s['wilson_lb']:.1f} | {'-' if s['breakeven_wr'] is None else format(100 * s['breakeven_wr'], '.1f')} | "
            f"{_f(s['profit_factor'], '.2f')} | {s['avg_r']:.2f} | {s['expectancy']:.1f} | {s['net_pnl']:.0f} | "
            f"{s['max_drawdown']:.0f} | {s['longest_losing_streak']} |{' LOW CONFIDENCE' if low else ''} |")


HEAD = ("| Strategy | TF | Trades | /month | Win % | Wilson LB % | Breakeven WR % | PF | Avg R | Exp $/trade | Net $ | Max DD $ "
        "| Max losing streak | Flag |\n|" + "---|" * 14)
METHOD = """## Method (pre-registered; written before results)

* Instrument MNQ ($2/pt), costs and fills exactly as `vof_ote.simulate()`: next-bar-open entry +1 tick, $0.62/contract/side,
  stops 1 tick worse, 0.25 tick rounding, TradingView intrabar path rule, gap rules, one position at a time per strategy.
  Rule exits (RSI2 SMA5 / time stop at the next open, momentum 16:00 close) also take 1 tick of slippage.
* Sizing: floor($200 / (stop points x $2)), capped at 10, trade skipped if < 1 contract.
* Split per timeframe: TRAIN = first 60% of tradable bars (1h from 2024-10-23, 5m/15m from the data start), TEST = last 40%.
  Each window is simulated on its own bar slice (no trade crosses the boundary; trades still open at a window end are
  dropped). Indicators are causal and warm up on earlier data.
* VOF-OTE: 24 variants (rr 1.5/2/3 x min_score 3/4 x require_fvg_in_ote x sess_asia). Selection uses TRAIN only: PF >= 1.2
  and trades >= 20, then the highest TRAIN avg R. Only the chosen variant's TEST enters the main table.
* RSI(2) (Connors, canonical, untuned): Wilder RSI(2), SMA200 trend filter; long RSI2 < 10 and close > SMA200, short
  RSI2 > 90 and close < SMA200; exit at the next open after close crosses SMA5; stop 2.5 x ATR(14) from the signal close;
  time stop at the next open after 10 bars held; all five sessions + NFP blackout as in VOF-OTE.
* Intraday momentum (Gao-Han-Li-Zhou 2018): sign of (10:00 ET price - previous 16:00 ET close); trade that direction from
  15:30 (5m/15m) or 15:00 (1h, approximation: last hour instead of last half-hour) to the 16:00 close; stop 1.0 x ATR(14)
  from the entry-bar open; skip NFP days and days without the needed bars (holidays, early closes). Untuned.
* PASS = profitable in TRAIN and TEST, TEST PF >= 1.2, TEST trades >= 30 (1h) or >= 15 (5m/15m), TEST Wilson LB >= the
  strategy's breakeven win rate (|avg loss| / (avg win + |avg loss|)). Passes are ranked by TEST win rate, then trades/month.
  TEST results with < 30 trades are marked LOW CONFIDENCE.
"""


def write_outputs(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    names = ("VOF-OTE", "RSI2", "MOMENTUM")
    L = ["# Strategy research", "", METHOD, "## Split dates", ""]
    for tf, r in res.items():
        L.append(f"* {tf}: {json.dumps(r['split'])}")
    L += ["", "## Main table: TEST period", "", HEAD]
    for tf in res:
        for nm in names:
            r = res[tf][nm]
            lab = nm if nm != "VOF-OTE" or r["chosen_index"] is None else f"VOF-OTE #{r['chosen_index']}"
            L.append(row(lab, tf, r["test"], r["test"]["trades"] < 30) if r.get("test") else f"| {nm} | {tf} | no variant chosen |" + " |" * 11)
    L += ["", "## TRAIN and FULL", "", HEAD]
    for tf in res:
        for nm in names:
            r = res[tf][nm]
            for w in ("train", "full"):
                if r.get(w):
                    L.append(row(f"{nm} {w.upper()}", tf, r[w]))
    L += ["", "## Verdict", ""]
    passes = []
    for tf in res:
        for nm in names:
            r = res[tf][nm]
            L.append(f"* {nm} {tf}: {'PASS' if r['pass'] else 'FAIL - ' + '; '.join(r['reasons'])}")
            if r["pass"]:
                passes.append((-r["test"]["win_rate"], -r["test"]["trades_per_month"], nm, tf))
    L.append("")
    if passes:
        L.append("Ranking of PASSES (TEST win rate, then trades/month):")
        for k, (w, m, nm, tf) in enumerate(sorted(passes), 1):
            L.append(f"{k}. {nm} {tf}: win rate {-100 * w:.1f}%, {-m:.1f} trades/month")
    else:
        L.append("Nothing passes. No strategy met the pre-registered rule, so none is supported by this data.")
    L += ["", "## Appendix: all 24 VOF-OTE variants (for transparency - not used for selection)", "",
          "| TF | # | rr | min_score | fvg_in_ote | asia | chosen | TRAIN trades | TRAIN PF | TRAIN avg R | TEST trades | TEST win % | TEST PF | TEST avg R | TEST net $ |",
          "|" + "---|" * 15]
    for tf in res:
        for k, x in enumerate(res[tf]["VOF-OTE"]["variants"]):
            g, a, b = x["params"], x["train"], x["test"]
            L.append(f"| {tf} | {k} | {g['rr']} | {g['min_score']} | {g['require_fvg_in_ote']} | {g['sess_asia']} | "
                     f"{'yes' if x['chosen'] else ''} | {a['trades']} | {_f(a['profit_factor'], '.2f')} | {a['avg_r']:.2f} | "
                     f"{b['trades']} | {100 * b['win_rate']:.1f} | {_f(b['profit_factor'], '.2f')} | {b['avg_r']:.2f} | {b['net_pnl']:.0f} |")
    with open(os.path.join(out_dir, "research.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    strip = lambda d: {k: (strip(x) if isinstance(x, dict) else [strip(i) if isinstance(i, dict) else i for i in x]
                           if isinstance(x, list) else x) for k, x in d.items() if k != "test_trades_df"}
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(strip(res), f, indent=2, default=str)
    for tf in res:
        for nm in names:
            r = res[tf][nm]
            if r.get("test_trades_df") is not None:
                r["test_trades_df"].to_csv(os.path.join(out_dir, f"trades_test_{nm}_{tf}.csv"), index=False)


def main():
    ap = argparse.ArgumentParser(description="Pre-registered MNQ strategy research (cached Yahoo data only)")
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--symbol", default="MNQ=F")
    ap.add_argument("--timeframes", default="1h,5m,15m")
    a = ap.parse_args()
    tfs = a.timeframes.split(",")
    for tf in set(tfs) | {"1h"}:
        p = os.path.join(a.cache_dir, f"{a.symbol}_{tf}_{v.YAHOO_RANGES[tf]}.json")
        if not os.path.exists(p):
            raise SystemExit(f"missing cache file {p} (this tool never downloads)")
    load = lambda tf: v.fetch_yahoo(a.symbol, tf, v.YAHOO_RANGES[tf], cache_dir=a.cache_dir)
    h1 = load("1h")
    frames = {tf: h1 if tf == "1h" else load(tf) for tf in tfs}
    res = run_all(frames, h1, {"1h": v.DEFAULTS["start"], "5m": None, "15m": None})
    write_outputs(res, a.out_dir)
    print(open(os.path.join(a.out_dir, "research.md")).read())


if __name__ == "__main__":
    main()
