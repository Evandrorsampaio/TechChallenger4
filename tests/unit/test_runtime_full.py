from __future__ import annotations

from lib.config import REPO_ROOT
from lib.runtime_full import (
    chroma_dir_configurado,
    decidir_4bit,
    device_embeddings,
    hospital_db_full,
    origem_adapter,
    resolver_adapter,
)


def test_adapter_explicito(tmp_path):
    pasta = tmp_path / 'adapter_final'
    pasta.mkdir()
    (pasta / 'adapter_config.json').write_text('{}', encoding='utf-8')
    assert resolver_adapter(str(pasta)) == pasta


def test_adapter_descobre_run(tmp_path):
    run = tmp_path / 'llama32-3b-saude-mulher_20260522' / 'adapter_final'
    run.mkdir(parents=True)
    (run / 'adapter_config.json').write_text('{}', encoding='utf-8')
    assert resolver_adapter(str(tmp_path)) == run


def test_sem_adapter(tmp_path):
    assert resolver_adapter(str(tmp_path / 'vazio')) is None
    assert resolver_adapter(None, None) is None


def test_caminhos_locais_quando_env_vazio(monkeypatch):
    monkeypatch.delenv('CHROMA_PATH', raising=False)
    monkeypatch.delenv('HOSPITAL_DB_PATH', raising=False)
    monkeypatch.delenv('ADAPTER_DIR', raising=False)
    monkeypatch.delenv('FINETUNE_DIR', raising=False)
    monkeypatch.setenv('CHROMA_PATH', '')
    monkeypatch.setenv('HOSPITAL_DB_PATH', '')
    assert chroma_dir_configurado() == REPO_ROOT / 'files' / 'chroma'
    assert hospital_db_full() == REPO_ROOT / 'files' / 'hospital.db'
    assert origem_adapter() == (None, str(REPO_ROOT / 'files' / 'finetune'))


def test_chroma_respeita_env(monkeypatch, tmp_path):
    monkeypatch.setenv('CHROMA_PATH', str(tmp_path))
    assert chroma_dir_configurado() == tmp_path


def test_4bit_so_com_cuda():
    assert decidir_4bit(True, None) is True
    assert decidir_4bit(False, None) is False
    assert decidir_4bit(False, '1') is False
    assert decidir_4bit(True, '0') is False
    assert device_embeddings(True) == 'cuda'
    assert device_embeddings(False) == 'cpu'
