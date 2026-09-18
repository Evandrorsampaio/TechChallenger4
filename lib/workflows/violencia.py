"""Fluxo de Detecção de Violência Doméstica.

Diagrama:

    START
      ↓
    extrair_sinais        (LLM mapeia descrição → checklist de sinais)
      ↓
    avaliar_risco         (matriz determinística — alertas_mod.avaliar_padrao_violencia)
      ↓
   ┌─────────┴─────────┐
   │      nível?       │
   └──┬──────┬──────┬──┘
     baixo  médio  alto
      ↓      ↓      ↓
      ↓      ↓    protocolo_seguranca   (ambiente reservado, sem acompanhante)
      ↓      ↓      ↓
      └─→ acionar_equipe (assistência social, psicologia, [+ Delegacia se alto])
              ↓
        documentar_seguro  (registra com criptografia + log_acesso + SINAN)
              ↓
        definir_seguimento (plano de retorno)
              ↓
        compilar_resposta
              ↓
             END
"""
from __future__ import annotations

from typing import TypedDict

from . import common
from .. import alertas as alertas_mod
from .. import tools as tools_mod


class ViolenciaState(TypedDict, total=False):
    # Inputs
    descricao_caso: str
    paciente_id: int | None
    profissional: str
    confirmacao_clinica: bool       # se False, NÃO registra no DB

    # Intermediários
    sinais_identificados: list[str]
    score: int
    nivel: str                       # 'sem_alerta' | 'atencao' | 'alta_suspeita'
    conduta_sugerida: str
    encaminhamentos: list[str]
    protocolo_seguranca_ativado: bool
    medidas: list[str]
    equipe_acionada: list[str]
    notificacao_sinan: bool
    registro_id: int | None
    seguimento: dict                 # {prazo_retorno, profissionais_envolvidos}

    # Explainability
    raciocinio: list[str]
    fontes: list[dict]
    confianca: str

    # Output
    resposta_estruturada: dict


# Mapa de descrição livre → chaves canônicas de SINAIS_VIOLENCIA
SINAIS_KEYS = list(alertas_mod.SINAIS_VIOLENCIA.keys())


# ============= NODES =============

def _extrair_sinais(chat_model):
    def node(state: ViolenciaState) -> dict:
        chaves_validas = ', '.join(SINAIS_KEYS)
        sistema = ('Você é profissional de saúde com expertise em atendimento '
                   'a vítimas de violência. Mapeie a descrição do caso para as chaves canônicas.')
        prompt = (
            f'Descrição do caso clínico:\n"{state["descricao_caso"]}"\n\n'
            f'Selecione APENAS as chaves cujos sinais estão claramente presentes. '
            f'Chaves válidas: {chaves_validas}\n\n'
            'Responda: {"sinais": ["lesoes_inexplicadas", "acompanhante_controlador", ...]}'
        )
        out = common.llm_json(chat_model, prompt, sistema, default={'sinais': []})
        sinais = [s for s in out.get('sinais', []) if s in SINAIS_KEYS]
        return {
            'sinais_identificados': sinais,
            'raciocinio': [f'Sinais identificados pelo LLM: {", ".join(sinais) or "nenhum"}'],
        }
    return node


def _avaliar_risco(state: ViolenciaState) -> dict:
    """Determinístico: aplica matriz de pontuação."""
    sinais = state.get('sinais_identificados', [])
    av = alertas_mod.avaliar_padrao_violencia(sinais)
    return {
        'score': av.score,
        'nivel': av.nivel,
        'conduta_sugerida': av.conduta_sugerida,
        'encaminhamentos': av.encaminhamentos,
        'raciocinio': state.get('raciocinio', []) +
                      [f'Score = {av.score}, nível = {av.nivel}'],
    }


def _protocolo_seguranca(state: ViolenciaState) -> dict:
    """Determinístico: ativa protocolo de segurança quando alta_suspeita."""
    medidas = [
        'Conduzir atendimento em ambiente reservado, SEM acompanhante',
        'Garantir presença de profissional do mesmo gênero (preferencialmente)',
        'Aplicar perguntas-chave da Norma Técnica (ex.: "alguém em casa tem feito mal a você?")',
        'Documentar achados em prontuário com linguagem objetiva e descritiva',
        'Avaliar segurança imediata: paciente pode voltar para casa em segurança?',
        'Avaliar risco para crianças/dependentes',
    ]
    return {
        'protocolo_seguranca_ativado': True,
        'medidas': medidas,
        'raciocinio': state.get('raciocinio', []) +
                      ['Protocolo de segurança ATIVADO (alta suspeita).'],
    }


def _acionar_equipe(state: ViolenciaState) -> dict:
    """Determinístico: define equipe e encaminhamentos da rede."""
    nivel = state.get('nivel', 'sem_alerta')
    equipe = []
    if nivel in ('atencao', 'alta_suspeita'):
        equipe.extend(['Assistência social hospitalar', 'Psicologia'])
    if nivel == 'alta_suspeita':
        equipe.extend(['Ginecologia (revisão clínica)', 'Enfermagem responsável pela notificação SINAN'])
        # Se ideação suicida nos sinais
        if 'ideacao_suicida' in state.get('sinais_identificados', []):
            equipe.append('CAPS / psiquiatria de plantão')

    return {
        'equipe_acionada': equipe,
        'raciocinio': state.get('raciocinio', []) +
                      [f'Equipe acionada ({len(equipe)}): {", ".join(equipe) or "nenhuma"}'],
    }


def _documentar_seguro(state: ViolenciaState, conn):
    """Registra com auditoria — só quando alta_suspeita E confirmação clínica."""
    nivel = state.get('nivel', 'sem_alerta')
    deve_registrar = (nivel == 'alta_suspeita' and state.get('confirmacao_clinica', False))

    if not deve_registrar:
        return {
            'notificacao_sinan': False,
            'registro_id': None,
            'raciocinio': state.get('raciocinio', []) +
                          [f'Sem registro formal (nivel={nivel}, confirmacao={state.get("confirmacao_clinica")}). '
                           f'Manter escuta atenta em consultas subsequentes.'],
        }

    # Configura usuário atual no log (se já não tiver sido feito)
    profissional = state.get('profissional', 'sessao_workflow')
    tools_mod.set_usuario_atual(profissional)

    paciente_id = state.get('paciente_id')
    if not paciente_id:
        return {
            'notificacao_sinan': False,
            'registro_id': None,
            'raciocinio': state.get('raciocinio', []) +
                          ['Sem paciente_id — não é possível registrar formalmente. Faça registro físico.'],
        }

    # Determina tipo predominante a partir dos sinais
    sinais = state.get('sinais_identificados', [])
    if any('lesoes' in s for s in sinais):
        tipo = 'fisica'
    elif 'ideacao_suicida' in sinais or 'somatizacoes_cronicas' in sinais:
        tipo = 'psicologica'
    else:
        tipo = 'psicologica'

    encs = '; '.join(state.get('encaminhamentos', []))
    res = tools_mod.registrar_violencia(
        paciente_id=paciente_id, tipo=tipo,
        encaminhamentos=encs,
        observacoes=state.get('descricao_caso', '')[:500],
        conn=conn,
    )
    registro_ok = res.get('status') == 'registrado'

    rid = None
    if registro_ok:
        row = conn.execute(
            'SELECT id FROM registros_violencia WHERE paciente_id = ? '
            'ORDER BY id DESC LIMIT 1', (paciente_id,),
        ).fetchone()
        rid = row['id'] if row else None

    return {
        'notificacao_sinan': registro_ok,
        'registro_id': rid,
        'raciocinio': state.get('raciocinio', []) +
                      [f'Registro SINAN: {"✅ id=" + str(rid) if registro_ok else "❌ falhou"}; '
                       f'log_acesso atualizado (usuario={profissional}).'],
    }


def _definir_seguimento(state: ViolenciaState) -> dict:
    nivel = state.get('nivel', 'sem_alerta')
    if nivel == 'alta_suspeita':
        seg = {
            'prazo_retorno': '7-14 dias (reavaliação por psicologia)',
            'profissionais_envolvidos': ['Assistência social', 'Psicologia', 'Ginecologia'],
            'orientacoes': ('Verificar segurança da paciente nos primeiros 7 dias. '
                           'Reforçar serviços da rede (Ligue 180, Centro de Referência) na alta. '
                           'Documentar contatos subsequentes em prontuário com a mesma confidencialidade.'),
        }
    elif nivel == 'atencao':
        seg = {
            'prazo_retorno': '30 dias',
            'profissionais_envolvidos': ['Psicologia (avaliação opcional)'],
            'orientacoes': ('Manter escuta qualificada nas próximas consultas. '
                           'Documentar evolução dos sinais identificados.'),
        }
    else:
        seg = {
            'prazo_retorno': 'rotina',
            'profissionais_envolvidos': [],
            'orientacoes': 'Sem necessidade de seguimento específico. Manter vigilância clínica.',
        }
    return {
        'seguimento': seg,
        'raciocinio': state.get('raciocinio', []) + [f'Seguimento definido: retorno {seg["prazo_retorno"]}'],
    }


def _compilar_resposta(state: ViolenciaState) -> dict:
    confianca = common.estimar_confianca(
        n_fontes=0,           # esse fluxo é guiado por matriz, não RAG
        n_decisoes_llm=1,
        dados_paciente_disponiveis=state.get('paciente_id') is not None,
    )
    resposta = {
        'sinais_identificados': state.get('sinais_identificados', []),
        'sinais_descricoes': [alertas_mod.SINAIS_VIOLENCIA[s] for s in state.get('sinais_identificados', [])],
        'score': state.get('score'),
        'nivel': state.get('nivel'),
        'conduta_sugerida': state.get('conduta_sugerida'),
        'protocolo_seguranca_ativado': state.get('protocolo_seguranca_ativado', False),
        'medidas': state.get('medidas', []),
        'equipe_acionada': state.get('equipe_acionada', []),
        'encaminhamentos': state.get('encaminhamentos', []),
        'notificacao_sinan': state.get('notificacao_sinan', False),
        'registro_id': state.get('registro_id'),
        'seguimento': state.get('seguimento'),
        'confianca': confianca,
        'raciocinio': state.get('raciocinio', []),
    }
    return {'confianca': confianca, 'resposta_estruturada': resposta}


# ============= GRAPH =============

def _rota_nivel(state: ViolenciaState) -> str:
    nivel = state.get('nivel', 'sem_alerta')
    if nivel == 'alta_suspeita':
        return 'protocolo_seguranca'
    return 'acionar_equipe'   # 'atencao' ou 'sem_alerta'


def build_violencia_workflow(chat_model, conn, retriever):
    """Compila o StateGraph do fluxo de Detecção de Violência.

    `retriever` é aceito por consistência com os outros workflows; este
    fluxo usa matriz determinística (`avaliar_padrao_violencia`), não RAG.
    """
    from langgraph.graph import StateGraph, START, END

    g = StateGraph(ViolenciaState)
    g.add_node('extrair_sinais', _extrair_sinais(chat_model))
    g.add_node('avaliar_risco', _avaliar_risco)
    g.add_node('protocolo_seguranca', _protocolo_seguranca)
    g.add_node('acionar_equipe', _acionar_equipe)
    g.add_node('documentar_seguro', lambda s: _documentar_seguro(s, conn))
    g.add_node('definir_seguimento', _definir_seguimento)
    g.add_node('compilar_resposta', _compilar_resposta)

    g.add_edge(START, 'extrair_sinais')
    g.add_edge('extrair_sinais', 'avaliar_risco')
    g.add_conditional_edges('avaliar_risco', _rota_nivel,
                            {'protocolo_seguranca': 'protocolo_seguranca',
                             'acionar_equipe':      'acionar_equipe'})
    g.add_edge('protocolo_seguranca', 'acionar_equipe')
    g.add_edge('acionar_equipe', 'documentar_seguro')
    g.add_edge('documentar_seguro', 'definir_seguimento')
    g.add_edge('definir_seguimento', 'compilar_resposta')
    g.add_edge('compilar_resposta', END)

    return g.compile()
