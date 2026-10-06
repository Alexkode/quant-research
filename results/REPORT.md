# Chronological quantitative research

Validation selected C=1, probability threshold=0.5. Selection used 2024 returns after 10 bps per side. All reported test metrics use 2025. Test ROC-AUC: 0.482; trade fraction: 56.3%.

| Strategy / cost | Total return | Sharpe (365) | Max drawdown |
|---|---:|---:|---:|
| fee_0_bps_each_side | -33.9% | -1.05 | -37.8% |
| fee_5_bps_each_side | -46.2% | -1.65 | -49.1% |
| fee_10_bps_each_side | -56.2% | -2.25 | -58.4% |
| fee_20_bps_each_side | -71.0% | -3.44 | -72.3% |
| always_long_intraday | -54.8% | -1.15 | -58.9% |
| momentum | -9.8% | -0.19 | -24.3% |
| cash | 0.0% | 0.00 | 0.0% |
| BTCUSDT | -56.0% | -2.66 | -58.6% |
| ETHUSDT | -57.8% | -1.66 | -60.1% |

Long/flat only, decision at previous close, entry next open, exit same close. Equal notional BTC/ETH sleeves; daily rebalance. Cost charged on both entry and exit. No leverage, funding or interest. Perfect fills and price availability are simplifying assumptions.

Every fold records training-label end and first test feature timestamp. Training labels precede test features. A future-price mutation test verifies causal features. Candidate comparisons and block bootstrap intervals are retained.

The study illustrates research discipline, not a deployable trading strategy. Short sample length, chosen assets, model selection, perfect fills, exchange-specific data and unstable regimes limit inference. Costs can erase any apparent edge. Cash and intraday long-only baselines are included.
