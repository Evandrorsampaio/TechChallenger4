"""e2e dos 4 cenários via workflow compilado."""
from __future__ import annotations

from tests.conftest import CASO_OK
from lib.workflows.risco_ml import build_risco_ml_workflow


def test_fluxo_completo_normal_ou_degradado(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    r = wf.invoke({'dados_clinicos': CASO_OK})['resposta_estruturada']
    assert r['modo'] in {'normal', 'degradado'}
    assert r['safety_notice'] and r['aviso_dados_sinteticos']


def test_fluxo_dados_incompletos(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    dados = {k: v for k, v in CASO_OK.items() if k != 'imc_pre_gestacional'}
    r = wf.invoke({'dados_clinicos': dados})['resposta_estruturada']
    assert r['requer_intervencao_humana']
    assert 'imc_pre_gestacional' in r['campos_faltantes']
