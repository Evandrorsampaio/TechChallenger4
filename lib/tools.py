"""Ferramentas LangChain do assistente clínico.

Toda função recebe `paciente_id` explícito (sem busca por nome) para evitar
vazamento cruzado. Acesso a `registros_violencia` SEMPRE loga em `log_acesso`
com motivo informado.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from . import alertas as alertas_mod
from . import db as db_mod


# Identificador do profissional logado (em produção viria de OAuth/SSO).
# Pode ser sobrescrito por set_usuario_atual() ou via variável de ambiente.
_USUARIO_ATUAL: str = 'sessao_demo'


def set_usuario_atual(identificador: str) -> None:
    global _USUARIO_ATUAL
    _USUARIO_ATUAL = identificador


def get_usuario_atual() -> str:
    return _USUARIO_ATUAL


def _log_acesso(conn: sqlite3.Connection, tabela: str,
                paciente_id: int | None, motivo: str) -> None:
    conn.execute(
        'INSERT INTO log_acesso (usuario, tabela, paciente_id, motivo) VALUES (?, ?, ?, ?)',
        (_USUARIO_ATUAL, tabela, paciente_id, motivo),
    )
    conn.commit()


# ---------- Schemas Pydantic (entradas das tools) ----------

class ConsultarProntuarioInput(BaseModel):
    paciente_id: int = Field(..., description='ID interno da paciente')


class HistoricoExamesInput(BaseModel):
    paciente_id: int = Field(..., description='ID interno da paciente')
    tipo: str | None = Field(
        None,
        description="Filtro por tipo: 'papanicolau', 'mamografia', 'usg_pelvica', 'usg_mamaria', 'colposcopia'. Omita para todos.",
    )


class ConsultarMedicamentoInput(BaseModel):
    termo: str = Field(..., description='Princípio ativo, nome comercial ou indicação')


class RegistroViolenciaInput(BaseModel):
    paciente_id: int
    tipo: str = Field(..., description="'fisica','psicologica','sexual','patrimonial','moral'")
    encaminhamentos: str
    observacoes: str = ''


class ConsultarViolenciaInput(BaseModel):
    paciente_id: int
    motivo: str = Field(..., description='Justificativa clínica do acesso (vai para o log)')


class AvaliarPadraoViolenciaInput(BaseModel):
    sinais: list[str] = Field(
        ...,
        description=(
            'Lista de chaves de sinais observados. Chaves válidas: '
            "lesoes_inexplicadas, lesoes_multiplas_fases, retardo_atendimento, "
            "discordancia_historia_exame, acompanhante_controlador, abortos_inexplicados, "
            "somatizacoes_cronicas, baixa_adesao, ideacao_suicida, gestacao_indesejada, "
            "isolamento_social, historico_violencia_familiar"
        ),
    )


# ---------- Implementações ----------

def consultar_prontuario(paciente_id: int, conn: sqlite3.Connection) -> dict[str, Any]:
    """Retorna dados base + prontuário ginecológico/obstétrico."""
    pac = conn.execute(
        'SELECT paciente_id, nome, data_nascimento, convenio FROM pacientes WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()
    if not pac:
        return {'erro': f'Paciente {paciente_id} não encontrada.'}
    pron = conn.execute(
        'SELECT menarca_idade, g_p_a, dum, metodo_contraceptivo, historico_familiar, observacoes '
        'FROM prontuario_gineco WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()
    idade = (date(2026, 5, 22) - date.fromisoformat(pac['data_nascimento'])).days // 365
    return {
        'paciente_id': pac['paciente_id'],
        'nome': pac['nome'],
        'idade': idade,
        'data_nascimento': pac['data_nascimento'],
        'convenio': pac['convenio'],
        'prontuario_gineco': dict(pron) if pron else None,
    }


def historico_exames(paciente_id: int, conn: sqlite3.Connection,
                     tipo: str | None = None) -> list[dict]:
    """Histórico de exames preventivos. Filtra por tipo se informado."""
    if tipo:
        rows = conn.execute(
            'SELECT tipo, data_realizacao, resultado, proximo_recomendado FROM exames '
            'WHERE paciente_id = ? AND tipo = ? ORDER BY data_realizacao DESC',
            (paciente_id, tipo),
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT tipo, data_realizacao, resultado, proximo_recomendado FROM exames '
            'WHERE paciente_id = ? ORDER BY data_realizacao DESC',
            (paciente_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def exames_atrasados(paciente_id: int, conn: sqlite3.Connection) -> list[dict]:
    """Aplica regras determinísticas e retorna lista de exames em atraso."""
    return [
        {
            'tipo': a.tipo,
            'ultima_data': a.ultima_data.isoformat() if a.ultima_data else None,
            'meses_desde_ultimo': a.meses_desde_ultimo,
            'motivo': a.motivo,
            'prioridade': a.prioridade,
        }
        for a in alertas_mod.exames_atrasados(conn, paciente_id)
    ]


def consultar_medicamento(termo: str, conn: sqlite3.Connection) -> list[dict]:
    """Busca por princípio ativo, nome comercial ou indicação (LIKE)."""
    padrao = f'%{termo.lower()}%'
    rows = conn.execute(
        'SELECT nome_principio_ativo, nome_comercial, indicacoes, contraindicacoes, '
        '       categoria_gestacao, categoria_lactacao '
        'FROM medicamentos '
        'WHERE LOWER(nome_principio_ativo) LIKE ? '
        '   OR LOWER(nome_comercial) LIKE ? '
        '   OR LOWER(indicacoes) LIKE ?',
        (padrao, padrao, padrao),
    ).fetchall()
    return [dict(r) for r in rows]


def calendario_menstrual(paciente_id: int, conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Estimativa de próxima menstruação e janela fértil."""
    return alertas_mod.proximo_periodo_menstrual(conn, paciente_id)


def registrar_violencia(paciente_id: int, tipo: str, encaminhamentos: str,
                        conn: sqlite3.Connection, observacoes: str = '') -> dict:
    """Registra atendimento por violência (notificação SINAN obrigatória)."""
    if tipo not in ('fisica', 'psicologica', 'sexual', 'patrimonial', 'moral'):
        return {'erro': f'Tipo inválido: {tipo}'}
    _log_acesso(conn, 'registros_violencia', paciente_id,
                f'Registro novo: {tipo}')
    conn.execute(
        'INSERT INTO registros_violencia '
        '(paciente_id, tipo, data_atendimento, notificado_sinan, encaminhamentos, observacoes) '
        'VALUES (?, ?, DATE("now"), 1, ?, ?)',
        (paciente_id, tipo, encaminhamentos, observacoes),
    )
    conn.commit()
    return {
        'status': 'registrado',
        'paciente_id': paciente_id,
        'tipo': tipo,
        'notificado_sinan': True,
    }


def consultar_violencia(paciente_id: int, motivo: str,
                        conn: sqlite3.Connection) -> list[dict]:
    """Consulta histórico de registros. SEMPRE loga acesso com motivo."""
    if not motivo or len(motivo.strip()) < 5:
        return [{'erro': 'Motivo de acesso obrigatório (mín. 5 caracteres) — LGPD.'}]
    _log_acesso(conn, 'registros_violencia', paciente_id, motivo.strip())
    rows = conn.execute(
        'SELECT tipo, data_atendimento, notificado_sinan, encaminhamentos, observacoes '
        'FROM registros_violencia WHERE paciente_id = ? '
        'ORDER BY data_atendimento DESC',
        (paciente_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def avaliar_padrao_violencia(sinais: list[str]) -> dict:
    """Aplica matriz de pontuação derivada dos protocolos do MS."""
    av = alertas_mod.avaliar_padrao_violencia(sinais)
    return {
        'score': av.score,
        'nivel': av.nivel,
        'sinais_presentes': av.sinais_presentes,
        'sinais_descricoes': av.sinais_descricoes,
        'conduta_sugerida': av.conduta_sugerida,
        'encaminhamentos': av.encaminhamentos,
    }


# ---------- Buscar protocolo (RAG) ----------

def buscar_protocolo(query: str, retriever, k: int = 4,
                     categoria: str | None = None) -> list[dict]:
    """Busca chunks dos protocolos via retriever Chroma já indexado.

    `retriever` deve ser um objeto com .invoke(query) -> List[Document].
    Filtragem por categoria é feita em pós-processamento porque o retriever
    em si não suporta filtro dinâmico em todas as versões do langchain.
    """
    docs = retriever.invoke(query)
    resultados = []
    for d in docs[:k * 2]:  # pega mais e filtra
        meta = d.metadata or {}
        if categoria and meta.get('category') != categoria:
            continue
        resultados.append({
            'trecho': d.page_content,
            'doc_id': meta.get('doc_id'),
            'category': meta.get('category'),
            'chunk_id': meta.get('chunk_id'),
        })
        if len(resultados) >= k:
            break
    return resultados


# ---------- Adaptadores LangChain (criados a partir de uma conexão + retriever) ----------

def build_langchain_tools(conn: sqlite3.Connection, retriever):
    """Devolve lista de StructuredTool prontos para um agente LangChain.

    Mantém a conexão e o retriever em closures para o agente não precisar
    receber esses objetos como argumentos.
    """
    from langchain_core.tools import StructuredTool

    return [
        StructuredTool.from_function(
            func=lambda paciente_id: consultar_prontuario(paciente_id, conn),
            name='consultar_prontuario',
            description='Retorna dados base + prontuário ginecológico/obstétrico da paciente.',
            args_schema=ConsultarProntuarioInput,
        ),
        StructuredTool.from_function(
            func=lambda paciente_id, tipo=None: historico_exames(paciente_id, conn, tipo),
            name='historico_exames',
            description='Histórico de exames preventivos. Filtra por tipo se informado.',
            args_schema=HistoricoExamesInput,
        ),
        StructuredTool.from_function(
            func=lambda paciente_id: exames_atrasados(paciente_id, conn),
            name='exames_atrasados',
            description='Lista exames preventivos em atraso (papanicolau, mamografia) com motivo e prioridade.',
            args_schema=ConsultarProntuarioInput,
        ),
        StructuredTool.from_function(
            func=lambda termo: consultar_medicamento(termo, conn),
            name='consultar_medicamento',
            description='Busca medicamentos por princípio ativo, nome comercial ou indicação. Inclui categoria gestacional/lactacional.',
            args_schema=ConsultarMedicamentoInput,
        ),
        StructuredTool.from_function(
            func=lambda paciente_id: calendario_menstrual(paciente_id, conn),
            name='calendario_menstrual',
            description='Estimativa de próxima menstruação e janela fértil baseado no histórico de ciclos.',
            args_schema=ConsultarProntuarioInput,
        ),
        StructuredTool.from_function(
            func=lambda paciente_id, tipo, encaminhamentos, observacoes='':
                registrar_violencia(paciente_id, tipo, encaminhamentos, conn, observacoes),
            name='registrar_violencia',
            description='Registra atendimento por violência e notifica SINAN. Use apenas com confirmação clínica.',
            args_schema=RegistroViolenciaInput,
        ),
        StructuredTool.from_function(
            func=lambda paciente_id, motivo: consultar_violencia(paciente_id, motivo, conn),
            name='consultar_violencia',
            description=('Consulta histórico de registros de violência. Acesso auditado — motivo clínico obrigatório.'),
            args_schema=ConsultarViolenciaInput,
        ),
        StructuredTool.from_function(
            func=avaliar_padrao_violencia,
            name='avaliar_padrao_violencia',
            description=('Aplica matriz de pontuação para sinais suspeitos de violência. '
                         'Retorna score, nível de suspeita e conduta sugerida.'),
            args_schema=AvaliarPadraoViolenciaInput,
        ),
        StructuredTool.from_function(
            func=lambda query, categoria=None: buscar_protocolo(query, retriever, k=4, categoria=categoria),
            name='buscar_protocolo',
            description=('Busca trechos dos protocolos clínicos (ginecologia/obstetrícia, câncer mama/colo, '
                         'planejamento familiar, violência doméstica, saúde mental). Use para condutas, doses, fluxos.'),
        ),
    ]
