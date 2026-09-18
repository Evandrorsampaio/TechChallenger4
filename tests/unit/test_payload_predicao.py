"""Contrato do payload de inferência (T-26)."""
from lib.ml.predict import prever
from tests.conftest import CASO_OK


def test_payload_predicao_campos_obrigatorios():
    out = prever(CASO_OK, nome_modelo='logistic_regression')
    for chave in (
        'prediction',
        'probabilities',
        'threshold',
        'dados_imputados',
        'model_name',
        'model_version',
        'dataset_version',
        'safety_notice',
        'aviso_dados_sinteticos',
        'features_hash',
    ):
        assert chave in out
    p = out['probabilities']
    assert abs(p['habitual'] + p['alto_risco'] - 1.0) < 1e-6
    assert (out['prediction'] == 'alto_risco') == (p['alto_risco'] >= out['threshold'] - 1e-12)
