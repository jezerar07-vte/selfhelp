# VOF-OTE backtest 1h

## Headline

* data_start: 2024-06-02 18:00:00-04:00
* data_end: 2026-10-23 16:00:00-04:00
* bars: 13738
* trades: 39
* wins: 12
* losses: 27
* win_rate: 0.3076923076923077
* net_pnl: 1816.6
* profit_factor: 1.440749025868469
* avg_r: 0.23904719449006023
* expectancy: 46.579487179487174
* max_drawdown: 1184.94
* longest_losing_streak: 7
* trades_per_month: 1.6261130136986301
* gross_profit: 5938.219999999999
* gross_loss: -4121.62
* avg_win: 494.85166666666663
* avg_loss: -152.65259259259258
* open_trades: 0
* open_unrealized_pnl: 0.0
* htf_valid_from: 2024-06-13 02:00:00-04:00
* htf_excluded_bars: 0
* htf_excluded_signals: 0
* snapshot_dropped: 1

## Highest win rate circumstances (by Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| rvol_q | Q3 [2.361, 3.396] | 10 | 5 | 50.0 | 23.7 | 0.99 | 9.9 | 2.54 | 1384 |
| session | NY | 14 | 6 | 42.9 | 21.4 | 0.69 | 9.7 | 2.03 | 1414 |
| side | short | 12 | 5 | 41.7 | 19.3 | 0.64 | 7.7 | 2.24 | 1361 |
| zone_bucket | <0 | 24 | 8 | 33.3 | 18.0 | 0.32 | 7.7 | 1.54 | 1309 |
| combo | htf_bias=bull & fvg_present=fvg | 13 | 5 | 38.5 | 17.7 | 0.61 | 7.9 | 2.16 | 1412 |
| sl_q | Q2 [41.5, 63.5] | 10 | 4 | 40.0 | 16.8 | 0.80 | 8.0 | 2.75 | 1234 |
| bos_bucket | 11+ | 10 | 4 | 40.0 | 16.8 | 0.57 | 5.7 | 2.25 | 1106 |
| combo | side=short & fvg_present=fvg | 10 | 4 | 40.0 | 16.8 | 0.57 | 5.7 | 2.09 | 1026 |
| htf_bias | bull | 27 | 8 | 29.6 | 15.9 | 0.21 | 5.6 | 1.43 | 1243 |
| combo | side=short & score=4 | 11 | 4 | 36.4 | 15.2 | 0.43 | 4.7 | 1.79 | 873 |
| combo | fvg_present=fvg & zone_bucket=<0 | 11 | 4 | 36.4 | 15.2 | 0.45 | 4.9 | 1.70 | 766 |
| combo | session=NY & score=4 | 12 | 4 | 33.3 | 13.8 | 0.30 | 3.6 | 1.31 | 418 |
| side | long | 27 | 7 | 25.9 | 13.2 | 0.06 | 1.6 | 1.15 | 456 |
| score | 4 | 33 | 8 | 24.2 | 12.8 | -0.08 | -2.8 | 1.02 | 86 |
| combo | fvg_present=no fvg & zone_bucket=<0 | 13 | 4 | 30.8 | 12.7 | 0.22 | 2.8 | 1.41 | 543 |

## Worst circumstances (lowest Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| weekday | Tuesday | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.5 | 0.31 | -1240 |
| sl_q | Q1 [0.75, 41.5] | 10 | 2 | 20.0 | 5.7 | -0.35 | -3.5 | 0.89 | -144 |
| rvol_q | Q4 [3.396, 6.54] | 10 | 2 | 20.0 | 5.7 | -0.31 | -3.1 | 0.91 | -97 |
| rvol_q | Q1 [0.17, 1.386] | 10 | 2 | 20.0 | 5.7 | -0.23 | -2.3 | 0.87 | -160 |
| combo | side=long & score=4 | 22 | 4 | 18.2 | 7.3 | -0.34 | -7.5 | 0.71 | -787 |
| combo | htf_bias=bull & fvg_present=no fvg | 14 | 3 | 21.4 | 7.6 | -0.17 | -2.3 | 0.90 | -169 |
| combo | htf_bias=bull & zone_bucket=<0 | 17 | 4 | 23.5 | 9.6 | -0.07 | -1.2 | 1.02 | 30 |
| combo | score=4 & fvg_present=no fvg | 17 | 4 | 23.5 | 9.6 | -0.08 | -1.4 | 1.00 | -8 |
| combo | side=long & fvg_present=fvg | 11 | 3 | 27.3 | 9.7 | 0.18 | 2.0 | 1.25 | 310 |
| bos_bucket | 1-2 | 11 | 3 | 27.3 | 9.7 | -0.02 | -0.2 | 1.25 | 282 |

## Top by average R (>= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| rvol_q | Q3 [2.361, 3.396] | 10 | 5 | 50.0 | 23.7 | 0.99 | 9.9 | 2.54 | 1384 |
| sl_q | Q2 [41.5, 63.5] | 10 | 4 | 40.0 | 16.8 | 0.80 | 8.0 | 2.75 | 1234 |
| session | NY | 14 | 6 | 42.9 | 21.4 | 0.69 | 9.7 | 2.03 | 1414 |
| side | short | 12 | 5 | 41.7 | 19.3 | 0.64 | 7.7 | 2.24 | 1361 |
| combo | htf_bias=bull & fvg_present=fvg | 13 | 5 | 38.5 | 17.7 | 0.61 | 7.9 | 2.16 | 1412 |
| bos_bucket | 11+ | 10 | 4 | 40.0 | 16.8 | 0.57 | 5.7 | 2.25 | 1106 |
| combo | side=short & fvg_present=fvg | 10 | 4 | 40.0 | 16.8 | 0.57 | 5.7 | 2.09 | 1026 |
| combo | fvg_present=fvg & zone_bucket=<0 | 11 | 4 | 36.4 | 15.2 | 0.45 | 4.9 | 1.70 | 766 |
| combo | side=short & score=4 | 11 | 4 | 36.4 | 15.2 | 0.43 | 4.7 | 1.79 | 873 |
| zone_bucket | <0 | 24 | 8 | 33.3 | 18.0 | 0.32 | 7.7 | 1.54 | 1309 |
| combo | session=NY & score=4 | 12 | 4 | 33.3 | 13.8 | 0.30 | 3.6 | 1.31 | 418 |
| combo | fvg_present=no fvg & zone_bucket=<0 | 13 | 4 | 30.8 | 12.7 | 0.22 | 2.8 | 1.41 | 543 |
| htf_bias | bull | 27 | 8 | 29.6 | 15.9 | 0.21 | 5.6 | 1.43 | 1243 |
| sl_q | Q4 [81.75, 99.0] | 10 | 3 | 30.0 | 10.8 | 0.19 | 1.9 | 1.17 | 223 |
| combo | side=long & fvg_present=fvg | 11 | 3 | 27.3 | 9.7 | 0.18 | 2.0 | 1.25 | 310 |

## Full tables

RVOL quartile edges: [0.17, 1.386, 2.361, 3.396, 6.54]; SL distance quartile edges (points): [0.75, 41.5, 63.5, 81.75, 99.0]

### side

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| long | 27 | 7 | 25.9 | 13.2 | 0.06 | 1.6 | 1.15 | 456 |
| short | 12 | 5 | 41.7 | 19.3 | 0.64 | 7.7 | 2.24 | 1361 |

### session

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| ASIA (small sample) | 8 | 1 | 12.5 | 2.2 | -0.51 | -4.1 | 0.45 | -642 |
| LON (small sample) | 1 | 0 | 0.0 | 0.0 | -1.01 | -1.0 | 0.00 | -146 |
| NY | 14 | 6 | 42.9 | 21.4 | 0.69 | 9.7 | 2.03 | 1414 |
| NY PM (small sample) | 7 | 3 | 42.9 | 15.8 | 0.98 | 6.9 | 3.80 | 1183 |
| OVERLAP (small sample) | 9 | 2 | 22.2 | 6.3 | -0.24 | -2.1 | 1.01 | 8 |

### hour

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.01 | -2.0 | 0.00 | -258 |
| 5 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.01 | -1.0 | 0.00 | -146 |
| 9 (small sample) | 3 | 1 | 33.3 | 6.1 | 0.30 | 0.9 | 1.36 | 129 |
| 10 (small sample) | 6 | 1 | 16.7 | 3.0 | -0.50 | -3.0 | 0.81 | -122 |
| 11 (small sample) | 7 | 4 | 57.1 | 25.0 | 1.28 | 8.9 | 4.29 | 1366 |
| 12 (small sample) | 5 | 1 | 20.0 | 3.6 | -0.25 | -1.2 | 0.74 | -197 |
| 13 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.99 | 2.0 | 2.23 | 246 |
| 14 (small sample) | 1 | 1 | 100.0 | 20.7 | 2.92 | 2.9 | - | 567 |
| 15 (small sample) | 5 | 2 | 40.0 | 11.8 | 1.01 | 5.1 | 2.90 | 679 |
| 16 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.09 | -1.1 | 0.00 | -64 |
| 19 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.99 | 2.0 | 2.68 | 332 |
| 21 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.03 | -1.0 | 0.00 | -203 |
| 22 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.01 | -1.0 | 0.00 | -179 |
| 23 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.01 | -2.0 | 0.00 | -333 |

### weekday

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Friday (small sample) | 6 | 4 | 66.7 | 30.0 | 1.99 | 11.9 | 5.87 | 1731 |
| Monday (small sample) | 4 | 2 | 50.0 | 15.0 | 0.99 | 4.0 | 3.09 | 660 |
| Sunday (small sample) | 1 | 0 | 0.0 | 0.0 | -1.01 | -1.0 | 0.00 | -179 |
| Thursday (small sample) | 7 | 2 | 28.6 | 8.2 | 0.01 | 0.0 | 1.20 | 132 |
| Tuesday | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.5 | 0.31 | -1240 |
| Wednesday (small sample) | 9 | 3 | 33.3 | 12.1 | 0.32 | 2.9 | 1.88 | 713 |

### score

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 4 | 33 | 8 | 24.2 | 12.8 | -0.08 | -2.8 | 1.02 | 86 |
| 5 (small sample) | 6 | 4 | 66.7 | 30.0 | 2.02 | 12.1 | 7.04 | 1731 |

### item_htf

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### item_zone (always 1: every signal is inside the OTE zone; not ranked)

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### item_rvol

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### item_cvd

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### item_bar

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### item_fvg

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|

### htf_bias

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| bear (small sample) | 8 | 2 | 25.0 | 7.1 | -0.03 | -0.2 | 1.11 | 91 |
| bull | 27 | 8 | 29.6 | 15.9 | 0.21 | 5.6 | 1.43 | 1243 |
| neutral (small sample) | 4 | 2 | 50.0 | 15.0 | 0.99 | 4.0 | 2.24 | 482 |

### rvol_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [0.17, 1.386] | 10 | 2 | 20.0 | 5.7 | -0.23 | -2.3 | 0.87 | -160 |
| Q2 [1.386, 2.361] (small sample) | 9 | 3 | 33.3 | 12.1 | 0.54 | 4.9 | 1.82 | 690 |
| Q3 [2.361, 3.396] | 10 | 5 | 50.0 | 23.7 | 0.99 | 9.9 | 2.54 | 1384 |
| Q4 [3.396, 6.54] | 10 | 2 | 20.0 | 5.7 | -0.31 | -3.1 | 0.91 | -97 |

### zone_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 0-0.33 (small sample) | 6 | 2 | 33.3 | 9.7 | 0.67 | 4.0 | 1.74 | 453 |
| 0.33-0.66 (small sample) | 4 | 1 | 25.0 | 4.6 | -0.06 | -0.2 | 1.34 | 144 |
| 0.66-1 (small sample) | 5 | 1 | 20.0 | 3.6 | -0.44 | -2.2 | 0.86 | -89 |
| <0 | 24 | 8 | 33.3 | 18.0 | 0.32 | 7.7 | 1.54 | 1309 |

### sl_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [0.75, 41.5] | 10 | 2 | 20.0 | 5.7 | -0.35 | -3.5 | 0.89 | -144 |
| Q2 [41.5, 63.5] | 10 | 4 | 40.0 | 16.8 | 0.80 | 8.0 | 2.75 | 1234 |
| Q3 [63.5, 81.75] (small sample) | 9 | 3 | 33.3 | 12.1 | 0.32 | 2.9 | 1.58 | 504 |
| Q4 [81.75, 99.0] | 10 | 3 | 30.0 | 10.8 | 0.19 | 1.9 | 1.17 | 223 |

### bos_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1-2 | 11 | 3 | 27.3 | 9.7 | -0.02 | -0.2 | 1.25 | 282 |
| 11+ | 10 | 4 | 40.0 | 16.8 | 0.57 | 5.7 | 2.25 | 1106 |
| 3-5 (small sample) | 9 | 2 | 22.2 | 6.3 | -0.13 | -1.2 | 0.74 | -343 |
| 6-10 (small sample) | 9 | 3 | 33.3 | 12.1 | 0.55 | 4.9 | 1.98 | 771 |

### month

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.04 | -3.1 | 0.00 | -430 |
| 2 (small sample) | 3 | 1 | 33.3 | 6.1 | 0.32 | 1.0 | 1.42 | 145 |
| 3 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.09 | -1.1 | 0.00 | -64 |
| 4 (small sample) | 4 | 1 | 25.0 | 4.6 | -0.02 | -0.1 | 0.82 | -100 |
| 5 (small sample) | 3 | 2 | 66.7 | 20.8 | 2.37 | 7.1 | 5.74 | 847 |
| 6 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.01 | -3.0 | 0.00 | -463 |
| 7 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.03 | -3.1 | 0.00 | -464 |
| 8 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.96 | 1.9 | 2.43 | 312 |
| 9 (small sample) | 9 | 4 | 44.4 | 18.9 | 0.75 | 6.8 | 2.44 | 1240 |
| 10 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.01 | -2.0 | 0.00 | -282 |
| 11 (small sample) | 5 | 3 | 60.0 | 23.1 | 1.37 | 6.8 | 5.67 | 1113 |
| 12 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.87 | -1.9 | 0.00 | -37 |

## How to read this

* Wilson LB is the lower end of the 95% confidence interval of the win rate. It penalises small samples, so 9/10 wins gives about 0.60 and 60/100 gives about 0.50.
* Open trades at the end of data and signals before the HTF EMAs are valid are excluded from every table here (counts in the headline).
* Groups with < 10 trades are marked small sample and excluded from rankings.
* Breakeven win rate at 3:R is 25.0% before costs and about 26.3% including commission and entry slippage (avg 0.050 R per trade; stop slippage not included). Win rate alone misleads: compare it to this and look at Avg R and PF.
* Ranking many groups and combinations will surface some winners by chance. Treat top combos as hypotheses to forward-test, not rules. Groups overlap (a trade appears in many groups), so they are not independent.
