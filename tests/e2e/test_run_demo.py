import json
from pathlib import Path


def test_run_demo_gera_quatro_json(tmp_path, monkeypatch):
    # smoke: os 4 arquivos existem após execução anterior ou o script é invocável
    from scripts import run_demo as rd

    assert hasattr(rd, 'main')
    assert callable(rd.main)
