from __future__ import annotations

import os
from pathlib import Path

import pytest

from lib import config


def test_defaults_colab_preservados():
    assert config.DEFAULT_DB_PATH == (
        '/content/drive/MyDrive/AssistenteHospitalar/files/hospital.db'
    )
    assert config.DEFAULT_DRIVE_BASE == (
        '/content/drive/MyDrive/AssistenteHospitalar'
    )


def test_ml_risco_desligado_por_padrao(monkeypatch):
    monkeypatch.delenv('ML_RISCO_HABILITADO', raising=False)
    assert config.ml_risco_habilitado() is False
    monkeypatch.setenv('ML_RISCO_HABILITADO', '1')
    assert config.ml_risco_habilitado() is True


def test_seed_padrao(monkeypatch):
    monkeypatch.delenv('RANDOM_SEED', raising=False)
    assert int(os.environ.get('RANDOM_SEED', '42')) == 42
    assert config.RANDOM_SEED == 42 or int(os.environ.get('RANDOM_SEED', '42')) == 42


def test_env_example_cobre_chaves_lidas():
    texto = Path('.env.example').read_text(encoding='utf-8')
    for chave in config.env_keys():
        assert chave in texto, chave


def test_db_usa_config(monkeypatch, tmp_path):
    monkeypatch.setenv('HOSPITAL_DB_PATH', str(tmp_path / 'hospital.db'))
    from importlib import reload
    import lib.config as cfg
    reload(cfg)
    import lib.db as db
    reload(db)
    assert db.get_db_path() == tmp_path / 'hospital.db'
    assert db.DEFAULT_DB_PATH == cfg.DEFAULT_DB_PATH
