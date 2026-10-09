"""Contrato somente-leitura entre ML e LLM."""
from __future__ import annotations

from lib.ml.predict import AVISO_SINTETICO, SAFETY_NOTICE

CHAVES = (
    'model_name',
    'model_version',
    'dataset_version',
    'prediction',
    'threshold',
    'probabilities',
    'explanation_method',
    'explanation_scope',
    'top_features',
    'dados_imputados',
    'retrieved_sources',
    'regras_disparadas',
    'safety_notice',
    'aviso_dados_sinteticos',
)


class ContratoInvalidoError(ValueError):
    pass


def montar_payload(base: dict, modo: str) -> dict:
    payload = dict(base)
    payload.setdefault('safety_notice', SAFETY_NOTICE)
    payload.setdefault('aviso_dados_sinteticos', AVISO_SINTETICO)
    payload.setdefault('retrieved_sources', [])
    payload.setdefault('regras_disparadas', [])
    payload.setdefault('top_features', [])
    payload.setdefault('explanation_method', None)
    payload.setdefault('explanation_scope', None)
    payload.setdefault('dados_imputados', [])
    payload['modo'] = modo
    faltando = [k for k in ('prediction', 'safety_notice', 'aviso_dados_sinteticos') if not payload.get(k)]
    if faltando:
        raise ContratoInvalidoError(f'Payload incompleto: {faltando}')
    return payload


def resposta_estruturada(payload: dict) -> str:
    linhas = [
        f"**Modo:** `{payload.get('modo', 'normal')}`",
        f"**Classificação:** `{payload.get('prediction')}`",
    ]
    probs = payload.get('probabilities') or {}
    if probs:
        linhas.append(
            f"**Probabilidades:** habitual={probs.get('habitual')}, "
            f"alto_risco={probs.get('alto_risco')} (limiar={payload.get('threshold')})"
        )
    if payload.get('regras_disparadas'):
        linhas.append('**Regras disparadas:** ' + ', '.join(payload['regras_disparadas']))
    tops = payload.get('top_features') or []
    if tops:
        linhas.append('**Variáveis que mais contribuíram para esta classificação:**')
        for t in tops:
            linhas.append(
                f"- `{t.get('feature')}` ({t.get('direction')}): contribuição {t.get('contribution')}"
            )
    if payload.get('dados_imputados'):
        linhas.append('**Campos imputados (opcionais):** ' + ', '.join(payload['dados_imputados']))
    fontes = payload.get('retrieved_sources') or []
    if fontes:
        linhas.append('**Fontes:**')
        for f in fontes:
            linhas.append(f"- `{f.get('doc_id')}` ({f.get('category')})")
    else:
        linhas.append('_Nenhuma fonte documental recuperada nesta execução._')
    linhas.append('')
    linhas.append(payload.get('safety_notice', SAFETY_NOTICE))
    linhas.append(payload.get('aviso_dados_sinteticos', AVISO_SINTETICO))
    return '\n'.join(linhas)


def prompt_sintese(payload: dict) -> str:
    return (
        'Você redige para a EQUIPE DE SAÚDE. Não altere números, rótulos, limiar nem contribuições. '
        'Não calcule nada. Não invente conduta sem as fontes listadas. '
        'Use a frase: "As variáveis que mais contribuíram para esta classificação foram…". '
        'Não use linguagem causal ("causou o risco").\n\n'
        f'PAYLOAD_JSON:\n{payload}\n'
    )
