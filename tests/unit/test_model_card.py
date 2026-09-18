"""Cards serializados (T-25)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPOS = {
    'nome',
    'versao',
    'dataset_version',
    'threshold',
    'hiperparametros',
    'metricas_teste',
    'semente',
    'timestamp',
    'pipeline_version',
}


def test_quatro_model_cards():
    base = ROOT / 'artifacts' / 'models'
    for nome in ('dummy_prior', 'baseline_regra', 'logistic_regression', 'random_forest'):
        card = json.loads((base / nome / 'model_card.json').read_text(encoding='utf-8'))
        assert CAMPOS <= set(card)
        assert card['nome'] == nome
        assert card['semente'] == 42
