"""Validate the configurations in the published experimental records."""
import json
from pathlib import Path
from datetime import datetime

root = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads(path.read_text())

quant=read(root/'results/research.json')
assert quant['validation_period']==2024 and quant['test_period']==2025
for fold in quant['folds']:
    assert datetime.fromisoformat(fold['train_label_end'])<datetime.fromisoformat(fold['first_test_feature_time'])

print('Published evidence checks passed for quant-research.')
