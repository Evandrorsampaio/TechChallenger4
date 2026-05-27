"""Conexão e bootstrap de schema do SQLite mock do hospital.

Default path: /content/drive/MyDrive/AssistenteHospitalar/files/hospital.db (Colab).
Override via env var HOSPITAL_DB_PATH para uso local.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = '/content/drive/MyDrive/AssistenteHospitalar/files/hospital.db'


def get_db_path() -> Path:
    return Path(os.environ.get('HOSPITAL_DB_PATH', DEFAULT_DB_PATH))


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path else get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False permite uso cross-thread (Gradio cria threads por requisição).
    # SQLite serializa writes internamente, então é seguro pra workload de demo (1 usuário).
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pacientes (
    paciente_id     INTEGER PRIMARY KEY,
    nome            TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    cpf_hash        TEXT NOT NULL,
    convenio        TEXT,
    cadastro_em     DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS prontuario_gineco (
    id                    INTEGER PRIMARY KEY,
    paciente_id           INTEGER UNIQUE NOT NULL,
    menarca_idade         INTEGER,
    g_p_a                 TEXT,                  -- ex 'G2P1A0'
    dum                   DATE,
    metodo_contraceptivo  TEXT,
    historico_familiar    TEXT,
    observacoes           TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);

CREATE TABLE IF NOT EXISTS exames (
    id                   INTEGER PRIMARY KEY,
    paciente_id          INTEGER NOT NULL,
    tipo                 TEXT NOT NULL,         -- 'papanicolau','mamografia','usg_mamaria','usg_pelvica','colposcopia'
    data_realizacao      DATE NOT NULL,
    resultado            TEXT,
    proximo_recomendado  DATE,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);
CREATE INDEX IF NOT EXISTS idx_exames_pac_tipo ON exames(paciente_id, tipo, data_realizacao);

CREATE TABLE IF NOT EXISTS registros_violencia (
    id                INTEGER PRIMARY KEY,
    paciente_id       INTEGER NOT NULL,
    tipo              TEXT NOT NULL,            -- 'fisica','psicologica','sexual','patrimonial','moral'
    data_atendimento  DATE NOT NULL,
    notificado_sinan  INTEGER NOT NULL,         -- 0/1
    encaminhamentos   TEXT,
    observacoes       TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);

CREATE TABLE IF NOT EXISTS log_acesso (
    id           INTEGER PRIMARY KEY,
    timestamp    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario      TEXT NOT NULL,
    tabela       TEXT NOT NULL,
    paciente_id  INTEGER,
    motivo       TEXT
);
CREATE INDEX IF NOT EXISTS idx_log_pac ON log_acesso(paciente_id, timestamp);

CREATE TABLE IF NOT EXISTS medicamentos (
    id                    INTEGER PRIMARY KEY,
    nome_principio_ativo  TEXT NOT NULL,
    nome_comercial        TEXT,
    indicacoes            TEXT,
    contraindicacoes      TEXT,
    categoria_gestacao    TEXT,                  -- 'A','B','C','D','X'
    categoria_lactacao    TEXT                   -- 'compativel','cautela','contraindicado'
);

CREATE TABLE IF NOT EXISTS ciclos_menstruais (
    id            INTEGER PRIMARY KEY,
    paciente_id   INTEGER NOT NULL,
    data_inicio   DATE NOT NULL,
    duracao_dias  INTEGER NOT NULL,
    sintomas      TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);
CREATE INDEX IF NOT EXISTS idx_ciclos_pac ON ciclos_menstruais(paciente_id, data_inicio);
"""


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def reset_database(conn: sqlite3.Connection) -> None:
    """Apaga e recria todas as tabelas. USE COM CUIDADO."""
    tables = [
        'ciclos_menstruais', 'medicamentos', 'log_acesso',
        'registros_violencia', 'exames', 'prontuario_gineco', 'pacientes',
    ]
    for t in tables:
        conn.execute(f'DROP TABLE IF EXISTS {t}')
    conn.commit()
    init_schema(conn)
