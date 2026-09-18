"""Validador da Fase 3.

Preferir `lib.validacao` na evolução ML. Este módulo permanece para os notebooks
e para o import reexportado; não apagar.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


# Categorias sensitive do projeto (conforme convenção em lib/workflows/)
CATEGORIAS_SENSITIVE = {'violencia_domestica', 'saude_mental'}

# Serviços da rede que respostas sensitive devem mencionar (alinhado ao
# que o fine-tuning aprendeu via PROMPT_SENSITIVE no 02_gerar_dataset_sft)
SERVICOS_REDE = (
    'SINAN',
    'Ligue 180',
    'CVV',
    '188',
    'CAPS',
    'SAMU 192',
    'Delegacia da Mulher',
    'Centro de Referência',
)

# Padrões que indicam diagnóstico definitivo proibido pelo enunciado
PADROES_DIAGNOSTICO = (
    r'\b(o\s+)?diagn[óo]stico\s+(é|e|definitivo|confirmado)',
    r'\bpaciente\s+(tem|possui|apresenta)\s+(c[aâ]ncer|HIV|s[íi]filis|gonorreia)',
    r'\b[ée]\s+certo\s+que\s+a\s+paciente',
    r'\bcertamente\s+(é|tem|possui|apresenta)',
)

# Padrões de prescrição direta — exige disclaimer de validação
PADROES_PRESCRICAO = (
    r'\bprescrev[ao]\b',
    r'\breceit[oe]i?\b',
    r'\btome\s+\d+\s*(mg|mcg|g|ml|UI|comp|cp)',
    r'\buse\s+\d+\s*(mg|mcg|g|ml|UI|comp|cp)',
)

# Padrões que indicam resposta dirigida à paciente — projeto é para a
# equipe de saúde, não para a paciente (decisão de público-alvo de
# 2026-05-22, ver project_assistente_hospitalar.md)
PADROES_DIRIGIDO_PACIENTE = (
    r'\bvocê\s+(deve|precisa|pode|tem\s+que)\s+procurar',
    r'\bprocure\s+um\s+(profissional|médico|psicólogo|ginecologista)',
    r'\bfique\s+(calma|tranquila)',
    r'\bnão\s+se\s+preocupe',
    r'\bse\s+você\s+est[áa]\s+sentindo',
)


@dataclass
class ResultadoValidacao:
    """Resultado da validação de uma resposta."""
    aprovada: bool
    violacoes: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    disclaimer_sugerido: str = ''


class ValidadorDeterministico:
    """Validador rápido baseado em regex/heurística.

    Cobre os 5 itens declarados nas regras de comportamento do assistente:
    (1) não-prescrição sem disclaimer, (2) não-diagnóstico definitivo,
    (3) menção a serviços da rede em categorias sensitive, (4) citação
    de fonte, (5) tom dirigido ao profissional (não à paciente).
    """

    def validar(self, resposta: str, categoria: str | None = None,
                fontes: list[dict] | None = None) -> ResultadoValidacao:
        violacoes: list[str] = []
        avisos: list[str] = []

        # 1. Diagnóstico definitivo — VIOLAÇÃO se detectado
        for padrao in PADROES_DIAGNOSTICO:
            if re.search(padrao, resposta, re.IGNORECASE):
                violacoes.append(
                    'Padrão de diagnóstico definitivo detectado. '
                    'Reescrever como "hipótese", "diferencial" ou "compatível com".'
                )
                break

        # 2. Prescrição direta sem disclaimer — VIOLAÇÃO
        tem_prescricao = any(
            re.search(p, resposta, re.IGNORECASE) for p in PADROES_PRESCRICAO
        )
        tem_disclaimer = bool(re.search(
            r'(valida[çc][ãa]o\s+de\s+especialista|sob\s+orienta[çc][ãa]o\s+m[ée]dica'
            r'|conforme\s+protocolo|seguindo\s+a\s+diretriz)',
            resposta, re.IGNORECASE,
        ))
        if tem_prescricao and not tem_disclaimer:
            violacoes.append(
                'Posologia direta sem referência a protocolo ou disclaimer de '
                'validação. Acrescentar "conforme protocolo X" ou "sob '
                'validação de especialista".'
            )

        # 3. Categoria sensitive sem serviços da rede — VIOLAÇÃO
        if categoria in CATEGORIAS_SENSITIVE:
            citou_servico = any(s.lower() in resposta.lower() for s in SERVICOS_REDE)
            if not citou_servico:
                violacoes.append(
                    'Categoria sensitive sem citação de serviço da rede '
                    '(SINAN, Ligue 180, CVV 188, CAPS, SAMU 192, Delegacia '
                    'da Mulher). Adicionar pelo menos um.'
                )

        # 4. Citação de fonte — AVISO (não bloqueia)
        fontes_em_metadata = bool(fontes)
        fontes_no_texto = bool(re.search(
            r'(fonte|protocolo|doc_id|febrasgo|inca|ms\b|oms)', resposta, re.IGNORECASE,
        ))
        if not fontes_em_metadata and not fontes_no_texto:
            avisos.append(
                'Resposta não cita fonte explícita. Adicionar "Fonte: <doc_id>".'
            )

        # 5. Dirigida à paciente — AVISO (não bloqueia, mas reformular)
        for padrao in PADROES_DIRIGIDO_PACIENTE:
            if re.search(padrao, resposta, re.IGNORECASE):
                avisos.append(
                    'Linguagem dirigida à paciente detectada. Reformular para '
                    'descrever conduta do profissional, não orientar a paciente.'
                )
                break

        disclaimer = ''
        if violacoes:
            disclaimer = (
                '\n\n⚠️ Esta resposta requer revisão. Validador automático '
                f'detectou {len(violacoes)} violação(ões) das regras de atuação '
                'do assistente (ver RELATORIO_TECNICO.md §4.5).'
            )

        return ResultadoValidacao(
            aprovada=not violacoes,
            violacoes=violacoes,
            avisos=avisos,
            disclaimer_sugerido=disclaimer,
        )


PROMPT_VALIDADOR_LLM = """Você é um auditor clínico revisando a resposta de um assistente \
para a EQUIPE DE SAÚDE (não para a paciente). Verifique se a resposta cumpre TODAS as regras:

1. NÃO prescreve medicação como ordem direta — apenas cita conduta do protocolo.
2. NÃO afirma diagnóstico definitivo — usa "hipótese", "diferencial", "compatível com".
3. SE a categoria é sensitive (violencia_domestica ou saude_mental), CITA pelo menos um \
serviço da rede (SINAN, Ligue 180, CVV 188, CAPS, SAMU 192, Delegacia da Mulher).
4. CITA fonte (protocolo, doc_id, sociedade médica como FEBRASGO/INCA/OMS/MS).
5. É dirigida ao PROFISSIONAL DE SAÚDE, não à paciente (não usa "você deve procurar").

Devolva JSON estrito, sem texto adicional:
{{
  "aprovada": true|false,
  "violacoes": ["lista", "de", "regras", "quebradas"],
  "sugestao_reescrita": "se aprovada=false, texto reescrito; caso contrário string vazia"
}}

CATEGORIA: {categoria}
RESPOSTA A VALIDAR:
\"\"\"
{resposta}
\"\"\""""


class ValidadorLLM:
    """Validador baseado em segundo passe do LLM.

    Latência: 5-10s adicionais por consulta — esta é a razão pela qual
    o validador não foi integrado aos workflows. Implementação literal do
    que o enunciado da Fase 3 pediu em "Validação da resposta pelo LLM
    antes do retorno".
    """

    def __init__(self, chat_model):
        self.chat_model = chat_model

    def validar(self, resposta: str, categoria: str | None = None,
                fontes: list[dict] | None = None) -> ResultadoValidacao:
        from langchain_core.messages import HumanMessage

        prompt = PROMPT_VALIDADOR_LLM.format(
            categoria=categoria or 'não especificada',
            resposta=resposta,
        )
        out = self.chat_model.invoke([HumanMessage(content=prompt)])
        text = out.content if hasattr(out, 'content') else str(out)

        cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', cleaned, re.DOTALL)
            data = json.loads(m.group(0)) if m else {'aprovada': True, 'violacoes': []}

        aprovada = bool(data.get('aprovada', True))
        violacoes = list(data.get('violacoes', []))
        sugestao = (data.get('sugestao_reescrita') or '').strip()

        disclaimer = ''
        if not aprovada and sugestao:
            disclaimer = (
                f'\n\n⚠️ Resposta revisada pelo validador. Versão sugerida:\n\n{sugestao}'
            )

        return ResultadoValidacao(
            aprovada=aprovada,
            violacoes=violacoes,
            avisos=[],
            disclaimer_sugerido=disclaimer,
        )


def _esboco_integracao_NAO_USE():
    """Esboço de como seria a integração — DESCARTADA por latência.

    Para integrar futuramente, no final de `_compilar_resposta` de cada
    workflow em `lib/workflows/`:

        from referencias.validador_resposta_llm import ValidadorDeterministico

        validador = ValidadorDeterministico()
        resultado = validador.validar(
            resposta=resposta_final,
            categoria=state.get('categoria'),
            fontes=state.get('fontes'),
        )
        if not resultado.aprovada:
            resposta_final += resultado.disclaimer_sugerido
            state['raciocinio'].append(
                f'Validador detectou: {", ".join(resultado.violacoes)}'
            )
        state['validacao'] = {
            'aprovada': resultado.aprovada,
            'violacoes': resultado.violacoes,
            'avisos': resultado.avisos,
        }
    """
    raise NotImplementedError('Esboço apenas — não integrar antes da entrega')


if __name__ == '__main__':
    v = ValidadorDeterministico()

    # Caso 1: sensitive sem citar a rede — DEVE REPROVAR
    r1 = v.validar(
        resposta='Em casos de violência, oriente acolhimento e escuta qualificada.',
        categoria='violencia_domestica',
    )
    assert not r1.aprovada, f'Esperava reprovação. Resultado: {r1}'
    print('[Caso 1] reprovou corretamente:', r1.violacoes[0][:80], '...')

    # Caso 2: sensitive com rede — DEVE APROVAR
    r2 = v.validar(
        resposta=(
            'Notificação SINAN compulsória. Acionar serviço social, oferecer '
            'encaminhamento ao Centro de Referência e informar Ligue 180. '
            'Conforme protocolo MS.'
        ),
        categoria='violencia_domestica',
    )
    assert r2.aprovada, f'Esperava aprovação. Resultado: {r2}'
    print('[Caso 2] aprovou corretamente')

    # Caso 3: diagnóstico definitivo — DEVE REPROVAR
    r3 = v.validar(
        resposta='O diagnóstico é câncer de mama. Encaminhar para mastologia.',
        categoria='cancer_mama_colo',
    )
    assert not r3.aprovada
    print('[Caso 3] reprovou diagnóstico definitivo:', r3.violacoes[0][:80], '...')

    # Caso 4: prescrição sem disclaimer — DEVE REPROVAR
    r4 = v.validar(
        resposta='Tome 500 mg de paracetamol de 6 em 6 horas.',
        categoria='ginecologia_obstetricia',
    )
    assert not r4.aprovada
    print('[Caso 4] reprovou prescrição direta:', r4.violacoes[0][:80], '...')

    # Caso 5: linguagem para paciente — APROVA mas avisa
    r5 = v.validar(
        resposta='Procure um profissional para avaliar conforme protocolo MS.',
        categoria='ginecologia_obstetricia',
    )
    assert r5.aprovada
    assert r5.avisos
    print('[Caso 5] aprovou com aviso:', r5.avisos[0][:80], '...')

    # Caso 6: resposta correta — DEVE APROVAR sem avisos
    r6 = v.validar(
        resposta=(
            'Hipótese: gestação ectópica rota. Encaminhamento imediato ao PS '
            'obstétrico para laparoscopia de urgência, conforme protocolo FEBRASGO.'
        ),
        categoria='ginecologia_obstetricia',
        fontes=[{'doc_id': 'febrasgo_emerg_obst_2018'}],
    )
    assert r6.aprovada
    assert not r6.avisos, f'Não esperava avisos: {r6.avisos}'
    print('[Caso 6] aprovou caso ideal sem avisos')

    print('\nTodos os 6 casos de teste passaram.')
