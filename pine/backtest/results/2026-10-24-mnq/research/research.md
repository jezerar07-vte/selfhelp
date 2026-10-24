# Strategy research

## Method (pre-registered; written before results)

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

## Split dates

* 1h: {"tradable_from": "2024-10-23 00:00:00-04:00", "test_from": "2026-01-06 23:00:00-05:00", "end": "2026-10-23 16:00:00-04:00", "train_bars": 6883, "test_bars": 4589}
* 5m: {"tradable_from": "2026-08-14 00:05:00-04:00", "test_from": "2026-09-27 23:10:00-04:00", "end": "2026-10-23 16:55:00-04:00", "train_bars": 8150, "test_bars": 5434}
* 15m: {"tradable_from": "2026-08-14 00:00:00-04:00", "test_from": "2026-09-27 22:45:00-04:00", "end": "2026-10-23 16:45:00-04:00", "train_bars": 2732, "test_bars": 1822}

## Main table: TEST period

| Strategy | TF | Trades | /month | Win % | Wilson LB % | Breakeven WR % | PF | Avg R | Exp $/trade | Net $ | Max DD $ | Max losing streak | Flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VOF-OTE #20 | 1h | 17 | 1.8 | 29.4 | 13.3 | 23.6 | 1.35 | 0.27 | 39.3 | 669 | 500 | 3 | LOW CONFIDENCE |
| RSI2 | 1h | 1 | 0.1 | 100.0 | 20.7 | - | - | 0.13 | 26.3 | 26 | 0 | 0 | LOW CONFIDENCE |
| MOMENTUM | 1h | 82 | 8.6 | 45.1 | 34.8 | 50.0 | 0.82 | -0.06 | -8.8 | -724 | 1370 | 7 | |
| VOF-OTE #21 | 5m | 15 | 18.3 | 33.3 | 15.2 | 24.2 | 1.57 | 0.28 | 59.8 | 896 | 738 | 5 | LOW CONFIDENCE |
| RSI2 | 5m | 190 | 231.3 | 62.6 | 55.6 | 63.6 | 0.96 | -0.02 | -1.2 | -236 | 1396 | 5 | |
| MOMENTUM | 5m | 19 | 23.1 | 15.8 | 5.5 | 68.1 | 0.09 | -0.79 | -136.3 | -2590 | 2762 | 12 | LOW CONFIDENCE |
| VOF-OTE #19 | 15m | 12 | 14.6 | 8.3 | 1.5 | 25.7 | 0.26 | -0.71 | -99.7 | -1197 | 1197 | 6 | LOW CONFIDENCE |
| RSI2 | 15m | 25 | 30.4 | 64.0 | 44.5 | 55.4 | 1.43 | 0.04 | 11.8 | 296 | 473 | 4 | LOW CONFIDENCE |
| MOMENTUM | 15m | 19 | 23.1 | 21.1 | 8.5 | 70.7 | 0.11 | -0.44 | -59.1 | -1123 | 1181 | 10 | LOW CONFIDENCE |

## TRAIN and FULL

| Strategy | TF | Trades | /month | Win % | Wilson LB % | Breakeven WR % | PF | Avg R | Exp $/trade | Net $ | Max DD $ | Max losing streak | Flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VOF-OTE TRAIN | 1h | 22 | 1.5 | 31.8 | 16.4 | 23.4 | 1.53 | 0.21 | 52.2 | 1148 | 1185 | 7 | |
| VOF-OTE FULL | 1h | 39 | 1.6 | 30.8 | 18.6 | 23.6 | 1.44 | 0.24 | 46.6 | 1817 | 1185 | 7 | |
| RSI2 TRAIN | 1h | 33 | 2.3 | 69.7 | 52.7 | 59.1 | 1.59 | 0.14 | 23.5 | 774 | 552 | 3 | |
| RSI2 FULL | 1h | 34 | 1.4 | 70.6 | 53.8 | 59.8 | 1.61 | 0.14 | 23.5 | 800 | 552 | 3 | |
| MOMENTUM TRAIN | 1h | 214 | 14.8 | 47.7 | 41.1 | 52.5 | 0.82 | -0.03 | -8.2 | -1752 | 2705 | 7 | |
| MOMENTUM FULL | 1h | 296 | 12.3 | 47.0 | 41.3 | 51.8 | 0.82 | -0.04 | -8.4 | -2476 | 3852 | 7 | |
| VOF-OTE TRAIN | 5m | 23 | 15.9 | 34.8 | 18.8 | 27.1 | 1.44 | 0.33 | 49.4 | 1136 | 555 | 3 | |
| VOF-OTE FULL | 5m | 38 | 16.5 | 34.2 | 21.2 | 25.9 | 1.49 | 0.31 | 53.5 | 2032 | 738 | 5 | |
| RSI2 TRAIN | 5m | 284 | 196.5 | 62.7 | 56.9 | 66.3 | 0.86 | -0.04 | -4.5 | -1289 | 2412 | 5 | |
| RSI2 FULL | 5m | 474 | 206.1 | 62.7 | 58.2 | 65.2 | 0.90 | -0.03 | -3.2 | -1524 | 2728 | 5 | |
| MOMENTUM TRAIN | 5m | 28 | 19.4 | 50.0 | 32.6 | 37.2 | 1.69 | 0.33 | 63.8 | 1787 | 640 | 3 | |
| MOMENTUM FULL | 5m | 47 | 20.4 | 36.2 | 24.0 | 39.9 | 0.85 | -0.12 | -17.1 | -803 | 2868 | 12 | |
| VOF-OTE TRAIN | 15m | 22 | 15.2 | 36.4 | 19.7 | 28.7 | 1.42 | 0.42 | 41.9 | 922 | 1368 | 8 | |
| VOF-OTE FULL | 15m | 34 | 14.8 | 26.5 | 14.6 | 27.9 | 0.93 | 0.02 | -8.1 | -275 | 1638 | 8 | |
| RSI2 TRAIN | 15m | 50 | 34.6 | 58.0 | 44.2 | 71.8 | 0.54 | -0.12 | -22.7 | -1133 | 1364 | 4 | |
| RSI2 FULL | 15m | 75 | 32.6 | 60.0 | 48.7 | 67.1 | 0.74 | -0.07 | -11.2 | -837 | 1835 | 5 | |
| MOMENTUM TRAIN | 15m | 28 | 19.4 | 60.7 | 42.4 | 34.5 | 2.93 | 0.29 | 53.2 | 1490 | 280 | 2 | |
| MOMENTUM FULL | 15m | 47 | 20.4 | 44.7 | 31.4 | 40.6 | 1.18 | -0.01 | 7.8 | 366 | 1210 | 10 | |

## Verdict

* VOF-OTE 1h: FAIL - TEST trades 17 < 30; TEST Wilson LB 13.3% < breakeven WR 23.6%
* RSI2 1h: FAIL - TEST trades 1 < 30
* MOMENTUM 1h: FAIL - TRAIN not profitable (net -1752); TEST not profitable (net -724); TEST PF 0.82 < 1.2; TEST Wilson LB 34.8% < breakeven WR 50.0%
* VOF-OTE 5m: FAIL - TEST Wilson LB 15.2% < breakeven WR 24.2%
* RSI2 5m: FAIL - TRAIN not profitable (net -1289); TEST not profitable (net -236); TEST PF 0.96 < 1.2; TEST Wilson LB 55.6% < breakeven WR 63.6%
* MOMENTUM 5m: FAIL - TEST not profitable (net -2590); TEST PF 0.09 < 1.2; TEST Wilson LB 5.5% < breakeven WR 68.1%
* VOF-OTE 15m: FAIL - TEST not profitable (net -1197); TEST PF 0.26 < 1.2; TEST trades 12 < 15; TEST Wilson LB 1.5% < breakeven WR 25.7%
* RSI2 15m: FAIL - TRAIN not profitable (net -1133); TEST Wilson LB 44.5% < breakeven WR 55.4%
* MOMENTUM 15m: FAIL - TEST not profitable (net -1123); TEST PF 0.11 < 1.2; TEST Wilson LB 8.5% < breakeven WR 70.7%

Nothing passes. No strategy met the pre-registered rule, so none is supported by this data.

## Appendix: all 24 VOF-OTE variants (for transparency - not used for selection)

| TF | # | rr | min_score | fvg_in_ote | asia | chosen | TRAIN trades | TRAIN PF | TRAIN avg R | TEST trades | TEST win % | TEST PF | TEST avg R | TEST net $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1h | 0 | 1.5 | 3 | True | True |  | 50 | 0.84 | -0.23 | 25 | 36.0 | 1.00 | 0.01 | 4 |
| 1h | 1 | 1.5 | 3 | True | False |  | 43 | 0.71 | -0.33 | 22 | 36.4 | 1.07 | 0.04 | 140 |
| 1h | 2 | 1.5 | 3 | False | True |  | 64 | 0.84 | -0.20 | 34 | 38.2 | 1.05 | 0.03 | 168 |
| 1h | 3 | 1.5 | 3 | False | False |  | 56 | 0.76 | -0.27 | 30 | 40.0 | 1.17 | 0.08 | 479 |
| 1h | 4 | 1.5 | 4 | True | True |  | 22 | 1.37 | 0.08 | 17 | 41.2 | 1.32 | 0.21 | 500 |
| 1h | 5 | 1.5 | 4 | True | False |  | 18 | 1.24 | 0.04 | 14 | 50.0 | 2.09 | 0.48 | 1088 |
| 1h | 6 | 1.5 | 4 | False | True |  | 43 | 0.89 | -0.21 | 25 | 36.0 | 0.98 | 0.02 | -43 |
| 1h | 7 | 1.5 | 4 | False | False |  | 38 | 0.77 | -0.31 | 22 | 40.9 | 1.28 | 0.16 | 545 |
| 1h | 8 | 2.0 | 3 | True | True |  | 50 | 0.69 | -0.38 | 25 | 20.0 | 0.54 | -0.31 | -1491 |
| 1h | 9 | 2.0 | 3 | True | False |  | 43 | 0.58 | -0.49 | 22 | 22.7 | 0.66 | -0.21 | -905 |
| 1h | 10 | 2.0 | 3 | False | True |  | 64 | 0.77 | -0.29 | 34 | 23.5 | 0.66 | -0.23 | -1443 |
| 1h | 11 | 2.0 | 3 | False | False |  | 56 | 0.71 | -0.35 | 30 | 26.7 | 0.80 | -0.13 | -683 |
| 1h | 12 | 2.0 | 4 | True | True |  | 22 | 1.19 | 0.05 | 17 | 29.4 | 0.99 | 0.04 | -27 |
| 1h | 13 | 2.0 | 4 | True | False |  | 18 | 1.28 | 0.12 | 14 | 35.7 | 1.42 | 0.26 | 561 |
| 1h | 14 | 2.0 | 4 | False | True |  | 43 | 0.66 | -0.42 | 25 | 24.0 | 0.68 | -0.18 | -999 |
| 1h | 15 | 2.0 | 4 | False | False |  | 38 | 0.58 | -0.50 | 22 | 27.3 | 0.84 | -0.07 | -411 |
| 1h | 16 | 3.0 | 3 | True | True |  | 50 | 0.86 | -0.28 | 25 | 16.0 | 0.55 | -0.31 | -1530 |
| 1h | 17 | 3.0 | 3 | True | False |  | 43 | 0.69 | -0.44 | 22 | 18.2 | 0.66 | -0.21 | -944 |
| 1h | 18 | 3.0 | 3 | False | True |  | 64 | 1.03 | -0.13 | 33 | 21.2 | 0.82 | -0.12 | -733 |
| 1h | 19 | 3.0 | 3 | False | False |  | 56 | 0.93 | -0.22 | 29 | 24.1 | 1.01 | 0.00 | 27 |
| 1h | 20 | 3.0 | 4 | True | True | yes | 22 | 1.53 | 0.21 | 17 | 29.4 | 1.35 | 0.27 | 669 |
| 1h | 21 | 3.0 | 4 | True | False |  | 18 | 1.59 | 0.27 | 14 | 35.7 | 1.93 | 0.55 | 1257 |
| 1h | 22 | 3.0 | 4 | False | True |  | 43 | 0.91 | -0.26 | 25 | 20.0 | 0.74 | -0.14 | -859 |
| 1h | 23 | 3.0 | 4 | False | False |  | 38 | 0.79 | -0.37 | 22 | 22.7 | 0.90 | -0.02 | -271 |
| 5m | 0 | 1.5 | 3 | True | True |  | 77 | 0.58 | -0.33 | 55 | 43.6 | 1.09 | -0.01 | 469 |
| 5m | 1 | 1.5 | 3 | True | False |  | 54 | 0.70 | -0.33 | 36 | 41.7 | 1.07 | -0.02 | 259 |
| 5m | 2 | 1.5 | 3 | False | True |  | 97 | 0.71 | -0.27 | 74 | 40.5 | 1.00 | -0.09 | -7 |
| 5m | 3 | 1.5 | 3 | False | False |  | 66 | 0.87 | -0.22 | 49 | 40.8 | 1.03 | -0.04 | 125 |
| 5m | 4 | 1.5 | 4 | True | True |  | 39 | 0.53 | -0.32 | 28 | 35.7 | 0.83 | -0.17 | -507 |
| 5m | 5 | 1.5 | 4 | True | False |  | 23 | 0.89 | -0.08 | 16 | 43.8 | 1.15 | 0.05 | 208 |
| 5m | 6 | 1.5 | 4 | False | True |  | 69 | 0.48 | -0.45 | 52 | 46.2 | 1.23 | 0.05 | 1055 |
| 5m | 7 | 1.5 | 4 | False | False |  | 47 | 0.56 | -0.43 | 34 | 44.1 | 1.20 | 0.04 | 647 |
| 5m | 8 | 2.0 | 3 | True | True |  | 77 | 0.65 | -0.29 | 55 | 40.0 | 1.26 | 0.09 | 1398 |
| 5m | 9 | 2.0 | 3 | True | False |  | 54 | 0.81 | -0.28 | 36 | 36.1 | 1.14 | 0.01 | 546 |
| 5m | 10 | 2.0 | 3 | False | True |  | 97 | 0.70 | -0.28 | 74 | 37.8 | 1.19 | 0.03 | 1441 |
| 5m | 11 | 2.0 | 3 | False | False |  | 66 | 0.89 | -0.22 | 49 | 36.7 | 1.16 | 0.03 | 834 |
| 5m | 12 | 2.0 | 4 | True | True |  | 39 | 0.73 | -0.16 | 28 | 32.1 | 0.96 | -0.11 | -115 |
| 5m | 13 | 2.0 | 4 | True | False |  | 23 | 1.22 | 0.15 | 16 | 37.5 | 1.21 | 0.08 | 327 |
| 5m | 14 | 2.0 | 4 | False | True |  | 69 | 0.51 | -0.45 | 52 | 42.3 | 1.41 | 0.16 | 1989 |
| 5m | 15 | 2.0 | 4 | False | False |  | 47 | 0.64 | -0.42 | 34 | 38.2 | 1.27 | 0.08 | 939 |
| 5m | 16 | 3.0 | 3 | True | True |  | 74 | 0.74 | -0.26 | 53 | 35.8 | 1.65 | 0.32 | 3591 |
| 5m | 17 | 3.0 | 3 | True | False |  | 51 | 0.90 | -0.22 | 34 | 38.2 | 1.93 | 0.45 | 3232 |
| 5m | 18 | 3.0 | 3 | False | True |  | 93 | 0.87 | -0.18 | 70 | 32.9 | 1.52 | 0.21 | 3905 |
| 5m | 19 | 3.0 | 3 | False | False |  | 62 | 1.09 | -0.07 | 47 | 36.2 | 1.71 | 0.38 | 3591 |
| 5m | 20 | 3.0 | 4 | True | True |  | 39 | 0.92 | 0.03 | 27 | 25.9 | 1.07 | -0.04 | 245 |
| 5m | 21 | 3.0 | 4 | True | False | yes | 23 | 1.44 | 0.33 | 15 | 33.3 | 1.57 | 0.28 | 896 |
| 5m | 22 | 3.0 | 4 | False | True |  | 67 | 0.54 | -0.40 | 50 | 38.0 | 1.84 | 0.41 | 4191 |
| 5m | 23 | 3.0 | 4 | False | False |  | 45 | 0.61 | -0.46 | 32 | 40.6 | 2.17 | 0.55 | 3634 |
| 15m | 0 | 1.5 | 3 | True | True |  | 23 | 0.53 | -0.23 | 12 | 58.3 | 2.11 | 0.43 | 872 |
| 15m | 1 | 1.5 | 3 | True | False |  | 15 | 1.42 | 0.28 | 7 | 57.1 | 2.01 | 0.42 | 468 |
| 15m | 2 | 1.5 | 3 | False | True |  | 31 | 1.00 | 0.03 | 18 | 50.0 | 1.36 | 0.16 | 507 |
| 15m | 3 | 1.5 | 3 | False | False |  | 22 | 1.71 | 0.31 | 12 | 41.7 | 0.98 | 0.01 | -19 |
| 15m | 4 | 1.5 | 4 | True | True |  | 12 | 0.29 | -0.42 | 5 | 40.0 | 0.90 | -0.03 | -42 |
| 15m | 5 | 1.5 | 4 | True | False |  | 10 | 0.48 | -0.27 | 3 | 33.3 | 0.55 | -0.18 | -139 |
| 15m | 6 | 1.5 | 4 | False | True |  | 19 | 0.31 | -0.50 | 11 | 54.5 | 1.96 | 0.35 | 690 |
| 15m | 7 | 1.5 | 4 | False | False |  | 13 | 0.79 | -0.08 | 6 | 66.7 | 3.08 | 0.66 | 629 |
| 15m | 8 | 2.0 | 3 | True | True |  | 23 | 0.71 | -0.07 | 12 | 41.7 | 1.47 | 0.22 | 518 |
| 15m | 9 | 2.0 | 3 | True | False |  | 15 | 1.33 | 0.36 | 7 | 28.6 | 0.83 | -0.15 | -134 |
| 15m | 10 | 2.0 | 3 | False | True |  | 31 | 1.11 | 0.15 | 18 | 33.3 | 0.96 | -0.10 | -69 |
| 15m | 11 | 2.0 | 3 | False | False |  | 22 | 1.39 | 0.32 | 12 | 16.7 | 0.37 | -0.53 | -931 |
| 15m | 12 | 2.0 | 4 | True | True |  | 12 | 0.40 | -0.30 | 5 | 20.0 | 0.50 | -0.43 | -263 |
| 15m | 13 | 2.0 | 4 | True | False |  | 10 | 0.30 | -0.41 | 3 | 0.0 | 0.00 | -1.02 | -428 |
| 15m | 14 | 2.0 | 4 | False | True |  | 19 | 0.42 | -0.39 | 11 | 36.4 | 1.24 | 0.08 | 249 |
| 15m | 15 | 2.0 | 4 | False | False |  | 13 | 0.68 | -0.11 | 6 | 33.3 | 1.04 | -0.00 | 27 |
| 15m | 16 | 3.0 | 3 | True | True |  | 23 | 0.66 | -0.11 | 12 | 16.7 | 0.60 | -0.35 | -643 |
| 15m | 17 | 3.0 | 3 | True | False |  | 15 | 0.70 | 0.04 | 7 | 0.0 | 0.00 | -1.02 | -1095 |
| 15m | 18 | 3.0 | 3 | False | True |  | 30 | 1.13 | 0.20 | 18 | 16.7 | 0.57 | -0.44 | -1018 |
| 15m | 19 | 3.0 | 3 | False | False | yes | 22 | 1.42 | 0.42 | 12 | 8.3 | 0.26 | -0.71 | -1197 |
| 15m | 20 | 3.0 | 4 | True | True |  | 12 | 0.37 | -0.38 | 5 | 20.0 | 0.76 | -0.23 | -127 |
| 15m | 21 | 3.0 | 4 | True | False |  | 10 | 0.20 | -0.61 | 3 | 0.0 | 0.00 | -1.02 | -428 |
| 15m | 22 | 3.0 | 4 | False | True |  | 19 | 0.27 | -0.60 | 11 | 18.2 | 0.71 | -0.29 | -389 |
| 15m | 23 | 3.0 | 4 | False | False |  | 13 | 0.41 | -0.40 | 6 | 0.0 | 0.00 | -1.02 | -934 |
