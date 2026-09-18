"""Configuração por variável de ambiente.

Defaults Colab são preservados para os notebooks 05–10 continuarem executáveis.
Módulos novos devem ler caminhos e flags daqui — nunca literais espalhados.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Defaults da Fase 3 (Colab + Drive). Não alterar sem ADR.
DEFAULT_DB_PATH = '/content/drive/MyDrive/AssistenteHospitalar/files/hospital.db'
DEFAULT_DRIVE_BASE = '/content/drive/MyDrive/AssistenteHospitalar'

REPO_ROOT = Path(__file__).resolve().parent.parent

RANDOM_SEED = int(os.environ.get('RANDOM_SEED', '42'))
DATASET_VERSION = os.environ.get('DATASET_VERSION', 'v1.0.0')
CONTRATO_VERSION = 'v1.0.0'
GERADOR_VERSION = '1.0.0'

# Data de referência alinhada a lib/mock_data.py (não importar mock_data daqui).
REFERENCE_DATE = date(2026, 5, 22)


def hospital_db_path() -> Path:
    return Path(os.environ.get('HOSPITAL_DB_PATH', DEFAULT_DB_PATH))


def drive_base() -> Path:
    return Path(os.environ.get('DRIVE_BASE', DEFAULT_DRIVE_BASE))


def hf_token() -> str | None:
    token = os.environ.get('HF_TOKEN')
    return token if token else None


def perfil_execucao() -> str:
    valor = os.environ.get('PERFIL_EXECUCAO', 'ml-only').strip().lower()
    if valor not in {'ml-only', 'demo-cpu', 'full-gpu'}:
        return 'ml-only'
    return valor


def ml_risco_habilitado() -> bool:
    return os.environ.get('ML_RISCO_HABILITADO', '0') == '1'


def artifacts_dir() -> Path:
    raw = os.environ.get('ARTIFACTS_DIR')
    if raw:
        return Path(raw)
    return REPO_ROOT / 'artifacts'


def env_keys() -> tuple[str, ...]:
    """Chaves lidas por este módulo — devem existir em .env.example."""
    return (
        'HOSPITAL_DB_PATH',
        'DRIVE_BASE',
        'HF_TOKEN',
        'PERFIL_EXECUCAO',
        'ML_RISCO_HABILITADO',
        'ARTIFACTS_DIR',
        'RANDOM_SEED',
        'DATASET_VERSION',
    )
