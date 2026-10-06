# Leakage-aware quantitative research

[![Verify project](https://github.com/Alexkode/quant-research/actions/workflows/verify.yml/badge.svg)](https://github.com/Alexkode/quant-research/actions/workflows/verify.yml)

Reproducible daily BTC/ETH research on official public Binance spot archives, 2022–2025. Downloaded ZIPs are checked against publisher SHA-256 checksums. Millisecond and microsecond timestamps are handled explicitly.

## Run

```sh
python -m pip install -r requirements.txt
python -m quant_lab.download
python -m pytest -q
python -m quant_lab.research
PYTHONPATH=. python scripts/report.py
```

No account, credentials or order placement. Raw archives are excluded; [download manifest](results/manifest.json) retains URLs and hashes.

## Protocol

Features use information available at a day's close. A long/flat position enters the next day's open and exits that day's close. Logistic regression and standardization are refit monthly on a rolling year, with training label times strictly before test feature times. Hyperparameters and trading threshold are selected on 2024 and frozen for 2025. Both entry and exit incur costs. Long-only positions avoid pretending that spot shorts are freely available.

Report total return, annualized Sharpe, drawdown, AUC, trade fraction, 7-day block bootstrap confidence intervals, per-asset results, and costs of 0/5/10/20 bps per side. Compare cash, intraday long and momentum baselines. See [measured report](results/REPORT.md), [equity](results/equity.png) and [every test prediction](results/test-predictions.csv).

An unfavorable test result is retained. The experiment is a portfolio demonstration of chronology and validation, not investment advice or evidence of a durable trading edge. It assumes perfect open/close fills and does not model exchange outages or capacity.

Code developed with AI assistance. Data source and usage terms: [Binance public data](https://github.com/binance/binance-public-data).

## Installation and verification

Clone this repository and run commands from its root. Each repository has its own dependencies and tests.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash scripts/verify.sh
```

GitHub Actions checks the code contracts and the consistency of published experimental records. It does not rerun training or cluster benchmarks. See [experiment provenance](ENVIRONMENT.md) and [measured report](results/REPORT.md).
