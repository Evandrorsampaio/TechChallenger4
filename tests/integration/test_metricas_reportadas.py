"""Métricas persistidas batem com o contrato de evaluate (T-21/T-28)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAVES = {
    'recall_positivo',
    'precision_positivo',
    'pr_auc',
    'roc_auc',
    'f1_macro',
    'brier',
    'acuracia',
    'matriz_confusao',
    'limiar',
}


def test_metricas_quatro_modelos_no_teste():
    dest = ROOT / 'artifacts' / 'metrics'
    for nome in ('dummy_prior', 'baseline_regra', 'logistic_regression', 'random_forest'):
        data = json.loads((dest / f'{nome}_teste.json').read_text(encoding='utf-8'))
        assert CHAVES <= set(data)
        assert data['modelo'] == nome
        assert data['split'] == 'teste'


def test_comparacao_tem_bootstrap_quando_completa():
    path = ROOT / 'artifacts' / 'metrics' / 'comparacao.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert 'logistic_regression' in data
    bloco = data['logistic_regression']
    assert 'bootstrap_teste' in bloco
    ic = bloco['bootstrap_teste']['pr_auc']
    assert ic['ic95_low'] <= ic['ponto'] <= ic['ic95_high']
