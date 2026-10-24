"""Circumstance analysis of a trades DataFrame (from vof_ote.simulate): grouped stats, rankings, markdown report."""
import itertools
import math

import numpy as np
import pandas as pd

MIN_N = 10
SIDE_DIMS = ["side", "session", "score", "htf_bias", "fvg_present", "rvol_q", "zone_bucket"]  # combo dimensions
ITEMS = ["htf", "zone", "rvol", "cvd", "bar", "fvg"]
ORDER = ["side", "session", "hour", "weekday", "score"] + [f"item_{i}" for i in ITEMS] + [
    "htf_bias", "rvol_q", "zone_bucket", "sl_q", "bos_bucket", "month"]


def wilson_lb(wins, n, z=1.96):
    if n == 0:
        return 0.0
    p = wins / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def stats(g):
    n, w = len(g), int((g.net_pnl > 0).sum())
    gp, gl = g.net_pnl[g.net_pnl > 0].sum(), g.net_pnl[g.net_pnl < 0].sum()
    r = g.r_multiple.dropna()
    return dict(trades=n, wins=w, win_rate=w / n, wilson_lb=wilson_lb(w, n), avg_r=float(r.mean()) if len(r) else 0.0,
                total_r=float(r.sum()), profit_factor=float(gp / -gl) if gl < 0 else None, net_pnl=float(g.net_pnl.sum()),
                small_sample=n < MIN_N)


def _quartiles(x, tag):
    """Quartile labels with the bucket edges shown. Returns (labels Series, edges list)."""
    edges = sorted({float(e) for e in np.quantile(x, [0, .25, .5, .75, 1]).round(3)})
    if len(edges) < 2:
        return pd.Series([f"{tag}1 [{edges[0]}]"] * len(x), index=x.index), edges
    codes = pd.cut(x, bins=[-np.inf] + edges[1:-1] + [np.inf], labels=False, include_lowest=True)
    names = [f"{tag}{k + 1} [{edges[k]}, {edges[k + 1]}]" for k in range(len(edges) - 1)]
    return codes.map(lambda k: names[int(k)]), edges


def add_buckets(tr):
    """Returns (DataFrame of dimension columns, dict of quartile edges)."""
    d = pd.DataFrame(index=tr.index)
    d["side"], d["session"], d["hour"], d["weekday"] = tr.side, tr.session, tr.hour, tr.weekday
    d["score"], d["htf_bias"], d["month"] = tr.score, tr.htf_bias, tr.month
    d["fvg_present"] = tr.fvg_present.map({True: "fvg", False: "no fvg"})
    for i in ITEMS:
        d[f"item_{i}"] = tr[f"item_{i}"].map({1: "present", 0: "absent", True: "present", False: "absent"})
    d["rvol_q"], e1 = _quartiles(tr.rvol, "Q")
    d["sl_q"], e2 = _quartiles(tr.sl_dist, "Q")
    z = tr.zone_depth
    d["zone_bucket"] = np.select([z < 0, z < .33, z < .66, z <= 1], ["<0", "0-0.33", "0.33-0.66", "0.66-1"], ">1")
    b = tr.bars_from_bos
    d["bos_bucket"] = np.select([b <= 2, b <= 5, b <= 10], ["1-2", "3-5", "6-10"], "11+")
    return d, dict(rvol=e1, sl_dist=e2)


def analyze(tr):
    """Grouped stats for every dimension and every pairwise combination, plus rankings."""
    if len(tr) == 0:
        return dict(dimensions={}, combos=[], rankings=dict(top_win_lb=[], bottom_win_lb=[], top_avg_r=[]), edges={})
    d, edges = add_buckets(tr)
    dims = {k: [dict(group=str(g), **stats(tr.loc[idx])) for g, idx in d.groupby(k).groups.items()] for k in ORDER}
    combos = []
    for a, b in itertools.combinations(SIDE_DIMS, 2):
        for (ga, gb), idx in d.groupby([a, b]).groups.items():
            combos.append(dict(group=f"{a}={ga} & {b}={gb}", **stats(tr.loc[idx])))
    pool = [dict(dimension=k, **r) for k, rows in dims.items()
            if k not in ("month", "item_zone") for r in rows]  # month: report only; item_zone: always present
    pool += [dict(dimension="combo", **r) for r in combos]
    ok = [r for r in pool if not r["small_sample"]]
    by_lb = sorted(ok, key=lambda r: (-r["wilson_lb"], -r["trades"]))
    rank = dict(top_win_lb=by_lb[:15], bottom_win_lb=by_lb[::-1][:10],
                top_avg_r=sorted(ok, key=lambda r: (-r["avg_r"], -r["trades"]))[:15])
    return dict(dimensions=dims, combos=combos, rankings=rank, edges=edges)


def _pf(x):
    return "-" if x is None else f"{x:.2f}"


def _table(rows, cols):
    out = ["| " + " | ".join(h for h, _ in cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f(r) for _, f in cols) + " |" for r in rows]
    return "\n".join(out)


STAT_COLS = [("Trades", lambda r: str(r["trades"])), ("Wins", lambda r: str(r["wins"])),
             ("Win %", lambda r: f"{100 * r['win_rate']:.1f}"), ("Wilson LB %", lambda r: f"{100 * r['wilson_lb']:.1f}"),
             ("Avg R", lambda r: f"{r['avg_r']:.2f}"), ("Total R", lambda r: f"{r['total_r']:.1f}"),
             ("PF", lambda r: _pf(r["profit_factor"])), ("Net $", lambda r: f"{r['net_pnl']:.0f}")]


def breakeven_wr(tr, rr):
    """Win rate needed for zero expectancy: p = (1 + c) / (rr + 1), c = avg commission + entry slippage in R."""
    if len(tr) == 0:
        return 1 / (rr + 1), 0.0
    c = float(((tr.gross_pnl - tr.net_pnl + tr.entry_slippage) / tr.planned_risk).mean())
    return (1 + c) / (rr + 1), c


def report_md(title, summ, an, tr, rr):
    be, c = breakeven_wr(tr, rr)
    L = [f"# {title}", "", "## Headline", ""]
    for k in ("data_start", "data_end", "bars", "trades", "wins", "losses", "win_rate", "net_pnl", "profit_factor",
              "avg_r", "expectancy", "max_drawdown", "longest_losing_streak", "trades_per_month", "gross_profit",
              "gross_loss", "avg_win", "avg_loss", "open_trades", "open_unrealized_pnl", "htf_valid_from",
              "htf_excluded_bars", "htf_excluded_signals", "snapshot_dropped"):
        if k in summ:
            L.append(f"* {k}: {summ[k]}")
    if summ.get("trades", 0) < 30:
        L.append("* LOW CONFIDENCE: fewer than 30 trades")
    rk = an["rankings"]
    cols = [("Dimension", lambda r: r["dimension"]), ("Group", lambda r: r["group"])] + STAT_COLS
    for name, key in (("Highest win rate circumstances (by Wilson lower bound, >= 10 trades)", "top_win_lb"),
                      ("Worst circumstances (lowest Wilson lower bound, >= 10 trades)", "bottom_win_lb"),
                      ("Top by average R (>= 10 trades)", "top_avg_r")):
        L += ["", f"## {name}", "", _table(rk[key], cols) if rk[key] else "_none_"]
    L += ["", "## Full tables", ""]
    if an["edges"]:
        L += [f"RVOL quartile edges: {an['edges']['rvol']}; SL distance quartile edges (points): {an['edges']['sl_dist']}", ""]
    gcols = [("Group", lambda r: r["group"] + (" (small sample)" if r["small_sample"] else ""))] + STAT_COLS
    for k, rows in an["dimensions"].items():
        L += [f"### {k}" + (" (always 1: every signal is inside the OTE zone; not ranked)" if k == "item_zone" else ""), "", _table(rows, gcols), ""]
    L += ["## How to read this", "",
          "* Wilson LB is the lower end of the 95% confidence interval of the win rate. It penalises small samples, so "
          "9/10 wins gives about 0.60 and 60/100 gives about 0.50.",
          "* Open trades at the end of data and signals before the HTF EMAs are valid are excluded from every table here "
          "(counts in the headline).",
          f"* Groups with < {MIN_N} trades are marked small sample and excluded from rankings.",
          f"* Breakeven win rate at {rr:g}:R is {100 / (rr + 1):.1f}% before costs and about {100 * be:.1f}% including "
          f"commission and entry slippage (avg {c:.3f} R per trade; stop slippage not included). Win rate alone misleads: "
          "compare it to this and look at Avg R and PF.",
          "* Ranking many groups and combinations will surface some winners by chance. Treat top combos as hypotheses "
          "to forward-test, not rules. Groups overlap (a trade appears in many groups), so they are not independent."]
    return "\n".join(L) + "\n"
