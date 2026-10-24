# VOF-OTE v2.1 Python backtester

Reproduces the signals of `pine/vof-ote.pine` (the spec) and simulates trades like a TradingView strategy,
so MNQ can be backtested outside TradingView. Needs Python 3.13, pandas, numpy. No other dependencies.

## Run

```
# MNQ on 5m, 15m, 1h in one command (writes OUT/<tf>/{trades.csv,summary.json,analysis.json,report.md} + OUT/comparison.md)
python3 pine/backtest/vof_ote.py --yahoo MNQ=F --timeframes 5m,15m,1h --out-dir OUT
# exported data (files go straight into --out-dir)
python3 pine/backtest/vof_ote.py --csv FILE --timeframe 15m [--htf-csv LONGER_FILE] [--min-score 4] [--start 2024-10-23] [--end TIMESTAMP] [--out-dir DIR]
python3 -m unittest pine/backtest/test_vof_ote.py      # from the repo root
```

`--end` is inclusive up to the given timestamp (Pine `time <= bt_end` on the bar open time): `--end 2025-01-02` means
2025-01-02 00:00 New York, not the whole day; give a time of day to include more.

Yahoo history limits used (the maximum Yahoo serves): 5m = 60 days, 15m = 60 days, 1h = 730 days. The default start is
2024-10-23; for 5m/15m the data starts later, so the effective start is the first bar. The span actually covered is
printed per timeframe and stored in `summary.json` (`data_start`, `data_end`, `bars`) and `comparison.md`; timeframes with
< 30 trades are flagged LOW CONFIDENCE there.

Yahoo runs: each raw response is cached in `OUT/cache/<symbol>_<interval>_<range>.json` and reused on reruns unless
`--refresh` is given. HTTP 429/5xx is retried (first try plus 4 retries after 15, 30, 60, 120 s; `Retry-After` is
honored); if Yahoo still refuses the run exits with a one-line "Yahoo is rate-limiting ... retry later" error. The
Yahoo download path is untested against the live API: it was blocked by HTTP 429 rate limiting while this was written
(it is covered by mocked tests only).

**HTF warm-up.** The HTF bias needs EMA(50) of 240-min closes (about 200 hours of data). With `--yahoo`, the 1h series
(730d) is fetched once and the 240-min bars for every timeframe (5m, 15m, 1h) are built from it, so the EMAs are
warm from the first 5m/15m bar; each bar still sees only the last completed HTF bar (no lookahead). With `--csv` the HTF
bars come from the CSV itself unless `--htf-csv` supplies a longer history; signals on bars before the HTF EMAs are valid
are excluded (not traded), and the counts are printed and stored in `summary.json` (`htf_valid_from`,
`htf_excluded_bars`, `htf_excluded_signals`).

Open trades: a trade still open at the end of data is not in `trades.csv`, the stats or the rankings; `summary.json`
has `open_trades` and `open_unrealized_pnl` (marked at the last close, net of round-trip commission) instead.

Data cleaning: bars whose timestamp has non-zero seconds (Yahoo's trailing 16:59:59 snapshot of the forming bar) are
dropped and counted (`snapshot_dropped`); everything else is kept, including :30 bars on early-close days.

`trades.csv` has one row per trade: entry/exit prices and times, P&L, plus timeframe, signal and entry bar time, NY weekday/
hour/month, session, side, score and the six score items (`item_htf/zone/rvol/cvd/bar/fvg`), `rvol`, `cvd_diff` (CVD minus
its EMA, signed in the trade direction), `htf_bias`, `fvg_present` (actual, regardless of the require setting), `zone_depth`
(0 = OTE edge nearest the leg extreme, 1 = far edge; <0 or >1 for wick taps), `leg_size`, `bars_from_bos`, `sl_dist`,
`planned_risk`, `contracts`, `entry_slippage`, `mfe_r`/`mae_r` (bar highs/lows from entry bar through exit bar, in R of the
planned risk = |signal close - SL|, clipped at 0; on the exit bar only the part of the range the intrabar path
visited before the fill counts: capped at the TP or the stop fill, and the opposite extreme only if the path reached it first), `bars_held`, `win`.

`analysis.py` produces `analysis.json` / `report.md`: per-dimension and pairwise-combination stats (trades, wins, win rate,
Wilson 95% lower bound, avg R, total R, PF, net $), rankings (`item_zone` is always 1 for a signal, so it is shown
in the tables marked "always 1" but never ranked) (>= 10 trades; top 15 and bottom 10 by Wilson LB, top 15 by
avg R) and a how-to-read section. Ranked circumstances are hypotheses to forward-test, not rules.

In Python: `from vof_ote import load_csv, fetch_yahoo, run_backtest` and `trades, summary = run_backtest(df, **params)`.
Every Pine input is a keyword parameter (see `DEFAULTS` in `vof_ote.py`); signals before `start` or after `end` are ignored.

## Data

* `load_csv(path)`: TradingView "Export chart data" CSV (time as unix seconds/ms or ISO 8601 with offset) or any
  OHLCV CSV with a `time`/`timestamp`/`datetime`/`date` column. Column names are case-insensitive. Naive time strings are
  assumed UTC. Use the **same timeframe as the chart you want to compare to** (indicator was designed for intraday; 1h default).
* `fetch_yahoo(symbol, interval, range_)`: plain urllib call to the Yahoo chart API; rows with NaN are dropped.
  Yahoo gives about 730 days of 1h and 60 days of 5m/15m bars. Untested against the live API (rate limited with
  HTTP 429 when this was written); retry/cache logic is covered by mocked tests. `load_csv` and
  `fetch_yahoo` drop snapshot bars (non-zero seconds).

Both return a DataFrame indexed by tz-aware America/New_York bar-open timestamps.

## Approximations vs TradingView (results will not match TV trade for trade)

* **Pivot ties**: a pivot needs a strictly higher (lower) value than all `left` bars before and all `right` bars after.
  Pine's exact tie handling may differ, so equal highs/lows can differ.
* **EMA seed**: SMA of the first `len` values, NaN before that. TV starts from the first bar of its (longer) history, so
  early values differ; the difference decays but the HTF EMA(50) needs many 4h bars to converge (see HTF warm-up above).
* **HTF alignment**: 240-min bars are anchored to 18:00 New York (CME open), each bar is used only after it completes.
  TradingView's 4H grid for MNQ may differ (session break, holidays, partial bars).
* **Continuous contract**: Yahoo `MNQ=F` is a stitched front-month series; roll gaps are not adjusted and can create false
  FVGs/breaks. Volume and the OHLC differ from TradingView's `MNQ1!`. Prefer a TV export.
* **Calendar/sessions**: sessions use America/New_York (as the Pine `time()` calls do); NFP (Friday, day <= 7) and the FOMC
  proxy use America/Chicago (CME exchange tz, like Pine `dayofweek`/`dayofmonth`) on the bar open time. FOMC proxy is off.
* **Same-bar long+short**: long wins (strategy: `short_signal and not long_signal`); both legs are still marked used.
* **Sizing**: $2/point for MNQ (`syminfo.pointvalue`).
* **Fills**: signal on bar close, entry at next bar open + 1 tick against you; SL/TP fixed from the signal bar. SL and TP
  order prices are rounded to the nearest 0.25 tick before simulating (P&L uses the rounded prices). Intrabar path:
  open closer to high -> O,H,L,C else O,L,H,C (tie -> low first). Stops fill 1 tick worse; limits fill at the limit price
  and never get slippage. If a bar opens beyond the stop, the stop fills at the open (+ slippage); if it opens beyond the
  target, the target fills at the open (better price, no slippage). Commission $0.62 per contract
  per side. One position at a time; signals while in a trade (or pending entry) are dropped but still consume the leg
  ("once per leg"), as in the indicator. A trade open at the end of data is reported separately
  (see above; `simulate` flags it `open_at_end`, exit = last close). A signal on the last bar has no next bar and is dropped. Real brokers can differ.
* R multiple = net P&L / (|entry - SL| x qty x $/pt), using the actual (slipped) entry.
* The legs, BOS, FVG and scoring run over all data (warm-up) even before `--start`.

## Disclaimer

Backtests are simulations on historical data with the approximations above. Results are not a guarantee of future
performance and are not investment advice.
