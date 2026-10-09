"""Regressão da Fase 3: tools, grafos, flag ML desligada."""
from __future__ import annotations

import os

from lib.tools import build_langchain_tools
from lib.workflows.obstetrico import build_obstetrico_workflow
from tests.conftest import FakeRetriever


def test_dez_tools(conn_tmp, fake_retriever):
    tools = build_langchain_tools(conn_tmp, fake_retriever)
    nomes = [t.name for t in tools]
    assert len(tools) == 10
    assert 'predizer_risco_gestacional' in nomes
    assert 'buscar_protocolo' in nomes
    for t in tools:
        assert getattr(t, 'args_schema', None) is not None


def test_obstetrico_flag_off_sem_no_ml(monkeypatch):
    monkeypatch.setenv('ML_RISCO_HABILITADO', '0')
    import importlib
    import inspect

    import lib.config as cfg
    import lib.workflows.obstetrico as obst

    importlib.reload(cfg)
    importlib.reload(obst)
    assert cfg.ml_risco_habilitado() is False
    src = inspect.getsource(obst.build_obstetrico_workflow)
    assert 'if ml_risco_habilitado()' in src
    assert "g.add_edge('avaliar_risco_gestacional', 'detectar_alertas_urgencia')" in src
