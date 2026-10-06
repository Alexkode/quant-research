import json
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from quant_lab.research import daily_returns
r=json.loads(Path('results/research.json').read_text());p=pd.read_csv('results/test-predictions.csv',parse_dates=['target_date']);fig,ax=plt.subplots(figsize=(9,4))
for fee in [0,5,10,20]:
    x=daily_returns(p,r['selected']['threshold'],fee);ax.plot(x.index,np.cumprod(1+x),label=f'{fee} bps/side')
ax.set(title='2025 frozen-policy chronological test',ylabel='Portfolio value, initial 1');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig('results/equity.png',dpi=160)
lines=['# Chronological quantitative research','',f"Validation selected C={r['selected']['c']}, probability threshold={r['selected']['threshold']}. Selection used 2024 returns after 10 bps per side. All reported test metrics use 2025. Test ROC-AUC: {r['test_auc']:.3f}; trade fraction: {r['test_trade_fraction']:.1%}.",'',
       '| Strategy / cost | Total return | Sharpe (365) | Max drawdown |','|---|---:|---:|---:|']
for name,m in r['results'].items():lines.append(f"| {name} | {m['total_return']:.1%} | {m['sharpe_365']:.2f} | {m['max_drawdown']:.1%} |")
lines+=['',r['execution'],'','Every fold records training-label end and first test feature timestamp. Training labels precede test features. A future-price mutation test verifies causal features. Candidate comparisons and block bootstrap intervals are retained.','',
        'The study illustrates research discipline, not a deployable trading strategy. Short sample length, chosen assets, model selection, perfect fills, exchange-specific data and unstable regimes limit inference. Costs can erase any apparent edge. Cash and intraday long-only baselines are included.']
Path('results/REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines[:8]))
