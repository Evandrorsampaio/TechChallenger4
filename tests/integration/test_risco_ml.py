"""Caminhos de integração do workflow risco_ml (FakeChatModel, sem GPU)."""
from __future__ import annotations

from tests.conftest import CASO_OK
from lib.workflows.risco_ml import (
    _rota_modelo,
    _rota_regras,
    _rota_validacao,
    _rota_validacao_llm,
    build_risco_ml_workflow,
)


def test_rotas_puras():
    assert _rota_validacao({'erros_validacao': [{'campo': 'x'}]}) == 'erro_validacao'
    assert _rota_validacao({'campos_faltantes': ['idade']}) == 'dados_incompletos'
    assert _rota_validacao({}) == 'regras_seguranca'
    assert _rota_regras({'eh_emergencia': True}) == 'bypass_ml'
    assert _rota_regras({'eh_emergencia': False}) == 'executar_modelo_ml'
    assert _rota_modelo({'falha_modelo': 'x'}) == 'modo_degradado'
    assert _rota_modelo({}) == 'gerar_explicabilidade'
    assert _rota_validacao_llm({'texto_descartado': True}) == 'usar_resposta_estruturada'
    assert _rota_validacao_llm({}) == 'aplicar_avisos_seguranca'


def test_incompleto_sem_rag_e_uma_auditoria(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    incompleto = dict(CASO_OK)
    del incompleto['idade']
    state = wf.invoke({'dados_clinicos': incompleto, 'usuario': 'teste'})
    r = state['resposta_estruturada']
    assert r['modo'] == 'incompleto'
    assert 'idade' in r['campos_faltantes']
    assert r['fontes'] == []
    n = conn_tmp.execute('SELECT COUNT(*) AS c FROM predicoes_ml').fetchone()['c']
    assert n == 1
    row = conn_tmp.execute('SELECT modo, probabilidade FROM predicoes_ml').fetchone()
    assert row['modo'] == 'incompleto'
    assert row['probabilidade'] is None
    assert 'Resultado de apoio à decisão' in r['safety_notice']


def test_bypass_alarme_antes_do_ml(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    state = wf.invoke({
        'dados_clinicos': CASO_OK,
        'descricao_clinica': 'cefaleia intensa, escotomas e epigastralgia em barra',
        'usuario': 'teste',
    })
    r = state['resposta_estruturada']
    assert r['modo'] == 'bypass_regra'
    assert r['prediction'] == 'alto_risco'
    assert r['regras_disparadas']
    assert any('bypass' in x.lower() or 'emerg' in x.lower() for x in r['raciocinio'])


def test_degradado_usa_baseline(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    state = wf.invoke({
        'dados_clinicos': CASO_OK,
        'usuario': 'teste',
        'forcar_degradado': True,
    })
    r = state['resposta_estruturada']
    assert r['modo'] == 'degradado'
    assert 'degradado' in r['resposta_texto'].lower() or 'regra' in (r.get('explanation_method') or '')


def test_sucesso_grava_hash_e_avisos(conn_tmp, fake_chat, fake_retriever):
    wf = build_risco_ml_workflow(fake_chat, conn_tmp, fake_retriever)
    state = wf.invoke({'dados_clinicos': CASO_OK, 'usuario': 'teste'})
    r = state['resposta_estruturada']
    assert r['modo'] in {'normal', 'degradado'}  # degradado se modelo ausente no ambiente
    assert r['safety_notice']
    assert r['aviso_dados_sinteticos']
    row = conn_tmp.execute('SELECT features_hash, top_features FROM predicoes_ml').fetchone()
    assert row['features_hash']
    if row['top_features'] and row['top_features'] != '[]':
        assert '"value"' not in row['top_features']
