# VOF-OTE backtest 5m

## Headline

* data_start: 2026-08-14 00:05:00-04:00
* data_end: 2026-10-23 16:55:00-04:00
* bars: 13584
* trades: 66
* wins: 18
* losses: 48
* win_rate: 0.2727272727272727
* net_pnl: -145.60000000000034
* profit_factor: 0.9819883121959911
* avg_r: 0.00015907283854793732
* expectancy: -2.206060606060611
* max_drawdown: 1764.9200000000003
* longest_losing_streak: 9
* trades_per_month: 28.698214285714286
* gross_profit: 7938.040000000001
* gross_loss: -8083.639999999999
* avg_win: 441.00222222222226
* avg_loss: -168.40916666666666
* open_trades: 0
* open_unrealized_pnl: 0.0
* htf_valid_from: 2026-08-14 00:05:00-04:00
* htf_excluded_bars: 0
* htf_excluded_signals: 0
* snapshot_dropped: 1

## Highest win rate circumstances (by Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| combo | rvol_q=Q2 [1.321, 1.486] & zone_bucket=<0 | 10 | 6 | 60.0 | 31.3 | 1.32 | 13.2 | 4.33 | 2227 |
| combo | score=4 & rvol_q=Q2 [1.321, 1.486] | 11 | 6 | 54.5 | 28.0 | 1.08 | 11.8 | 3.17 | 1820 |
| combo | score=4 & htf_bias=bull | 15 | 7 | 46.7 | 24.8 | 0.71 | 10.6 | 2.08 | 1534 |
| combo | fvg_present=no fvg & rvol_q=Q2 [1.321, 1.486] | 13 | 6 | 46.2 | 23.2 | 0.73 | 9.5 | 2.71 | 1828 |
| rvol_q | Q2 [1.321, 1.486] | 16 | 7 | 43.8 | 23.1 | 0.64 | 10.3 | 2.14 | 1624 |
| combo | session=LON & fvg_present=no fvg | 16 | 7 | 43.8 | 23.1 | 0.64 | 10.2 | 2.33 | 2029 |
| htf_bias | bull | 26 | 10 | 38.5 | 22.4 | 0.41 | 10.7 | 1.50 | 1461 |
| combo | session=LON & zone_bucket=<0 | 20 | 8 | 40.0 | 21.9 | 0.52 | 10.3 | 1.88 | 1912 |
| combo | htf_bias=bull & zone_bucket=<0 | 18 | 7 | 38.9 | 20.3 | 0.50 | 8.9 | 1.83 | 1670 |
| combo | session=LON & score=4 | 15 | 6 | 40.0 | 19.8 | 0.51 | 7.7 | 2.06 | 1693 |
| combo | session=ASIA & htf_bias=bull | 12 | 5 | 41.7 | 19.3 | 0.47 | 5.7 | 1.27 | 364 |
| combo | htf_bias=bull & fvg_present=no fvg | 19 | 7 | 36.8 | 19.1 | 0.34 | 6.5 | 1.47 | 1031 |
| combo | fvg_present=no fvg & zone_bucket=<0 | 34 | 11 | 32.4 | 19.1 | 0.23 | 8.0 | 1.33 | 1325 |
| session | LON | 23 | 8 | 34.8 | 18.8 | 0.30 | 7.0 | 1.59 | 1512 |
| zone_bucket | <0 | 52 | 15 | 28.8 | 18.3 | 0.10 | 5.4 | 1.14 | 902 |

## Worst circumstances (lowest Wilson lower bound, >= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| combo | session=ASIA & htf_bias=bear | 10 | 0 | 0.0 | -0.0 | -1.08 | -10.8 | 0.00 | -1573 |
| combo | side=short & session=ASIA | 14 | 1 | 7.1 | 1.3 | -0.88 | -12.3 | 0.02 | -2071 |
| combo | score=4 & htf_bias=neutral | 11 | 1 | 9.1 | 1.6 | -0.74 | -8.1 | 0.29 | -1203 |
| combo | side=long & rvol_q=Q1 [0.623, 1.321] | 10 | 1 | 10.0 | 1.8 | -0.64 | -6.4 | 0.31 | -1101 |
| combo | session=ASIA & zone_bucket=<0 | 19 | 2 | 10.5 | 2.9 | -0.62 | -11.7 | 0.34 | -1929 |
| combo | session=ASIA & fvg_present=no fvg | 19 | 2 | 10.5 | 2.9 | -0.72 | -13.7 | 0.19 | -2328 |
| rvol_q | Q1 [0.623, 1.321] | 17 | 2 | 11.8 | 3.3 | -0.57 | -9.7 | 0.30 | -1824 |
| combo | rvol_q=Q1 [0.623, 1.321] & zone_bucket=<0 | 16 | 2 | 12.5 | 3.5 | -0.54 | -8.6 | 0.33 | -1616 |
| sl_q | Q2 [16.188, 25.125] | 16 | 2 | 12.5 | 3.5 | -0.57 | -9.1 | 0.41 | -1573 |
| weekday | Monday | 14 | 2 | 14.3 | 4.0 | -0.49 | -6.9 | 0.33 | -1295 |

## Top by average R (>= 10 trades)

| Dimension | Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|---|
| combo | rvol_q=Q2 [1.321, 1.486] & zone_bucket=<0 | 10 | 6 | 60.0 | 31.3 | 1.32 | 13.2 | 4.33 | 2227 |
| combo | score=4 & rvol_q=Q2 [1.321, 1.486] | 11 | 6 | 54.5 | 28.0 | 1.08 | 11.8 | 3.17 | 1820 |
| combo | fvg_present=no fvg & rvol_q=Q2 [1.321, 1.486] | 13 | 6 | 46.2 | 23.2 | 0.73 | 9.5 | 2.71 | 1828 |
| combo | score=4 & htf_bias=bull | 15 | 7 | 46.7 | 24.8 | 0.71 | 10.6 | 2.08 | 1534 |
| rvol_q | Q2 [1.321, 1.486] | 16 | 7 | 43.8 | 23.1 | 0.64 | 10.3 | 2.14 | 1624 |
| combo | session=LON & fvg_present=no fvg | 16 | 7 | 43.8 | 23.1 | 0.64 | 10.2 | 2.33 | 2029 |
| combo | session=LON & zone_bucket=<0 | 20 | 8 | 40.0 | 21.9 | 0.52 | 10.3 | 1.88 | 1912 |
| combo | session=LON & score=4 | 15 | 6 | 40.0 | 19.8 | 0.51 | 7.7 | 2.06 | 1693 |
| combo | session=LON & htf_bias=bull | 10 | 4 | 40.0 | 16.8 | 0.51 | 5.1 | 1.97 | 1031 |
| combo | htf_bias=bull & zone_bucket=<0 | 18 | 7 | 38.9 | 20.3 | 0.50 | 8.9 | 1.83 | 1670 |
| combo | session=ASIA & htf_bias=bull | 12 | 5 | 41.7 | 19.3 | 0.47 | 5.7 | 1.27 | 364 |
| htf_bias | bull | 26 | 10 | 38.5 | 22.4 | 0.41 | 10.7 | 1.50 | 1461 |
| sl_q | Q4 [34.812, 81.5] | 17 | 6 | 35.3 | 17.3 | 0.39 | 6.6 | 1.63 | 971 |
| weekday | Tuesday | 13 | 5 | 38.5 | 17.7 | 0.37 | 4.8 | 1.61 | 731 |
| combo | htf_bias=bull & fvg_present=no fvg | 19 | 7 | 36.8 | 19.1 | 0.34 | 6.5 | 1.47 | 1031 |

## Full tables

RVOL quartile edges: [0.623, 1.321, 1.486, 1.939, 5.431]; SL distance quartile edges (points): [0.75, 16.188, 25.125, 34.812, 81.5]

### side

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| long | 38 | 11 | 28.9 | 17.0 | 0.09 | 3.5 | 1.10 | 489 |
| short | 28 | 7 | 25.0 | 12.7 | -0.12 | -3.5 | 0.81 | -635 |

### session

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| ASIA | 28 | 5 | 17.9 | 7.9 | -0.42 | -11.6 | 0.44 | -2178 |
| LON | 23 | 8 | 34.8 | 18.8 | 0.30 | 7.0 | 1.59 | 1512 |
| NY (small sample) | 2 | 1 | 50.0 | 9.5 | 0.93 | 1.9 | 2.11 | 156 |
| NY PM (small sample) | 3 | 1 | 33.3 | 6.1 | 0.37 | 1.1 | 0.86 | -55 |
| OVERLAP | 10 | 3 | 30.0 | 10.8 | 0.17 | 1.7 | 1.39 | 419 |

### hour

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 0 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.04 | -1.0 | 0.00 | -179 |
| 1 (small sample) | 6 | 1 | 16.7 | 3.0 | -0.38 | -2.3 | 0.17 | -751 |
| 3 (small sample) | 7 | 3 | 42.9 | 15.8 | 0.64 | 4.5 | 2.18 | 840 |
| 4 (small sample) | 3 | 1 | 33.3 | 6.1 | 0.31 | 0.9 | 1.51 | 184 |
| 5 (small sample) | 1 | 1 | 100.0 | 20.7 | 2.97 | 3.0 | - | 571 |
| 6 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.04 | -1.0 | 0.00 | -183 |
| 7 (small sample) | 5 | 2 | 40.0 | 11.8 | 0.49 | 2.4 | 1.67 | 375 |
| 8 (small sample) | 9 | 1 | 11.1 | 2.0 | -0.66 | -5.9 | 0.38 | -820 |
| 9 (small sample) | 6 | 2 | 33.3 | 9.7 | 0.33 | 2.0 | 2.02 | 536 |
| 10 (small sample) | 1 | 1 | 100.0 | 20.7 | 2.82 | 2.8 | - | 429 |
| 12 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.93 | 1.9 | 2.11 | 156 |
| 15 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.06 | -2.1 | 0.00 | -382 |
| 16 (small sample) | 1 | 1 | 100.0 | 20.7 | 3.24 | 3.2 | - | 327 |
| 19 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.15 | -3.4 | 0.00 | -434 |
| 20 | 12 | 4 | 33.3 | 13.8 | 0.14 | 1.6 | 1.07 | 107 |
| 21 (small sample) | 3 | 0 | 0.0 | 0.0 | -1.14 | -3.4 | 0.00 | -417 |
| 22 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.02 | -2.0 | 0.00 | -303 |
| 23 (small sample) | 1 | 0 | 0.0 | 0.0 | -1.05 | -1.0 | 0.00 | -201 |

### weekday

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Friday | 11 | 3 | 27.3 | 9.7 | 0.00 | 0.0 | 1.19 | 256 |
| Monday | 14 | 2 | 14.3 | 4.0 | -0.49 | -6.9 | 0.33 | -1295 |
| Sunday (small sample) | 3 | 1 | 33.3 | 6.1 | 0.14 | 0.4 | 1.31 | 126 |
| Thursday | 11 | 3 | 27.3 | 9.7 | 0.02 | 0.2 | 1.01 | 16 |
| Tuesday | 13 | 5 | 38.5 | 17.7 | 0.37 | 4.8 | 1.61 | 731 |
| Wednesday | 14 | 4 | 28.6 | 11.7 | 0.10 | 1.5 | 1.01 | 20 |

### score

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 4 | 46 | 13 | 28.3 | 17.3 | 0.03 | 1.6 | 1.01 | 65 |
| 5 | 18 | 5 | 27.8 | 12.5 | 0.03 | 0.5 | 1.07 | 161 |
| 6 (small sample) | 2 | 0 | 0.0 | 0.0 | -1.03 | -2.1 | 0.00 | -371 |

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
| bear | 28 | 6 | 21.4 | 10.2 | -0.20 | -5.5 | 0.74 | -892 |
| bull | 26 | 10 | 38.5 | 22.4 | 0.41 | 10.7 | 1.50 | 1461 |
| neutral | 12 | 2 | 16.7 | 4.7 | -0.43 | -5.1 | 0.58 | -715 |

### rvol_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [0.623, 1.321] | 17 | 2 | 11.8 | 3.3 | -0.57 | -9.7 | 0.30 | -1824 |
| Q2 [1.321, 1.486] | 16 | 7 | 43.8 | 23.1 | 0.64 | 10.3 | 2.14 | 1624 |
| Q3 [1.486, 1.939] | 16 | 4 | 25.0 | 10.2 | -0.11 | -1.8 | 0.95 | -98 |
| Q4 [1.939, 5.431] | 17 | 5 | 29.4 | 13.3 | 0.08 | 1.3 | 1.08 | 152 |

### zone_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 0-0.33 (small sample) | 8 | 1 | 12.5 | 2.2 | -0.61 | -4.9 | 0.39 | -813 |
| 0.33-0.66 (small sample) | 2 | 1 | 50.0 | 9.5 | 0.81 | 1.6 | 1.80 | 70 |
| 0.66-1 (small sample) | 4 | 1 | 25.0 | 4.6 | -0.53 | -2.1 | 0.10 | -305 |
| <0 | 52 | 15 | 28.8 | 18.3 | 0.10 | 5.4 | 1.14 | 902 |

### sl_q

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| Q1 [0.75, 16.188] | 17 | 5 | 29.4 | 13.3 | -0.06 | -1.0 | 0.89 | -214 |
| Q2 [16.188, 25.125] | 16 | 2 | 12.5 | 3.5 | -0.57 | -9.1 | 0.41 | -1573 |
| Q3 [25.125, 34.812] | 16 | 5 | 31.2 | 14.2 | 0.22 | 3.5 | 1.36 | 670 |
| Q4 [34.812, 81.5] | 17 | 6 | 35.3 | 17.3 | 0.39 | 6.6 | 1.63 | 971 |

### bos_bucket

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 1-2 | 20 | 6 | 30.0 | 14.5 | 0.15 | 3.0 | 1.23 | 538 |
| 11+ | 19 | 4 | 21.1 | 8.5 | -0.19 | -3.7 | 0.59 | -1059 |
| 3-5 | 15 | 5 | 33.3 | 15.2 | 0.12 | 1.9 | 1.33 | 527 |
| 6-10 | 12 | 3 | 25.0 | 8.9 | -0.10 | -1.2 | 0.90 | -152 |

### month

| Group | Trades | Wins | Win % | Wilson LB % | Avg R | Total R | PF | Net $ |
|---|---|---|---|---|---|---|---|---|
| 8 | 18 | 4 | 22.2 | 9.0 | -0.16 | -2.8 | 0.68 | -779 |
| 9 | 24 | 8 | 33.3 | 18.0 | 0.20 | 4.7 | 1.20 | 535 |
| 10 | 24 | 6 | 25.0 | 12.0 | -0.08 | -1.9 | 1.03 | 98 |

## How to read this

* Wilson LB is the lower end of the 95% confidence interval of the win rate. It penalises small samples, so 9/10 wins gives about 0.60 and 60/100 gives about 0.50.
* Open trades at the end of data and signals before the HTF EMAs are valid are excluded from every table here (counts in the headline).
* Groups with < 10 trades are marked small sample and excluded from rankings.
* Breakeven win rate at 3:R is 25.0% before costs and about 26.8% including commission and entry slippage (avg 0.073 R per trade; stop slippage not included). Win rate alone misleads: compare it to this and look at Avg R and PF.
* Ranking many groups and combinations will surface some winners by chance. Treat top combos as hypotheses to forward-test, not rules. Groups overlap (a trade appears in many groups), so they are not independent.
