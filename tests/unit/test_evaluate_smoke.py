"""Smoke de avaliação usando o Dummy já serializado."""
from __future__ import annotations

from lib.ml.evaluate import avaliar_modelos, analisar_erros, metricas_em
from lib.ml.registry import carregar_modelo, pasta_modelo, salvar_modelo
from lib.ml.baseline import BaselineRegra
from pathlib import Path
import numpy as np
import pandas as pd


def test_avaliar_dummy_serializado():
    est = carregar_modelo(pasta_modelo('dummy_prior'))
    av = avaliar_modelos({'dummy_prior': est})
    assert av['limiares']['dummy_prior'] >= 0
    assert 'teste' in av['comparacao']['dummy_prior']


def test_analisar_erros_vazio():
    X = pd.DataFrame({
        'has_cronica': [False, False],
        'diabetes_previo': [False, False],
        'gemelaridade': [False, False],
        'idade': [20, 30],
        'imc_pre_gestacional': [22.0, 24.0],
        'ig_semanas': [10, 20],
    })
    y = np.array([0, 1])
    p = np.array([0.1, 0.9])
    out = analisar_erros(X, y, p, 0.5)
    assert out['falsos_negativos']['n'] == 0
    assert 'subgrupo_idade' in out


def test_salvar_modelo_tmp(tmp_path):
    est = BaselineRegra()
    dest = salvar_modelo('x', est, tmp_path / 'x')
    assert dest.exists()
