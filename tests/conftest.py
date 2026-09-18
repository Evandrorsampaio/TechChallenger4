"""Fixtures compartilhadas: banco temp, FakeChatModel, retriever falso, casos."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from lib.db import init_schema
from lib.llm_fake import FakeChatModel

try:
    import langchain

    if not hasattr(langchain, 'debug'):
        langchain.debug = False
    if not hasattr(langchain, 'verbose'):
        langchain.verbose = False
except Exception:
    pass


class _Doc:
    def __init__(self, text: str, meta: dict):
        self.page_content = text
        self.metadata = meta


class FakeRetriever:
    def invoke(self, query: str):
        return [
            _Doc(
                'Pré-natal de alto risco: encaminhar à referência regional.',
                {
                    'doc_id': 'ms_prenatal_alto_risco',
                    'category': 'ginecologia_obstetricia',
                    'chunk_id': 'c1',
                },
            ),
            _Doc(
                'Pré-natal de risco habitual: consultas mensais até 28 semanas.',
                {
                    'doc_id': 'ms_prenatal_habitual',
                    'category': 'ginecologia_obstetricia',
                    'chunk_id': 'c2',
                },
            ),
        ]


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


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def conn_tmp(tmp_path):
    db = tmp_path / 'hospital.db'
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    yield conn
    conn.close()


@pytest.fixture
def fake_chat():
    return FakeChatModel()


@pytest.fixture
def fake_retriever():
    return FakeRetriever()
