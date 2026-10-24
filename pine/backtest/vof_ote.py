#!/usr/bin/env python3
"""Python port of pine/vof-ote.pine (VOF-OTE v2.1) plus a TradingView-style trade simulator.

Bar-by-bar loops, clarity over speed. See README.md for approximations vs TradingView.
The short side is computed by running the long-side engine on negated prices
(open'=-open, high'=-low, low'=-high, close'=-close), which is an exact mirror of the Pine rules.
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

import numpy as np
import pandas as pd

import analysis

TZ = "America/New_York"
EXCHANGE_TZ = "America/Chicago"  # CME exchange tz: Pine dayofweek/dayofmonth use it; sessions stay on TZ
DPP = {"ES": 50.0, "NQ": 20.0, "MES": 5.0, "MNQ": 2.0}
# (param key, tag, Pine session string) in the Pine priority order used for sess_tag
SESSIONS = [
    ("sess_asia", "ASIA", "1900-0200"),
    ("sess_london", "LON", "0300-0830"),
    ("sess_overlap", "OVERLAP", "0800-1100"),
    ("sess_ny", "NY", "1100-1330"),
    ("sess_ny_pm", "NY PM", "1330-1700"),
]
DEFAULTS = dict(
    instrument="MNQ", max_loss=200.0, rr=3.0, max_contracts=10,
    swing_left=8, swing_right=2, fib_low=0.62, fib_mid=0.705, fib_high=0.79,  # fib_mid is display-only in Pine
    vol_ma_len=20, rvol_min=1.3, cvd_len=14,
    require_fvg_in_ote=True, fvg_lookback=30,
    htf_minutes=240, htf_ema_fast=20, htf_ema_slow=50,
    min_score=4,
    use_session_filter=True, sess_asia=True, sess_london=True, sess_overlap=True, sess_ny=True, sess_ny_pm=True,
    use_news_filter=True, block_nfp=True, block_fomc=False,
    tick=0.25, slippage_ticks=1, commission=0.62,
    start="2024-10-23", end=None, timeframe="",
)


def _params(overrides):
    bad = set(overrides) - set(DEFAULTS)
    if bad:
        raise TypeError(f"unknown parameters: {sorted(bad)}")
    return SimpleNamespace(**{**DEFAULTS, **overrides})


# ---------------------------------------------------------------- data input
def _finish(df):
    """Numeric/dedupe/sort. Drops bars whose timestamp has non-zero seconds (Yahoo's trailing xx:59:59 snapshot of
    the forming bar); everything else is kept, including :30 bars on early-close days. Count kept in df.attrs."""
    df = df[["open", "high", "low", "close", "volume"]].astype(float).dropna()
    df = df[~df.index.duplicated()].sort_index()
    df.index.name = "time"
    t = df.index.tz_convert("UTC")
    snap = np.asarray((t.second != 0) | (t.microsecond != 0))
    if snap.any():
        print(f"data cleaning: dropped {int(snap.sum())} snapshot bar(s) with non-zero seconds")
    df = df[~snap]
    df.attrs["snapshot_dropped"] = int(snap.sum())
    return df


def load_csv(path):
    """TradingView 'Export chart data' CSV or generic OHLCV CSV. Naive time strings are assumed UTC."""
    raw = pd.read_csv(path)
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    tcol = next((c for c in ("time", "timestamp", "datetime", "date") if c in raw.columns), None)
    if tcol is None:
        raise ValueError("no time column (time/timestamp/datetime/date) in CSV")
    t = raw[tcol]
    if pd.api.types.is_numeric_dtype(t):
        unit = "ms" if t.abs().max() > 1e11 else "s"
        idx = pd.to_datetime(t, unit=unit, utc=True)
    else:
        idx = pd.to_datetime(t, utc=True, format="ISO8601")
    raw.index = pd.DatetimeIndex(idx).tz_convert(TZ)
    missing = {"open", "high", "low", "close", "volume"} - set(raw.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    return _finish(raw)


class YahooUnavailable(RuntimeError):
    pass


RETRY_DELAYS = (15, 30, 60, 120)  # seconds; first attempt + 4 retries on HTTP 429/5xx


def _download_yahoo(url, sleep=time.sleep):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                                            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
            if attempt == len(RETRY_DELAYS):
                raise YahooUnavailable(f"Yahoo is rate-limiting or unavailable (HTTP {e.code}); retry later") from None
            ra = e.headers.get("Retry-After") if e.headers else None
            wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else RETRY_DELAYS[attempt]
            print(f"Yahoo HTTP {e.code}; retrying in {wait:g}s ({attempt + 1}/{len(RETRY_DELAYS)})", file=sys.stderr)
            sleep(wait)


def fetch_yahoo(symbol="MNQ=F", interval="1h", range_="730d", cache_dir=None, refresh=False, sleep=time.sleep):
    """Yahoo chart API. The raw response is cached in cache_dir/<symbol>_<interval>_<range>.json and reused
    unless refresh=True."""
    path = os.path.join(cache_dir, f"{symbol}_{interval}_{range_}.json") if cache_dir else None
    if path and not refresh and os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    else:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
        data = _download_yahoo(url, sleep)
        if path:
            os.makedirs(cache_dir, exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f)
    res = data["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")},
                      index=pd.DatetimeIndex(pd.to_datetime(res["timestamp"], unit="s", utc=True)).tz_convert(TZ))
    return _finish(df)  # None -> NaN -> dropped


# ---------------------------------------------------------------- indicator primitives
def pivots(x, left, right, high=True):
    """ta.pivothigh/pivotlow. out[i] = pivot value of bar i-right, confirmed on bar i, else NaN.
    Tie rule (approximation): the pivot bar must be STRICTLY greater (lower) than all `left` bars before
    and all `right` bars after; equal neighbours disqualify it."""
    out = np.full(len(x), np.nan)
    for i in range(left + right, len(x)):
        p = i - right
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if (x[p] > w).all() if high else (x[p] < w).all():
            out[i] = x[p]
    return out


def ema(x, n):
    """ta.ema: alpha=2/(n+1), seeded with the SMA of the first n values; NaN before n values exist."""
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def sma(x, n):
    return pd.Series(x).rolling(n).mean().to_numpy()


def htf_series(df, minutes=240, fast=20, slow=50, src=None):
    """(ema_fast, ema_slow, close) of the last COMPLETED HTF bar before each bar of df (== expr[1] + lookahead_on).
    HTF bars are built from `src` (default df; pass a longer/finer series for EMA warm-up) and anchored to 18:00
    New York wall time (CME session open); approximates TradingView's 4H grid."""
    src = df if src is None else src
    off = pd.Timedelta(hours=18)
    skey = (src.index.tz_localize(None) - off).floor(f"{minutes}min")
    key = (df.index.tz_localize(None) - off).floor(f"{minutes}min")
    hc = src["close"].groupby(skey).last()
    ef, es = ema(hc.to_numpy(), fast), ema(hc.to_numpy(), slow)
    pos = hc.index.searchsorted(key, side="left") - 1  # previous existing HTF bar
    ok = pos >= 0
    take = lambda a: np.where(ok, a[np.where(ok, pos, 0)], np.nan)
    return take(ef), take(es), take(hc.to_numpy())


def _minutes(s):
    return int(s[:2]) * 60 + int(s[2:4]), int(s[5:7]) * 60 + int(s[7:9])


def in_session_window(mod, spec):
    a, b = _minutes(spec)
    return (a <= mod < b) if a < b else (mod >= a or mod < b)  # 1900-0200 wraps midnight


def size_trade(side, close, top, bot, p):
    """Pine sizing. side=+1 long / -1 short; top/bot = OTE zone prices. Returns (contracts, sl, tp)."""
    sl = bot - (top - bot) * 0.05 if side > 0 else top + (top - bot) * 0.05
    pts = (close - sl) * side
    cts = min(math.floor(p.max_loss / (pts * DPP[p.instrument])), p.max_contracts) if pts > 0 else 0
    return cts, sl, close + side * pts * p.rr


# ---------------------------------------------------------------- leg engine (long orientation)
class Leg:
    def __init__(self, O, H, L, C, p):
        self.O, self.H, self.L, self.C, self.p = O, H, L, C, p
        self.ph = pivots(H, p.swing_left, p.swing_right, True)
        self.pl = pivots(L, p.swing_left, p.swing_right, False)
        self.last_ph = self.last_pl = self.last_ph_bar = self.last_pl_bar = None
        self.anchor = self.ext = self.brk = None
        self.alive = self.active = self.used = False
        self.fvg_top = self.fvg_bot = self.fvg_bar = None
        self.prev_active, self.prev_ext = False, None
        self.top = self.bot = None
        self.bos = self.in_zone = self.fvg_ok = self.fvg_in = False
        self.bos_bar = None

    def step(self, i):
        p, H, L, C, R = self.p, self.H, self.L, self.C, self.p.swing_right
        ph, pl = self.ph[i], self.pl[i]
        hh = H[i - R:i + 1].max() if i >= R else np.nan
        if not np.isnan(ph):
            self.last_ph, self.last_ph_bar = ph, i - R
        if not np.isnan(pl):
            self.last_pl, self.last_pl_bar = pl, i - R
            self.anchor, self.ext = pl, hh
            # break level: latest confirmed swing high strictly before the anchor and still unbroken
            ok = self.last_ph_bar is not None and self.last_ph_bar < i - R and self.last_ph > hh
            self.brk = self.last_ph if ok else None
            self.alive, self.active, self.used = True, False, False
        elif self.alive:
            self.ext = max(self.ext, H[i])
        if self.alive and C[i] < self.anchor:
            self.alive = self.active = False
        self.bos = False
        if self.alive and not self.active and self.brk is not None and self.ext > self.brk:
            self.active = self.bos = True
            self.bos_bar = i
        if i >= 2 and L[i] > H[i - 2] and C[i - 1] > H[i - 2]:
            self.fvg_top, self.fvg_bot, self.fvg_bar = L[i], H[i - 2], i
        if self.active:
            rng = self.ext - self.anchor
            self.top, self.bot = self.ext - rng * p.fib_low, self.ext - rng * p.fib_high
        else:
            self.top = self.bot = None
        self.in_zone = bool(self.active and self.prev_active and self.prev_ext is not None
                            and H[i] <= self.prev_ext and L[i] <= self.top and C[i] >= self.bot)
        recent = self.fvg_bar is not None and i - self.fvg_bar <= p.fvg_lookback
        self.fvg_in = bool(recent and self.top is not None and self.fvg_bot <= self.top and self.fvg_top >= self.bot)
        self.fvg_ok = (not p.require_fvg_in_ote) or self.fvg_in
        self.prev_active, self.prev_ext = self.active, self.ext


def cvd_delta(h, l, c, v):
    """Per-bar buy_vol - sell_vol: volume * (2*close - low - high) / range, 0 on zero-range bars."""
    rng = h - l
    return np.where(rng > 0, v * (2 * c - l - h) / np.where(rng > 0, rng, 1.0), 0.0)


def compute_signals(df, htf_df=None, **params):
    """Per-bar list of dicts with the indicator state and long/short signals (once per leg)."""
    p = _params(params)
    o, h, l, c, v = (df[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    n = len(df)
    legs = {1: Leg(o, h, l, c, p), -1: Leg(-o, -l, -h, -c, p)}
    vma = sma(v, p.vol_ma_len)
    cvd = np.cumsum(cvd_delta(h, l, c, v))
    cvd_ma = ema(cvd, p.cvd_len)
    ef, es, hc = htf_series(df, p.htf_minutes, p.htf_ema_fast, p.htf_ema_slow, htf_df)
    with np.errstate(invalid="ignore"):
        htf_ok = {1: (ef > es) & (hc > ef), -1: (ef < es) & (hc < ef)}
        cvd_ok = {1: cvd > cvd_ma, -1: cvd < cvd_ma}
        vol_ok = (v / vma) >= p.rvol_min
    idx = df.index
    mod = idx.hour * 60 + idx.minute
    cidx = idx.tz_convert(EXCHANGE_TZ)
    dow, dom = cidx.dayofweek, cidx.day
    rows = []
    for i in range(n):
        flags = [getattr(p, key) and in_session_window(mod[i], spec) for key, _, spec in SESSIONS]
        tag = next((s[1] for s, f in zip(SESSIONS, flags) if f), "-")
        session_ok = (not p.use_session_filter) or any(flags)
        blocked = p.use_news_filter and ((p.block_nfp and dow[i] == 4 and dom[i] <= 7)
                                         or (p.block_fomc and dow[i] == 2 and 8 <= dom[i] <= 21))
        row = dict(time=idx[i], session=tag, bos_bull=False, bos_bear=False,
                   htf_valid=not (np.isnan(ef[i]) or np.isnan(es[i]) or np.isnan(hc[i])))
        for side, name in ((1, "long"), (-1, "short")):
            leg = legs[side]
            leg.step(i)
            O, H, L, C = leg.O[i], leg.H[i], leg.L[i], leg.C[i]
            items = dict(
                htf=bool(htf_ok[side][i]), ote=leg.in_zone, vol=bool(vol_ok[i]), cvd=bool(cvd_ok[side][i]),
                bar=bool(C > O and (C - O) > (H - L) * 0.2), fvg=leg.fvg_ok)
            score = sum(items.values())
            cts, sl, tp, zt, zb = 0, None, None, None, None
            if leg.active:
                zt, zb = (leg.top, leg.bot) if side > 0 else (-leg.bot, -leg.top)  # original price space
                cts, sl, tp = size_trade(side, side * C, zt, zb, p)  # side*C = original close
            sig = bool(score >= p.min_score and leg.in_zone and session_ok and not blocked
                       and cts >= 1 and not leg.used)
            meta = None
            if sig:
                leg.used = True
                bias = "bull" if htf_ok[1][i] else "bear" if htf_ok[-1][i] else "neutral"
                C0 = side * C
                depth = (zt - C0) / (zt - zb) if side > 0 else (C0 - zb) / (zt - zb)
                meta = dict(
                    item_htf=items["htf"], item_zone=items["ote"], item_rvol=items["vol"], item_cvd=items["cvd"],
                    item_bar=items["bar"], item_fvg=items["fvg"], rvol=float(v[i] / vma[i]),
                    cvd_diff=float(side * (cvd[i] - cvd_ma[i])), htf_bias=bias, fvg_present=leg.fvg_in,
                    zone_depth=float(depth), leg_size=float(leg.ext - leg.anchor), bars_from_bos=i - leg.bos_bar)
            row.update({f"bos_{'bull' if side > 0 else 'bear'}": leg.bos, f"{name}_in_zone": leg.in_zone,
                        f"{name}_score": score, f"{name}_items": items, f"{name}_cts": cts, f"{name}_sl": sl, f"{name}_tp": tp,
                        f"{name}_zone": (zb, zt), f"{name}_signal": sig, f"{name}_meta": meta})
        rows.append(row)
    return rows


# ---------------------------------------------------------------- trade simulation
def simulate(df, signals, **params):
    """signals[i] is None or dict(side, qty, sl, tp, score, session) decided at the close of bar i.
    Entry = bar i+1 open +/- slippage. SL/TP are rounded to the tick. Exits are checked from the entry bar on.
    Optional signal key `meta` (dict) is copied into the trade row."""
    p = _params(params)
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    slip = p.slippage_ticks * p.tick
    dpp = DPP[p.instrument]
    trades, pend, pos = [], None, None

    def close_trade(price, reason, t_idx, bar_hi, bar_lo):
        """bar_hi/bar_lo: the part of the exit bar's range the price path visited before the exit."""
        d = pos["side"]
        gross = (price - pos["entry"]) * d * pos["qty"] * dpp
        net = gross - 2 * p.commission * pos["qty"]
        risk = abs(pos["entry"] - pos["sl"]) * pos["qty"] * dpp
        a, sg = pos["i"], pos["sig_i"]
        rp = abs(c[sg] - pos["sl"])  # planned risk in points (signal close to stop)
        hi, lo = max(h[a:t_idx].max() if a < t_idx else -np.inf, bar_hi), min(l[a:t_idx].min() if a < t_idx else np.inf, bar_lo)
        fav, adv = ((hi - pos["entry"]), (pos["entry"] - lo)) if d > 0 else ((pos["entry"] - lo), (hi - pos["entry"]))
        st = ny = df.index[sg]
        trades.append(dict(pos.get("meta") or {}, timeframe=p.timeframe, signal_time=st, weekday=ny.day_name(),
            hour=ny.hour, month=ny.month, sl_dist=rp, planned_risk=rp * pos["qty"] * dpp, contracts=pos["qty"],
            entry_slippage=slip * pos["qty"] * dpp, mfe_r=max(fav, 0) / rp if rp > 0 else np.nan,
            mae_r=max(adv, 0) / rp if rp > 0 else np.nan, bars_held=t_idx - a + 1, win=int(net > 0),
            
            entry_time=df.index[pos["i"]], exit_time=df.index[t_idx], side="long" if d > 0 else "short",
            qty=pos["qty"], entry=pos["entry"], exit=price, sl=pos["sl"], tp=pos["tp"], exit_reason=reason,
            gross_pnl=gross, net_pnl=net, r_multiple=net / risk if risk > 0 else np.nan,
            score=pos["score"], session=pos["session"], open_at_end=reason == "END"))

    def tick(x):
        return math.floor(x / p.tick + 0.5) * p.tick

    def visible(d, reason, fill, i, other_seen):
        """Exit bar range seen up to the exit: the exit side is capped at the fill, the other extreme counts only
        if the intrabar path reached it first (otherwise just the open)."""
        exit_high = (d > 0) == (reason == "TP")
        if exit_high:
            return fill, (l[i] if other_seen else o[i])
        return (h[i] if other_seen else o[i]), fill

    for i in range(len(df)):
        if pend is not None:
            pos = dict(pend, i=i, entry=o[i] + pend["side"] * slip, sig_i=i - 1, sl=tick(pend["sl"]), tp=tick(pend["tp"]))
            pend = None
        if pos is not None:
            d, sl, tp = pos["side"], pos["sl"], pos["tp"]
            if (o[i] <= sl) if d > 0 else (o[i] >= sl):  # opened through the stop: fill at the open + slippage
                fill = o[i] - d * slip
                close_trade(fill, "SL", i, *visible(d, "SL", fill, i, False))
                pos = None
            elif (o[i] >= tp) if d > 0 else (o[i] <= tp):  # opened beyond the target: fill at the open, no slippage
                close_trade(o[i], "TP", i, *visible(d, "TP", o[i], i, False))
                pos = None
            else:
                hit = {"TP": h[i] >= tp if d > 0 else l[i] <= tp, "SL": l[i] <= sl if d > 0 else h[i] >= sl}
                high_first = (h[i] - o[i]) < (o[i] - l[i])  # open closer to high -> o,h,l,c else o,l,h,c (tie: low first)
                # for a long the high is the TP side, for a short it is the SL side
                order = ("TP", "SL") if high_first == (d > 0) else ("SL", "TP")
                reason = next((r for r in order if hit[r]), None)
                if reason:
                    fill = tp if reason == "TP" else sl - d * slip
                    exit_high = (d > 0) == (reason == "TP")
                    close_trade(fill, reason, i, *visible(d, reason, fill, i, high_first != exit_high))
                    pos = None
        if pos is None and signals[i] is not None and i + 1 < len(df):
            pend = signals[i]
    if pos is not None:
        close_trade(c[-1], "END", len(df) - 1, h[-1], l[-1])
    cols = ["entry_time", "exit_time", "side", "qty", "entry", "exit", "sl", "tp", "exit_reason",
            "gross_pnl", "net_pnl", "r_multiple", "score", "session", "open_at_end",
            "timeframe", "signal_time", "weekday", "hour", "month", "item_htf", "item_zone", "item_rvol", "item_cvd",
            "item_bar", "item_fvg", "rvol", "cvd_diff", "htf_bias", "fvg_present", "zone_depth", "leg_size",
            "bars_from_bos", "sl_dist", "planned_risk", "contracts", "entry_slippage", "mfe_r", "mae_r", "bars_held",
            "win"]
    return pd.DataFrame(trades, columns=cols)


def _group(tr, col):
    return {str(k): dict(trades=int(len(g)), net_pnl=float(g.net_pnl.sum()), win_rate=float((g.net_pnl > 0).mean()))
            for k, g in tr.groupby(col)}


def summarize(tr, first, last):
    n = len(tr)
    if n == 0:
        return dict(trades=0, wins=0, losses=0, win_rate=0.0, gross_profit=0.0, gross_loss=0.0, net_pnl=0.0,
                    profit_factor=None, avg_win=0.0, avg_loss=0.0, avg_r=0.0, expectancy=0.0, max_drawdown=0.0,
                    longest_losing_streak=0, trades_per_month=0.0, by_side={}, by_session={}, by_score={})
    months = max((last - first).days / 30.4375, 1e-9)
    net = tr.net_pnl
    gp, gl = float(net[net > 0].sum()), float(net[net < 0].sum())
    eq = net.cumsum().to_numpy()
    dd = float((np.maximum.accumulate(np.maximum(eq, 0)) - eq).max())
    streak = best = 0
    for x in net:
        streak = streak + 1 if x < 0 else 0
        best = max(best, streak)
    return dict(
        trades=n, wins=int((net > 0).sum()), losses=int((net < 0).sum()), win_rate=float((net > 0).mean()),
        gross_profit=gp, gross_loss=gl, net_pnl=float(net.sum()), profit_factor=gp / -gl if gl < 0 else None,
        avg_win=float(net[net > 0].mean()) if gp > 0 else 0.0, avg_loss=float(net[net < 0].mean()) if gl < 0 else 0.0,
        avg_r=float(tr.r_multiple.mean()), expectancy=float(net.mean()), max_drawdown=dd,
        longest_losing_streak=best, trades_per_month=n / months,
        by_side=_group(tr, "side"), by_session=_group(tr, "session"), by_score=_group(tr, "score"))


def run_backtest(df, htf_df=None, **params):
    """Returns (closed trades, summary). Signals before the HTF EMAs are valid are excluded and counted; trades still
    open at the end of data are left out of the trades/stats and reported as open_trades / open_unrealized_pnl."""
    p = _params(params)
    rows = compute_signals(df, htf_df, **params)
    lo = pd.Timestamp(p.start, tz=TZ) if p.start else df.index[0]
    hi = pd.Timestamp(p.end, tz=TZ) if p.end else None  # inclusive: Pine `time <= bt_end` on the bar open time
    sigs, excl_sigs, excl_bars = [], 0, 0
    for r in rows:
        s = None
        if r["time"] >= lo and (hi is None or r["time"] <= hi):
            excl_bars += not r["htf_valid"]
            # strategy: `short_signal and not long_signal` -> long wins; both legs were already marked used
            side, nm = (1, "long") if r["long_signal"] else (-1, "short")
            if r[f"{nm}_signal"]:
                if r["htf_valid"]:
                    s = dict(side=side, qty=r[f"{nm}_cts"], sl=r[f"{nm}_sl"], tp=r[f"{nm}_tp"], score=r[f"{nm}_score"],
                             session=r["session"], meta=r[f"{nm}_meta"])
                else:
                    excl_sigs += 1
        sigs.append(s)
    allt = simulate(df, sigs, **params)
    tr = allt[~allt.open_at_end.astype(bool)].reset_index(drop=True)
    opn = allt[allt.open_at_end.astype(bool)]
    last = min(hi, df.index[-1]) if hi is not None else df.index[-1]
    summ = summarize(tr, max(lo, df.index[0]), last)
    valid = [r["time"] for r in rows if r["htf_valid"]]
    summ.update(open_trades=len(opn), open_unrealized_pnl=float(opn.net_pnl.sum()),
                htf_valid_from=str(valid[0]) if valid else None, htf_excluded_bars=int(excl_bars),
                htf_excluded_signals=excl_sigs, snapshot_dropped=int(df.attrs.get("snapshot_dropped", 0)))
    return tr, summ


YAHOO_RANGES = {"5m": "60d", "15m": "60d", "1h": "730d"}  # Yahoo's maximum history per interval
LOW_CONFIDENCE_TRADES = 30


def run_and_write(df, tf, out_dir, min_score, start, end, htf_df=None):
    """Backtest one timeframe, write trades.csv/summary.json/analysis.json/report.md, return the summary."""
    tr, summ = run_backtest(df, htf_df, min_score=min_score, start=start, end=end, timeframe=tf)
    summ.update(timeframe=tf, data_start=str(df.index[0]), data_end=str(df.index[-1]), bars=len(df))
    an = analysis.analyze(tr)
    os.makedirs(out_dir, exist_ok=True)
    tr.to_csv(os.path.join(out_dir, "trades.csv"), index=False)
    for name, obj in (("summary.json", summ), ("analysis.json", an)):
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(obj, f, indent=2, default=str)
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write(analysis.report_md(f"VOF-OTE backtest {tf}", summ, an, tr, DEFAULTS["rr"]))
    print(f"[{tf}] bars: {len(df)}  data span {summ['data_start']} -> {summ['data_end']}  trades: {summ['trades']}  "
          f"open at end: {summ['open_trades']}  HTF valid from {summ['htf_valid_from']}  "
          f"excluded before HTF valid: {summ['htf_excluded_bars']} bars / {summ['htf_excluded_signals']} signals")
    return summ


def write_comparison(summaries, out_dir):
    rows = ["| Timeframe | Data span | Bars | Trades | Win % | Wilson LB % | PF | Avg R | Net $ | Max DD $ | Confidence |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summaries:
        n, w = s["trades"], s["wins"]
        pf = "-" if s["profit_factor"] is None else f"{s['profit_factor']:.2f}"
        rows.append(f"| {s['timeframe']} | {s['data_start'][:10]} to {s['data_end'][:10]} | {s['bars']} | {n} | "
                    f"{100 * s['win_rate']:.1f} | {100 * analysis.wilson_lb(w, n):.1f} | {pf} | {s['avg_r']:.2f} | "
                    f"{s['net_pnl']:.0f} | {s['max_drawdown']:.0f} | "
                    f"{'LOW CONFIDENCE (< 30 trades)' if n < LOW_CONFIDENCE_TRADES else 'ok'} |")
    with open(os.path.join(out_dir, "comparison.md"), "w") as f:
        f.write("# Timeframe comparison\n\n" + "\n".join(rows) + "\n")


def run_multi(symbol, timeframes, out_dir, min_score=DEFAULTS["min_score"], start=DEFAULTS["start"], end=None,
              refresh=False):
    """HTF bias for every timeframe is derived from the 1h series (fetched once, 730d) for EMA warm-up."""
    cache = os.path.join(out_dir, "cache")
    fetch = lambda tf: fetch_yahoo(symbol, tf, YAHOO_RANGES.get(tf, "60d"), cache_dir=cache, refresh=refresh)
    htf_src = fetch("1h")
    summaries = []
    for tf in timeframes:
        df = htf_src if tf == "1h" else fetch(tf)
        summaries.append(run_and_write(df, tf, os.path.join(out_dir, tf), min_score, start, end, htf_src))
    os.makedirs(out_dir, exist_ok=True)
    write_comparison(summaries, out_dir)
    return summaries


def main():
    ap = argparse.ArgumentParser(description="VOF-OTE v2.1 backtester")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv")
    src.add_argument("--yahoo", metavar="SYMBOL")
    ap.add_argument("--htf-csv", help="with --csv: longer-history CSV used only to build the 240-min HTF bars (EMA warm-up)")
    ap.add_argument("--timeframe", default="1h", help="timeframe label of the --csv data")
    ap.add_argument("--timeframes", default="5m,15m,1h", help="with --yahoo; max Yahoo range: 5m/15m 60d, 1h 730d")
    ap.add_argument("--min-score", type=int, default=DEFAULTS["min_score"])
    ap.add_argument("--start", default=DEFAULTS["start"])
    ap.add_argument("--end", default=None, help="inclusive up to this timestamp (bar open time <= END)")
    ap.add_argument("--out-dir", default="backtest_out")
    ap.add_argument("--refresh", action="store_true", help="with --yahoo: ignore the cached responses")
    a = ap.parse_args()
    if a.csv:
        htf = load_csv(a.htf_csv) if a.htf_csv else None
        summ = run_and_write(load_csv(a.csv), a.timeframe, a.out_dir, a.min_score, a.start, a.end, htf)
        print(json.dumps(summ, indent=2))
    else:
        try:
            run_multi(a.yahoo, a.timeframes.split(","), a.out_dir, a.min_score, a.start, a.end, a.refresh)
        except YahooUnavailable as e:
            sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
