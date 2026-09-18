"""Lógica determinística de alertas — sem LLM.

Regras derivadas dos protocolos:
- Papanicolau: 25-64a, anual nos 2 primeiros (negativos), depois trienal. Atraso se >3.5a desde último.
- Mamografia: 50-69a bienal. Atraso se >2.5a desde último OU se nunca fez após 50a.
- USG mamária: NÃO é rastreio populacional — só por queixa, não gera alerta.
- Violência: checklist de sinais (Norma Técnica e cadernos AB do MS). Score ≥3 sinaliza investigação ativa.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

from lib.config import REFERENCE_DATE

TODAY = REFERENCE_DATE

DIAS_ANO = 365


@dataclass
class ExameAtrasado:
    tipo: str
    ultima_data: date | None
    meses_desde_ultimo: int | None
    motivo: str
    prioridade: Literal['alta', 'media', 'baixa']


def _idade(dn: date) -> int:
    return (TODAY - dn).days // DIAS_ANO


def exames_atrasados(conn: sqlite3.Connection, paciente_id: int) -> list[ExameAtrasado]:
    """Lista exames preventivos em atraso para a paciente."""
    row = conn.execute(
        'SELECT data_nascimento FROM pacientes WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()
    if not row:
        return []
    idade = _idade(date.fromisoformat(row['data_nascimento']))
    alertas: list[ExameAtrasado] = []

    # PAPANICOLAU — 25-64a
    if 25 <= idade <= 64:
        ultimo = conn.execute(
            "SELECT data_realizacao FROM exames "
            "WHERE paciente_id = ? AND tipo = 'papanicolau' "
            "ORDER BY data_realizacao DESC LIMIT 1",
            (paciente_id,),
        ).fetchone()
        if ultimo is None:
            alertas.append(ExameAtrasado(
                tipo='papanicolau', ultima_data=None, meses_desde_ultimo=None,
                motivo='Mulher 25-64a sem registro de citologia.',
                prioridade='alta',
            ))
        else:
            ultima = date.fromisoformat(ultimo['data_realizacao'])
            dias = (TODAY - ultima).days
            meses = dias // 30
            if dias > int(3.5 * DIAS_ANO):
                alertas.append(ExameAtrasado(
                    tipo='papanicolau', ultima_data=ultima, meses_desde_ultimo=meses,
                    motivo=f'Última citologia há {meses // 12}a {meses % 12}m (limite trienal ultrapassado).',
                    prioridade='alta' if dias > 5 * DIAS_ANO else 'media',
                ))

    # MAMOGRAFIA — 50-69a bienal
    if 50 <= idade <= 69:
        ultimo = conn.execute(
            "SELECT data_realizacao FROM exames "
            "WHERE paciente_id = ? AND tipo = 'mamografia' "
            "ORDER BY data_realizacao DESC LIMIT 1",
            (paciente_id,),
        ).fetchone()
        if ultimo is None:
            alertas.append(ExameAtrasado(
                tipo='mamografia', ultima_data=None, meses_desde_ultimo=None,
                motivo='Mulher 50-69a sem registro de mamografia.',
                prioridade='alta',
            ))
        else:
            ultima = date.fromisoformat(ultimo['data_realizacao'])
            dias = (TODAY - ultima).days
            meses = dias // 30
            if dias > int(2.5 * DIAS_ANO):
                alertas.append(ExameAtrasado(
                    tipo='mamografia', ultima_data=ultima, meses_desde_ultimo=meses,
                    motivo=f'Última mamografia há {meses // 12}a {meses % 12}m (limite bienal ultrapassado).',
                    prioridade='alta' if dias > 4 * DIAS_ANO else 'media',
                ))

    return alertas


# ---------- Detecção de padrões de violência ----------

SINAIS_VIOLENCIA = {
    'lesoes_inexplicadas': 'Lesões em locais não-expostos ou com explicação incompatível',
    'lesoes_multiplas_fases': 'Lesões em múltiplas fases de cicatrização',
    'retardo_atendimento': 'Retardo significativo na busca por atendimento',
    'discordancia_historia_exame': 'Discordância entre história e exame físico',
    'acompanhante_controlador': 'Acompanhante recusa deixar a paciente sozinha / responde por ela',
    'abortos_inexplicados': 'Histórico de abortos espontâneos sem causa identificada',
    'somatizacoes_cronicas': 'Sintomas psicossomáticos crônicos sem causa orgânica',
    'baixa_adesao': 'Baixa adesão ao pré-natal / consultas / tratamentos',
    'ideacao_suicida': 'Relato ou sinais de ideação suicida',
    'gestacao_indesejada': 'Gestação indesejada e sem suporte familiar',
    'isolamento_social': 'Isolamento social acentuado relatado pela paciente',
    'historico_violencia_familiar': 'Histórico familiar de violência',
}


@dataclass
class AvaliacaoViolencia:
    score: int
    sinais_presentes: list[str]
    sinais_descricoes: list[str]
    nivel: Literal['sem_alerta', 'atencao', 'alta_suspeita']
    conduta_sugerida: str
    encaminhamentos: list[str] = field(default_factory=list)


def avaliar_padrao_violencia(sinais: list[str]) -> AvaliacaoViolencia:
    """Recebe uma lista de chaves de SINAIS_VIOLENCIA e devolve avaliação.

    Score = quantidade de sinais presentes. Sinais com peso 2 contam dobrado.
    """
    pesos = {'lesoes_inexplicadas': 2, 'lesoes_multiplas_fases': 2, 'ideacao_suicida': 2}
    sinais_validos = [s for s in sinais if s in SINAIS_VIOLENCIA]
    score = sum(pesos.get(s, 1) for s in sinais_validos)

    if score >= 4:
        nivel = 'alta_suspeita'
        conduta = (
            'Conduzir escuta qualificada em ambiente reservado, SEM acompanhante. '
            'Realizar exame físico completo documentando achados. '
            'NOTIFICAR via SINAN (Ficha de Notificação Compulsória de Violência Interpessoal/Autoprovocada) — '
            'obrigatório mesmo sem confirmação verbal. Acionar serviço social e psicologia hospitalar.'
        )
        encs = [
            'Centro de Referência de Atendimento à Mulher',
            'Delegacia da Mulher (orientar paciente; não é obrigatório por parte da equipe se adulta capaz)',
            'CAPS (se sofrimento mental ou ideação suicida)',
            'Assistência social hospitalar',
            'Psicologia',
        ]
    elif score >= 2:
        nivel = 'atencao'
        conduta = (
            'Aprofundar anamnese em ambiente reservado. Aplicar perguntas-chave da Norma Técnica '
            '(ex.: "alguém em casa tem feito mal a você?"). Documentar achados em prontuário. '
            'Considerar notificação SINAN se houver confirmação de qualquer modalidade de violência.'
        )
        encs = ['Centro de Referência da Mulher (orientar paciente)', 'Psicologia']
    else:
        nivel = 'sem_alerta'
        conduta = 'Sem critérios mínimos para alerta ativo. Manter escuta atenta nas consultas subsequentes.'
        encs = []

    return AvaliacaoViolencia(
        score=score,
        sinais_presentes=sinais_validos,
        sinais_descricoes=[SINAIS_VIOLENCIA[s] for s in sinais_validos],
        nivel=nivel,
        conduta_sugerida=conduta,
        encaminhamentos=encs,
    )


def proximo_periodo_menstrual(conn: sqlite3.Connection, paciente_id: int) -> dict | None:
    """Estima próximo período menstrual a partir do histórico de ciclos."""
    ciclos = conn.execute(
        'SELECT data_inicio FROM ciclos_menstruais WHERE paciente_id = ? '
        'ORDER BY data_inicio DESC LIMIT 6',
        (paciente_id,),
    ).fetchall()
    if len(ciclos) < 2:
        return None
    datas = [date.fromisoformat(r['data_inicio']) for r in ciclos]
    intervalos = [(datas[i] - datas[i + 1]).days for i in range(len(datas) - 1)]
    media = sum(intervalos) / len(intervalos)
    ultimo = datas[0]
    proximo = ultimo + timedelta(days=round(media))
    return {
        'ultimo_inicio': ultimo.isoformat(),
        'intervalo_medio_dias': round(media, 1),
        'proximo_estimado': proximo.isoformat(),
        'janela_fertil_estimada': [
            (proximo - timedelta(days=19)).isoformat(),
            (proximo - timedelta(days=12)).isoformat(),
        ],
    }
