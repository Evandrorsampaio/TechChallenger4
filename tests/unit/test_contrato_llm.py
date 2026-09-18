from lib.validacao import verificar_coerencia_numerica
from lib.ml.llm_contract import montar_payload, resposta_estruturada
from lib.ml.predict import SAFETY_NOTICE


def test_payload_tem_avisos():
    p = montar_payload({'prediction': 'habitual', 'probabilities': {'habitual': 0.7, 'alto_risco': 0.3}, 'threshold': 0.3}, 'normal')
    txt = resposta_estruturada(p)
    assert SAFETY_NOTICE in txt
    assert 'sintéticos' in p['aviso_dados_sinteticos'].lower() or 'sinteticos' in p['aviso_dados_sinteticos'].lower()


def test_divergencia_numerica_descarta():
    payload = {'prediction': 'habitual', 'probabilities': {'habitual': 0.9, 'alto_risco': 0.1}, 'threshold': 0.3}
    r = verificar_coerencia_numerica('A probabilidade de alto risco é 0.99', payload)
    assert r.aprovada is False
