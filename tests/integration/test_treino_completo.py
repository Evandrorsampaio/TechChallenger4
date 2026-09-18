"""T-20/T-27: modelos serializados existem (treino completo não é reexecutado na suíte rápida)."""
from lib.ml.registry import pasta_modelo


def test_quatro_pipelines_no_disco():
    for nome in ('dummy_prior', 'baseline_regra', 'logistic_regression', 'random_forest'):
        assert (pasta_modelo(nome) / 'modelo.joblib').exists()
        assert (pasta_modelo(nome) / 'model_card.json').exists()
