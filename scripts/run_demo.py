#!/usr/bin/env python3
"""Quatro cenários de demonstração (perfil demo-cpu, FakeChatModel)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CASO_OK = {
    'idade': 28,
    'imc_pre_gestacional': 24.0,
    'ig_semanas': 22,
    'gestacoes': 2,
    'partos': 1,
    'abortos': 0,
    'pas_mmhg': 118,
    'pad_mmhg': 72,
    'has_cronica': False,
    'diabetes_previo': False,
    'gemelaridade': False,
    'escolaridade_anos': 12,
    'cesareas_previas': 0,
    'natimorto_previo': False,
    'pre_eclampsia_previa': False,
    'intervalo_interpartal_meses': 36.0,
    'hemoglobina_g_dl': 12.5,
    'glicemia_jejum_mg_dl': 82.0,
    'proteinuria_fita': 'ausente',
    'cardiopatia': False,
    'nefropatia': False,
    'tev_previo': False,
    'tabagismo': False,
    'infeccao_sexual_ativa': False,
}

from lib.db import init_schema, reset_database
from lib.llm_fake import FakeChatModel
from lib.mock_data import populate
from lib.workflows.risco_ml import build_risco_ml_workflow


class _Doc:
    def __init__(self, text, meta):
        self.page_content = text
        self.metadata = meta


class FakeRetriever:
    def invoke(self, query: str):
        return [
            _Doc(
                'Pré-natal de alto risco: encaminhar à referência regional.',
                {'doc_id': 'ms_prenatal_alto_risco', 'category': 'ginecologia_obstetricia', 'chunk_id': 'c1'},
            )
        ]


def _conn(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def main() -> int:
    dest = ROOT / 'artifacts' / 'demo'
    dest.mkdir(parents=True, exist_ok=True)
    db_path = ROOT / 'artifacts' / 'demo' / 'hospital_demo.db'
    if db_path.exists():
        db_path.unlink()
    conn = _conn(db_path)
    reset_database(conn)
    init_schema(conn)
    populate(conn, seed=42, verbose=False)

    wf = build_risco_ml_workflow(FakeChatModel(), conn, FakeRetriever())
    cenario_alto = dict(CASO_OK)
    cenario_alto.update({'idade': 41, 'has_cronica': True, 'pas_mmhg': 150, 'pad_mmhg': 95})
    incompleto = dict(CASO_OK)
    del incompleto['pas_mmhg']

    casos = [
        ('D1_sucesso', {'dados_clinicos': CASO_OK, 'usuario': 'demo'}),
        ('D2_incompleto', {'dados_clinicos': incompleto, 'usuario': 'demo'}),
        (
            'D3_emergencia',
            {
                'dados_clinicos': CASO_OK,
                'descricao_clinica': 'cefaleia intensa, escotomas e epigastralgia',
                'usuario': 'demo',
            },
        ),
        (
            'D4_degradado',
            {'dados_clinicos': cenario_alto, 'usuario': 'demo', 'forcar_degradado': True},
        ),
    ]
    for nome, payload in casos:
        state = wf.invoke(payload)
        out = state.get('resposta_estruturada') or {}
        (dest / f'{nome}.json').write_text(
            json.dumps(out, indent=2, ensure_ascii=False, default=str) + '\n',
            encoding='utf-8',
        )
        print(nome, out.get('modo'), out.get('prediction'))
    n = conn.execute('SELECT COUNT(*) AS c FROM predicoes_ml').fetchone()['c']
    print('auditoria_linhas', n)
    conn.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
