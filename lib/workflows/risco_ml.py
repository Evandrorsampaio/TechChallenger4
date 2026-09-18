"""Workflow de inferência de risco gestacional (ML + regras + RAG + LLM).

16 nós, 4 rotas condicionais. Um único nó usa LLM (síntese somente-leitura).
"""
from __future__ import annotations

import json
from typing import Literal, TypedDict

try:
    import langchain as _lc

    if not hasattr(_lc, 'debug'):
        _lc.debug = False
    if not hasattr(_lc, 'verbose'):
        _lc.verbose = False
except Exception:
    pass

from lib.config import ml_risco_habilitado
from lib.ml.baseline import criterios_disparados
from lib.ml.explain import explicar
from lib.ml.llm_contract import montar_payload, prompt_sintese, resposta_estruturada
from lib.ml.predict import (
    AVISO_SINTETICO,
    SAFETY_NOTICE,
    ModeloIndisponivelError,
    features_hash,
    prever,
)
from lib.ml.registry import carregar_modelo, pasta_modelo
from lib.ml.schema import DadosIncompletosError, DominioInvalidoError, GestanteFeatures, parse_gestante
from lib.observabilidade import no_evento, novo_correlation_id
from lib.validacao import verificar_coerencia_numerica
from lib.workflows import common
from lib.workflows.obstetrico import SINAIS_ALARME_OBST, _detectar_alertas_urgencia

ModoExecucao = Literal['normal', 'degradado', 'bypass_regra', 'incompleto']

MODELO_PADRAO = 'logistic_regression'

TERMO_CLINICO = {
    'alto_risco': 'pré-natal de alto risco estratificação gestacional encaminhamento',
    'habitual': 'pré-natal de risco habitual acompanhamento obstétrico MS',
    'bypass_regra': 'emergência obstétrica pré-eclâmpsia sinais de alarme encaminhamento imediato',
    'degradado': 'pré-natal alto risco critérios Ministério da Saúde FEBRASGO',
}


class RiscoMLState(TypedDict, total=False):
    dados_clinicos: dict
    paciente_id: int | None
    usuario: str
    descricao_clinica: str | None
    publico: Literal['clinico', 'tecnico']
    features: GestanteFeatures | None
    campos_faltantes: list[str]
    erros_validacao: list[dict]
    regras_disparadas: list[str]
    eh_emergencia: bool
    resultado_predicao: dict | None
    dados_imputados: list[str]
    falha_modelo: str | None
    resultado_explicacao: dict | None
    fontes: list[dict]
    fontes_sem_filtro: bool
    falha_rag: str | None
    payload_llm: dict
    variante_prompt: str
    texto_llm: str
    falha_llm: str | None
    verificacao: object
    texto_descartado: bool
    resposta_texto: str
    requer_intervencao_humana: bool
    intervencao: dict
    decisao_humana: dict | None
    modo: ModoExecucao
    correlation_id: str
    falhas: list[dict]
    raciocinio: list[str]
    auditoria_id: int | None
    auditoria_falhou: bool
    resposta_estruturada: dict
    nome_modelo: str
    forcar_degradado: bool


def _append(state: RiscoMLState, linha: str) -> list[str]:
    return list(state.get('raciocinio') or []) + [linha]


def _top_auditoria(tops: list[dict]) -> list[dict]:
    return [
        {
            'feature': t.get('feature'),
            'direction': t.get('direction'),
            'contribution': t.get('contribution'),
        }
        for t in (tops or [])
    ]


def validar_dados(state: RiscoMLState) -> dict:
    cid = state.get('correlation_id') or novo_correlation_id()
    with no_evento('validar_dados', cid):
        dados = dict(state.get('dados_clinicos') or {})
        extra = (state.get('decisao_humana') or {}).get('dados') or {}
        dados.update(extra)
        try:
            feat = parse_gestante(dados)
        except DadosIncompletosError as exc:
            return {
                'correlation_id': cid,
                'dados_clinicos': dados,
                'features': None,
                'campos_faltantes': exc.campos_faltantes,
                'erros_validacao': [],
                'raciocinio': _append(state, f'Dados incompletos: {exc.campos_faltantes}'),
            }
        except DominioInvalidoError as exc:
            return {
                'correlation_id': cid,
                'dados_clinicos': dados,
                'features': None,
                'campos_faltantes': [],
                'erros_validacao': [
                    {
                        'campo': exc.campo,
                        'valor_recebido': exc.valor,
                        'faixa': exc.faixa,
                        'mensagem': str(exc),
                    }
                ],
                'raciocinio': _append(state, f'Erro de domínio: {exc}'),
            }
        return {
            'correlation_id': cid,
            'dados_clinicos': dados,
            'features': feat,
            'campos_faltantes': [],
            'erros_validacao': [],
            'raciocinio': _append(state, 'Validação de contrato ok (24 features).'),
        }


def _rota_validacao(state: RiscoMLState) -> str:
    if state.get('erros_validacao'):
        return 'erro_validacao'
    if state.get('campos_faltantes'):
        return 'dados_incompletos'
    return 'regras_seguranca'


def erro_validacao(state: RiscoMLState) -> dict:
    payload = montar_payload(
        {
            'prediction': 'incompleto',
            'model_name': 'nenhum',
            'model_version': 'n/a',
            'dataset_version': 'v1.0.0',
            'features_hash': '',
        },
        'incompleto',
    )
    return {
        'modo': 'incompleto',
        'payload_llm': payload,
        'requer_intervencao_humana': False,
        'raciocinio': _append(state, 'Caminho erro_validacao.'),
    }


def dados_incompletos(state: RiscoMLState) -> dict:
    return {
        'modo': 'incompleto',
        'raciocinio': _append(state, 'Caminho dados_incompletos (sem imputação, sem RAG).'),
    }


def solicitar_complemento(state: RiscoMLState) -> dict:
    faltantes = state.get('campos_faltantes') or []
    payload = montar_payload(
        {
            'prediction': 'incompleto',
            'model_name': 'nenhum',
            'model_version': 'n/a',
            'dataset_version': 'v1.0.0',
            'features_hash': '',
            'campos_faltantes': faltantes,
        },
        'incompleto',
    )
    return {
        'payload_llm': payload,
        'requer_intervencao_humana': True,
        'intervencao': {
            'tipo': 'complemento_obrigatorio',
            'campos': faltantes,
            'pergunta': (
                'Campos obrigatórios ausentes: '
                + ', '.join(faltantes)
                + '. Completar os dados e resubmeter. Valores obrigatórios não são imputados.'
            ),
            'opcoes': None,
        },
        'raciocinio': _append(state, 'Human-in-the-loop: solicitar complemento.'),
    }


def regras_seguranca(state: RiscoMLState) -> dict:
    cid = state.get('correlation_id') or ''
    with no_evento('regras_seguranca', cid):
        desc = state.get('descricao_clinica') or ''
        mini = {'descricao_caso': desc, 'ig_semanas': None, 'raciocinio': []}
        feat = state.get('features')
        if feat is not None:
            mini['ig_semanas'] = feat.ig_semanas
        det = _detectar_alertas_urgencia(mini)
        regras = list(det.get('alertas_urgencia') or [])
        return {
            'regras_disparadas': regras,
            'eh_emergencia': bool(det.get('eh_emergencia')),
            'raciocinio': _append(
                state,
                f'Regras SINAIS_ALARME_OBST: {len(regras)} disparo(s).',
            ),
        }


def _rota_regras(state: RiscoMLState) -> str:
    return 'bypass_ml' if state.get('eh_emergencia') else 'executar_modelo_ml'


def bypass_ml(state: RiscoMLState) -> dict:
    feat = state.get('features')
    payload = {
        'model_name': 'regra_alarme',
        'model_version': '1.0.0',
        'dataset_version': 'v1.0.0',
        'prediction': 'alto_risco',
        'threshold': None,
        'probabilities': None,
        'dados_imputados': feat.campos_imputaveis_ausentes() if feat else [],
        'features_hash': features_hash(feat) if feat else '',
        'safety_notice': SAFETY_NOTICE,
        'aviso_dados_sinteticos': AVISO_SINTETICO,
    }
    return {
        'modo': 'bypass_regra',
        'resultado_predicao': payload,
        'dados_imputados': payload['dados_imputados'],
        'resultado_explicacao': {
            'explanation_method': None,
            'explanation_scope': None,
            'top_features': [],
            'aviso': 'Predição não executada: encaminhamento imediato por regra de alarme.',
        },
        'raciocinio': _append(state, 'bypass_ml: emergência obstétrica, ML não executado.'),
    }


def executar_modelo_ml(state: RiscoMLState) -> dict:
    cid = state.get('correlation_id') or ''
    with no_evento('executar_modelo_ml', cid):
        if state.get('forcar_degradado'):
            return {
                'falha_modelo': 'forcado',
                'raciocinio': _append(state, 'Falha forçada para modo degradado (demo/teste).'),
            }
        feat = state['features']
        nome = state.get('nome_modelo') or MODELO_PADRAO
        try:
            pred = prever(feat, nome_modelo=nome)
        except ModeloIndisponivelError as exc:
            return {
                'falha_modelo': str(exc),
                'raciocinio': _append(state, f'Modelo indisponível: {exc}'),
            }
        except Exception as exc:  # noqa: BLE001 — degradar, não explodir
            return {
                'falha_modelo': str(exc),
                'raciocinio': _append(state, f'Falha de inferência: {exc}'),
            }
        return {
            'modo': 'normal',
            'falha_modelo': None,
            'resultado_predicao': pred,
            'dados_imputados': pred.get('dados_imputados') or [],
            'raciocinio': _append(
                state,
                f"ML {pred['model_name']}: {pred['prediction']} "
                f"P={pred['probabilities']['alto_risco']} limiar={pred['threshold']}",
            ),
        }


def _rota_modelo(state: RiscoMLState) -> str:
    return 'modo_degradado' if state.get('falha_modelo') else 'gerar_explicabilidade'


def modo_degradado(state: RiscoMLState) -> dict:
    feat = state['features']
    hits = criterios_disparados(feat.para_registro())
    rotulo = 'alto_risco' if hits else 'habitual'
    payload = {
        'model_name': 'baseline_regra',
        'model_version': '1.0.0',
        'dataset_version': 'v1.0.0',
        'prediction': rotulo,
        'threshold': None,
        'probabilities': None,
        'dados_imputados': feat.campos_imputaveis_ausentes(),
        'features_hash': features_hash(feat),
        'safety_notice': SAFETY_NOTICE,
        'aviso_dados_sinteticos': AVISO_SINTETICO,
        'criterios_disparados': hits,
    }
    return {
        'modo': 'degradado',
        'resultado_predicao': payload,
        'dados_imputados': payload['dados_imputados'],
        'resultado_explicacao': {
            'explanation_method': 'regra_deterministica',
            'explanation_scope': 'global',
            'top_features': [],
            'aviso': (
                'Modo degradado: o modelo supervisionado não estava disponível. '
                'Classificação pela disjunção de CRITERIOS_ALTO_RISCO.'
            ),
        },
        'raciocinio': _append(state, f'modo_degradado → {rotulo}; critérios={hits}'),
    }


def gerar_explicabilidade(state: RiscoMLState) -> dict:
    if state.get('modo') in {'bypass_regra', 'degradado'}:
        return {}
    feat = state['features']
    nome = (state.get('resultado_predicao') or {}).get('model_name') or MODELO_PADRAO
    try:
        est = carregar_modelo(pasta_modelo(nome))
        exp = explicar(est, feat)
    except Exception as exc:  # noqa: BLE001
        exp = {
            'explanation_method': 'indisponivel',
            'explanation_scope': None,
            'top_features': [],
            'aviso': f'Explicabilidade indisponível ({exc}).',
        }
    pred = dict(state.get('resultado_predicao') or {})
    pred['explanation_method'] = exp.get('explanation_method')
    pred['explanation_scope'] = exp.get('explanation_scope')
    pred['top_features'] = exp.get('top_features') or []
    return {
        'resultado_explicacao': exp,
        'resultado_predicao': pred,
        'raciocinio': _append(state, f"Explicação: {exp.get('explanation_method')}."),
    }


def recuperar_protocolos_rag(retriever):
    def node(state: RiscoMLState) -> dict:
        if state.get('modo') == 'incompleto':
            return {'fontes': [], 'falha_rag': None}
        modo = state.get('modo') or 'normal'
        pred = (state.get('resultado_predicao') or {}).get('prediction', 'habitual')
        query = TERMO_CLINICO.get(modo) or TERMO_CLINICO.get(pred, TERMO_CLINICO['habitual'])
        feat = state.get('features')
        if feat is not None:
            extras = []
            if feat.has_cronica:
                extras.append('hipertensão gestacional')
            if feat.diabetes_previo:
                extras.append('diabetes mellitus gestacional')
            if extras:
                query = query + ' ' + ' '.join(extras)
        try:
            fontes = common.rag_search(retriever, query, categoria='ginecologia_obstetricia', k=4)
            return {
                'fontes': fontes,
                'falha_rag': None,
                'fontes_sem_filtro': False,
                'raciocinio': _append(state, f'RAG: {len(fontes)} trecho(s) para query clínica.'),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                'fontes': [],
                'falha_rag': str(exc),
                'raciocinio': _append(state, f'RAG indisponível: {exc}'),
            }
    return node


def sintetizar_com_llm(chat_model):
    def node(state: RiscoMLState) -> dict:
        pred = dict(state.get('resultado_predicao') or {})
        exp = state.get('resultado_explicacao') or {}
        pred.setdefault('explanation_method', exp.get('explanation_method'))
        pred.setdefault('explanation_scope', exp.get('explanation_scope'))
        pred.setdefault('top_features', exp.get('top_features') or [])
        pred['regras_disparadas'] = state.get('regras_disparadas') or []
        pred['retrieved_sources'] = [
            {'doc_id': f.get('doc_id'), 'category': f.get('category'), 'chunk_id': f.get('chunk_id')}
            for f in (state.get('fontes') or [])
        ]
        modo = state.get('modo') or 'normal'
        if modo == 'incompleto':
            pred['prediction'] = pred.get('prediction') or 'incompleto'
        payload = montar_payload(pred, modo)
        if modo == 'incompleto' or not chat_model:
            return {
                'payload_llm': payload,
                'texto_llm': '',
                'variante_prompt': 'nenhum',
                'raciocinio': _append(state, 'LLM não chamado (incompleto ou sem chat_model).'),
            }
        prompt = prompt_sintese(payload)
        try:
            texto = common.llm_text(chat_model, prompt, 'Você redige para a equipe. Não altere números.')
            return {
                'payload_llm': payload,
                'texto_llm': texto,
                'variante_prompt': 'sintese_v1',
                'falha_llm': None,
                'raciocinio': _append(state, 'Síntese LLM gerada (somente leitura do payload).'),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                'payload_llm': payload,
                'texto_llm': '',
                'falha_llm': str(exc),
                'raciocinio': _append(state, f'LLM falhou: {exc}'),
            }
    return node


def validar_resposta_llm(state: RiscoMLState) -> dict:
    payload = state.get('payload_llm') or {}
    texto = state.get('texto_llm') or ''
    if not texto:
        return {
            'texto_descartado': True,
            'verificacao': None,
            'raciocinio': _append(state, 'Sem texto LLM — usar resposta estruturada.'),
        }
    ver = verificar_coerencia_numerica(texto, payload)
    return {
        'verificacao': ver,
        'texto_descartado': not ver.aprovada,
        'raciocinio': _append(
            state,
            'Validação LLM: ' + ('aprovada' if ver.aprovada else 'descartada'),
        ),
    }


def _rota_validacao_llm(state: RiscoMLState) -> str:
    return 'usar_resposta_estruturada' if state.get('texto_descartado') else 'aplicar_avisos_seguranca'


def usar_resposta_estruturada(state: RiscoMLState) -> dict:
    payload = state.get('payload_llm') or {}
    return {
        'resposta_texto': resposta_estruturada(payload),
        'raciocinio': _append(state, 'Texto do LLM descartado; template determinístico.'),
    }


def aplicar_avisos_seguranca(state: RiscoMLState) -> dict:
    payload = dict(state.get('payload_llm') or {})
    payload['safety_notice'] = SAFETY_NOTICE
    payload['aviso_dados_sinteticos'] = AVISO_SINTETICO
    texto = state.get('resposta_texto') or state.get('texto_llm') or resposta_estruturada(payload)
    if SAFETY_NOTICE not in texto:
        texto = texto.rstrip() + '\n\n' + SAFETY_NOTICE
    if AVISO_SINTETICO not in texto:
        texto = texto.rstrip() + '\n\n' + AVISO_SINTETICO
    return {
        'payload_llm': payload,
        'resposta_texto': texto,
        'raciocinio': _append(state, 'Avisos de segurança anexados.'),
    }


def auditar(conn):
    def node(state: RiscoMLState) -> dict:
        pred = state.get('resultado_predicao') or {}
        exp = state.get('resultado_explicacao') or {}
        modo = state.get('modo') or 'incompleto'
        tops = _top_auditoria(exp.get('top_features') or pred.get('top_features') or [])
        probs = pred.get('probabilities') or {}
        p = None if not probs else probs.get('alto_risco')
        rotulo = pred.get('prediction') or 'incompleto'
        try:
            cur = conn.execute(
                '''INSERT INTO predicoes_ml (
                    usuario, paciente_id, modelo_nome, modelo_versao, dataset_versao,
                    features_hash, predicao, probabilidade, threshold,
                    explicacao_metodo, top_features, regras_disparadas, modo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    state.get('usuario') or 'sessao_demo',
                    state.get('paciente_id'),
                    pred.get('model_name') or 'nenhum',
                    pred.get('model_version') or 'n/a',
                    pred.get('dataset_version') or 'v1.0.0',
                    pred.get('features_hash') or '',
                    rotulo,
                    p,
                    pred.get('threshold'),
                    exp.get('explanation_method'),
                    json.dumps(tops, ensure_ascii=False),
                    json.dumps(state.get('regras_disparadas') or [], ensure_ascii=False),
                    modo,
                ),
            )
            conn.commit()
            return {
                'auditoria_id': cur.lastrowid,
                'auditoria_falhou': False,
                'raciocinio': _append(state, f'Auditoria predicoes_ml id={cur.lastrowid}.'),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                'auditoria_id': None,
                'auditoria_falhou': True,
                'raciocinio': _append(state, f'Auditoria falhou: {exc}'),
            }
    return node


def compilar_resposta(state: RiscoMLState) -> dict:
    payload = state.get('payload_llm') or {}
    resp = {
        'modo': state.get('modo'),
        'prediction': payload.get('prediction') or (state.get('resultado_predicao') or {}).get('prediction'),
        'probabilities': payload.get('probabilities'),
        'threshold': payload.get('threshold'),
        'top_features': payload.get('top_features') or [],
        'dados_imputados': payload.get('dados_imputados') or state.get('dados_imputados') or [],
        'regras_disparadas': state.get('regras_disparadas') or [],
        'fontes': state.get('fontes') or [],
        'safety_notice': SAFETY_NOTICE,
        'aviso_dados_sinteticos': AVISO_SINTETICO,
        'resposta_texto': state.get('resposta_texto') or '',
        'campos_faltantes': state.get('campos_faltantes') or [],
        'erros_validacao': state.get('erros_validacao') or [],
        'requer_intervencao_humana': bool(state.get('requer_intervencao_humana')),
        'intervencao': state.get('intervencao'),
        'texto_descartado': bool(state.get('texto_descartado')),
        'auditoria_id': state.get('auditoria_id'),
        'correlation_id': state.get('correlation_id'),
        'raciocinio': state.get('raciocinio') or [],
        'falha_rag': state.get('falha_rag'),
        'falha_modelo': state.get('falha_modelo'),
        'explanation_method': (state.get('resultado_explicacao') or {}).get('explanation_method'),
    }
    return {'resposta_estruturada': resp}


def build_risco_ml_workflow(chat_model, conn, retriever):
    """Mesma assinatura dos quatro workflows da Fase 3."""
    from langgraph.graph import END, START, StateGraph

    g = StateGraph(RiscoMLState)
    g.add_node('validar_dados', validar_dados)
    g.add_node('erro_validacao', erro_validacao)
    g.add_node('dados_incompletos', dados_incompletos)
    g.add_node('solicitar_complemento', solicitar_complemento)
    g.add_node('regras_seguranca', regras_seguranca)
    g.add_node('bypass_ml', bypass_ml)
    g.add_node('executar_modelo_ml', executar_modelo_ml)
    g.add_node('modo_degradado', modo_degradado)
    g.add_node('gerar_explicabilidade', gerar_explicabilidade)
    g.add_node('recuperar_protocolos_rag', recuperar_protocolos_rag(retriever))
    g.add_node('sintetizar_com_llm', sintetizar_com_llm(chat_model))
    g.add_node('validar_resposta_llm', validar_resposta_llm)
    g.add_node('usar_resposta_estruturada', usar_resposta_estruturada)
    g.add_node('aplicar_avisos_seguranca', aplicar_avisos_seguranca)
    g.add_node('auditar', auditar(conn))
    g.add_node('compilar_resposta', compilar_resposta)

    g.add_edge(START, 'validar_dados')
    g.add_conditional_edges(
        'validar_dados',
        _rota_validacao,
        {
            'erro_validacao': 'erro_validacao',
            'dados_incompletos': 'dados_incompletos',
            'regras_seguranca': 'regras_seguranca',
        },
    )
    g.add_edge('dados_incompletos', 'solicitar_complemento')
    g.add_edge('erro_validacao', 'aplicar_avisos_seguranca')
    g.add_edge('solicitar_complemento', 'aplicar_avisos_seguranca')
    g.add_conditional_edges(
        'regras_seguranca',
        _rota_regras,
        {'bypass_ml': 'bypass_ml', 'executar_modelo_ml': 'executar_modelo_ml'},
    )
    g.add_edge('bypass_ml', 'recuperar_protocolos_rag')
    g.add_conditional_edges(
        'executar_modelo_ml',
        _rota_modelo,
        {
            'modo_degradado': 'modo_degradado',
            'gerar_explicabilidade': 'gerar_explicabilidade',
        },
    )
    g.add_edge('modo_degradado', 'recuperar_protocolos_rag')
    g.add_edge('gerar_explicabilidade', 'recuperar_protocolos_rag')
    g.add_edge('recuperar_protocolos_rag', 'sintetizar_com_llm')
    g.add_edge('sintetizar_com_llm', 'validar_resposta_llm')
    g.add_conditional_edges(
        'validar_resposta_llm',
        _rota_validacao_llm,
        {
            'usar_resposta_estruturada': 'usar_resposta_estruturada',
            'aplicar_avisos_seguranca': 'aplicar_avisos_seguranca',
        },
    )
    g.add_edge('usar_resposta_estruturada', 'aplicar_avisos_seguranca')
    g.add_edge('aplicar_avisos_seguranca', 'auditar')
    g.add_edge('auditar', 'compilar_resposta')
    g.add_edge('compilar_resposta', END)
    try:
        compiled = g.compile()
    except Exception:
        compiled = None
    return _WorkflowAdapter(compiled, chat_model, conn, retriever)


def _merge(state: dict, upd: dict) -> dict:
    out = dict(state)
    out.update(upd or {})
    return out


def executar_risco_ml(entrada: dict, chat_model, conn, retriever) -> dict:
    """Executa a topologia dos 16 nós sem depender de LangGraph runtime."""
    state: dict = dict(entrada)
    state = _merge(state, validar_dados(state))
    rota = _rota_validacao(state)
    if rota == 'erro_validacao':
        state = _merge(state, erro_validacao(state))
        state = _merge(state, aplicar_avisos_seguranca(state))
        state = _merge(state, auditar(conn)(state))
        return _merge(state, compilar_resposta(state))
    if rota == 'dados_incompletos':
        state = _merge(state, dados_incompletos(state))
        state = _merge(state, solicitar_complemento(state))
        state = _merge(state, aplicar_avisos_seguranca(state))
        state = _merge(state, auditar(conn)(state))
        return _merge(state, compilar_resposta(state))
    state = _merge(state, regras_seguranca(state))
    if _rota_regras(state) == 'bypass_ml':
        state = _merge(state, bypass_ml(state))
    else:
        state = _merge(state, executar_modelo_ml(state))
        if _rota_modelo(state) == 'modo_degradado':
            state = _merge(state, modo_degradado(state))
        else:
            state = _merge(state, gerar_explicabilidade(state))
    state = _merge(state, recuperar_protocolos_rag(retriever)(state))
    state = _merge(state, sintetizar_com_llm(chat_model)(state))
    state = _merge(state, validar_resposta_llm(state))
    if _rota_validacao_llm(state) == 'usar_resposta_estruturada':
        state = _merge(state, usar_resposta_estruturada(state))
    state = _merge(state, aplicar_avisos_seguranca(state))
    state = _merge(state, auditar(conn)(state))
    return _merge(state, compilar_resposta(state))


class _WorkflowAdapter:
    def __init__(self, compiled, chat_model, conn, retriever):
        self._compiled = compiled
        self._chat = chat_model
        self._conn = conn
        self._retr = retriever

    def invoke(self, state: dict, config=None):
        if self._compiled is not None:
            try:
                return self._compiled.invoke(state, config=config) if config else self._compiled.invoke(state)
            except Exception:
                pass
        return executar_risco_ml(state, self._chat, self._conn, self._retr)


def classificar_risco_ml_opcional(state: dict) -> dict:
    """Nó opcional do obstétrico. No-op se não houver payload estruturado completo."""
    bruto = state.get('dados_clinicos_ml')
    if not bruto:
        return {}
    try:
        feat = parse_gestante(bruto)
        pred = prever(feat, nome_modelo=MODELO_PADRAO)
    except (DadosIncompletosError, DominioInvalidoError, ModeloIndisponivelError):
        return {}
    return {
        'classificacao_risco': pred['prediction'],
        'fatores_risco_identificados': list(state.get('fatores_risco_identificados') or [])
        + [f"ml:{pred['prediction']}"],
        'raciocinio': list(state.get('raciocinio') or [])
        + [f"Nó ML opcional: {pred['prediction']} P={pred['probabilities']['alto_risco']}"],
    }
