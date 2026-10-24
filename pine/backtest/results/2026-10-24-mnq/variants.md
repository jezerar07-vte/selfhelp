# Variant comparison (same data as comparison.md)

MNQ, $200 risk, 1:3, $0.62/side + 1 tick slippage. "Asia off" disables the 19:00-02:00 NY session window only. Raising min score changes which legs get consumed, so score>=5 is a different trade set, not a subset of score>=4.

Asia off was chosen after seeing these same results (in-sample), so its improvement is not independent evidence. Breakeven win rate at 1:3 after costs is about 25| TF | Variant | Trades | Win % | Wilson LB % | PF | Avg R | Net $ | Max DD $ | Worst streak |
|---|---|---|---|---|---|---|---|---|---|
| 1h | score>=4, all sessions (baseline) | 39 | 30.8 | 18.6 | 1.44 | +0.24 | +1,817 | 1,185 | 7 |
| 1h | score>=4, Asia off | 32 | 34.4 | 20.4 | 1.74 | +0.39 | +2,295 | 765 | 4 |
| 1h | score>=5, all sessions | 9 | 44.4 | 18.9 | 2.44 | +1.00 | +1,189 | 493 | 3 |
| 1h | score>=5, Asia off | 9 | 44.4 | 18.9 | 2.44 | +1.00 | +1,189 | 493 | 3 |
| 5m | score>=4, all sessions (baseline) | 66 | 27.3 | 18.0 | 0.98 | +0.00 | -146 | 1,765 | 9 |
| 5m | score>=4, Asia off | 38 | 34.2 | 21.2 | 1.49 | +0.31 | +2,032 | 738 | 5 |
| 5m | score>=5, all sessions | 24 | 25.0 | 12.0 | 0.94 | -0.08 | -173 | 1,372 | 8 |
| 5m | score>=5, Asia off | 13 | 30.8 | 12.7 | 1.26 | +0.15 | +380 | 637 | 4 |
| 15m | score>=4, all sessions (baseline) | 17 | 17.6 | 6.2 | 0.47 | -0.34 | -1,181 | 1,654 | 10 |
| 15m | score>=4, Asia off | 13 | 7.7 | 1.4 | 0.16 | -0.70 | -1,638 | 1,638 | 10 |
| 15m | score>=5, all sessions | 4 | 0.0 | 0.0 | 0.0 | -1.03 | -680 | 680 | 4 |
| 15m | score>=5, Asia off | 4 | 0.0 | 0.0 | 0.0 | -1.03 | -680 | 680 | 4 |
