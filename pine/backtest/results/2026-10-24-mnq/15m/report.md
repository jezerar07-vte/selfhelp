# VOF-OTE backtest 15m

## Headline

* data_start: 2026-08-14 00:00:00-04:00
* data_end: 2026-10-23 16:45:00-04:00
* bars: 4554
* trades: 17
* wins: 3
* losses: 14
* win_rate: 0.17647058823529413
* net_pnl: -1180.9399999999998
* profit_factor: 0.4665215073678885
* avg_r: -0.33798809189057205
* expectancy: -69.4670588235294
* max_drawdown: 1654.08
* longest_losing_streak: 10
* trades_per_month: 7.391964285714286
* gross_profit: 1032.72
* gross_loss: -2213.66
* avg_win: 344.24
* avg_loss: -158.1185714285714
* open_trades: 0
* open_unrealized_pnl: 0.0
* htf_valid_from: 2026-08-14 00:00:00-04:00
* htf_excluded_bars: 0
* htf_excluded_signals: 0
* snapshot_dropped: 1
* LOW CONFIDENCE: fewer than 30 trades

## Highest win rate circumstances (by Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| score | 4 | 14 | 3 | 21.4 | 7.6 | -0.19 | -2.6 | 0.60 | -698 |
| combo | score=4 & zone_bucket=<0 | 10 | 1 | 10.0 | 1.8 | -0.63 | -6.3 | 0.29 | -978 |
| zone_bucket | <0 | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.4 | 0.24 | -1256 |

## Worst circumstances (lowest Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| zone_bucket | <0 | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.4 | 0.24 | -1256 |
| combo | score=4 & zone_bucket=<0 | 10 | 1 | 10.0 | 1.8 | -0.63 | -6.3 | 0.29 | -978 |
| score | 4 | 14 | 3 | 21.4 | 7.6 | -0.19 | -2.6 | 0.60 | -698 |

## Top by average R (>= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| score | 4 | 14 | 3 | 21.4 | 7.6 | -0.19 | -2.6 | 0.60 | -698 |
| combo | score=4 & zone_bucket=<0 | 10 | 1 | 10.0 | 1.8 | -0.63 | -6.3 | 0.29 | -978 |
| zone_bucket | <0 | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.4 | 0.24 | -1256 |

## Full tables

RVOL quartile edges: [0.358, 1.28, 1.413, 1.737, 3.137]; SL distance quartile edges (points): [5.25, 25.75, 34.0, 50.75, 75.75]

### side

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| long (small sample) | 9 | 2 | 22.2 | 6.3 | -0.17 | -1.5 | 0.55 | -526 |
| short (small sample) | 8 | 1 | 12.5 | 2.2 | -0.53 | -4.3 | 0.38 | -655 |

### session

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| ASIA (small sample) | 5 | 2 | 40.0 | 11.8 | 0.46 | 2.3 | 1.52 | 249 |
| LON (small sample) | 6 | 0 | 0.0 | 0.0 | -1.03 | -6.2 | 0.00 | -1037 |
| NY (small sample) | 1 | 0 | 0.0 | 0.0 | -1.02 | -1.0 | 0.00 | -162 |
| OVERLAP (small sample) | 5 | 1 | 20.0 | 3.6 | -0.17 | -0.8 | 0.57 | -230 |

### hour

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.03 | -1.0 | 0.00 | -188 |
| 3 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.02 | -3.1 | 0.00 | -450 |
| 4 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.03 | -2.1 | 0.00 | -382 |
| 7 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.06 | -1.1 | 0.00 | -205 |
| 8 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.02 | -3.1 | 0.00 | -387 |
| 10 (small sample) | 2 | 1 | 50.0 | 9.5 | 1.11 | 2.2 | 2.04 | 157 |
| 11 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.02 | -1.0 | 0.00 | -162 |
| 19 (small sample) | 1 | 1 | 100.0 | 20.7 | 2.90 | 2.9 | - | 403 |
| 21 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.04 | -1.0 | 0.00 | -187 |
| 22 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.73 | 1.5 | 3.19 | 221 |

### weekday

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Friday (small sample) | 2 | 0 | 0.0 | 0.0 | -1.02 | -2.0 | 0.00 | -328 |
| Monday (small sample) | 4 | 1 | 25.0 | 4.6 | -0.04 | -0.2 | 0.95 | -22 |
| Sunday (small sample) | 1 | 1 | 100.0 | 20.7 | 2.48 | 2.5 | - | 323 |
| Thursday (small sample) | 3 | 0 | 0.0 | 0.0 | -1.02 | -3.1 | 0.00 | -409 |
| Wednesday (small sample) | 7 | 1 | 14.3 | 2.6 | -0.42 | -2.9 | 0.29 | -743 |

### score

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 4 | 14 | 3 | 21.4 | 7.6 | -0.19 | -2.6 | 0.60 | -698 |
| 5 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.04 | -3.1 | 0.00 | -483 |

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
| bear (small sample) | 9 | 2 | 22.2 | 6.3 | -0.20 | -1.8 | 0.67 | -359 |
| bull (small sample) | 5 | 0 | 0.0 | -0.0 | -1.03 | -5.1 | 0.00 | -843 |
| neutral (small sample) | 3 | 1 | 33.3 | 6.1 | 0.40 | 1.2 | 1.07 | 21 |

### rvol_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [0.358, 1.28] (small sample) | 4 | 1 | 25.0 | 4.6 | -0.04 | -0.2 | 0.86 | -65 |
| Q2 [1.28, 1.413] (small sample) | 4 | 0 | 0.0 | 0.0 | -1.03 | -4.1 | 0.00 | -639 |
| Q3 [1.413, 1.737] (small sample) | 4 | 0 | 0.0 | 0.0 | -1.04 | -4.1 | 0.00 | -731 |
| Q4 [1.737, 3.137] (small sample) | 5 | 2 | 40.0 | 11.8 | 0.54 | 2.7 | 1.68 | 254 |

### zone_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 0-0.33 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.05 | -2.1 | 0.00 | -393 |
| 0.33-0.66 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.02 | -1.0 | 0.00 | -162 |
| 0.66-1 (small sample) | 2 | 2 | 100.0 | 34.2 | 2.86 | 5.7 | - | 630 |
| <0 | 12 | 1 | 8.3 | 1.5 | -0.70 | -8.4 | 0.24 | -1256 |

### sl_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [5.25, 25.75] (small sample) | 5 | 2 | 40.0 | 11.8 | 0.52 | 2.6 | 1.14 | 77 |
| Q2 [25.75, 34.0] (small sample) | 4 | 1 | 25.0 | 4.6 | -0.05 | -0.2 | 0.71 | -168 |
| Q3 [34.0, 50.75] (small sample) | 4 | 0 | 0.0 | 0.0 | -1.02 | -4.1 | 0.00 | -613 |
| Q4 [50.75, 75.75] (small sample) | 4 | 0 | 0.0 | 0.0 | -1.02 | -4.1 | 0.00 | -477 |

### bos_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1-2 (small sample) | 4 | 0 | 0.0 | 0.0 | -1.04 | -4.1 | 0.00 | -671 |
| 11+ (small sample) | 2 | 0 | 0.0 | 0.0 | -1.03 | -2.1 | 0.00 | -338 |
| 3-5 (small sample) | 4 | 1 | 25.0 | 4.6 | 0.04 | 0.2 | 0.59 | -216 |
| 6-10 (small sample) | 7 | 2 | 28.6 | 8.2 | 0.04 | 0.3 | 1.06 | 44 |

### month

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 8 (small sample) | 5 | 2 | 40.0 | 11.8 | 0.52 | 2.6 | 1.16 | 85 |
| 9 (small sample) | 7 | 0 | 0.0 | 0.0 | -1.03 | -7.2 | 0.00 | -1140 |
| 10 (small sample) | 5 | 1 | 20.0 | 3.6 | -0.23 | -1.2 | 0.76 | -127 |

## How to read this

* Wilson LB is the lower end of the 95% confidence interval of the win rate. It penalises small samples, so 9/10 wins gives about 0.60 and 60/100 gives about 0.50.
* Open trades at the end of data and signals before the HTF EMAs are valid are excluded from every table here (counts in the headline).
* Groups with < 10 trades are marked small sample and excluded from rankings.
* Breakeven win rate at 3:R is 25.0% before costs and about 26.0% including commission and entry slippage (avg 0.042 R per trade; stop slippage not included). Win rate alone misleads: compare it to this and look at Avg R and PF.
* Ranking many groups and combinations will surface some winners by chance. Treat top combos as hypotheses to forward-test, not rules. Groups overlap (a trade appears in many groups), so they are not independent.
