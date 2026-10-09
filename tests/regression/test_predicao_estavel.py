"""Regressão: mesma entrada → mesma predição (T-26)."""
from lib.ml.predict import prever
from tests.conftest import CASO_OK


def test_predicao_estavel_duas_chamadas():
    a = prever(CASO_OK, nome_modelo='logistic_regression')
    b = prever(CASO_OK, nome_modelo='logistic_regression')
    assert a['prediction'] == b['prediction']
    assert a['probabilities'] == b['probabilities']
    assert a['features_hash'] == b['features_hash']
    assert a['threshold'] == b['threshold']
