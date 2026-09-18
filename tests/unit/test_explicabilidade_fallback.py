"""Testes da cascata de explicabilidade, inclusive sem shap."""
from __future__ import annotations

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from lib.ml.explain import explicar, explicar_permutacao_global
from lib.ml.features import construir_pipeline, dataframe_de_features
from lib.ml.schema import GestanteFeatures
from tests.conftest import CASO_OK


def _feat():
    return GestanteFeatures.model_validate(CASO_OK)


def _repeat(X, n):
    return pd.concat([X] * n, ignore_index=True)


def test_import_sem_shap_nao_quebra(monkeypatch):
    import lib.ml.explain as ex

    monkeypatch.setattr(ex, 'SHAP_DISPONIVEL', False)
    monkeypatch.setattr(ex, 'shap', None)
    feat = _feat()
    pipe = construir_pipeline(LogisticRegression(max_iter=200))
    X = dataframe_de_features(feat)
    Xs = pd.concat([X, X], ignore_index=True)
    pipe.fit(Xs, [0, 1])
    out = ex.explicar(pipe, feat)
    assert out['explanation_method'] == 'coef_linear'
    assert out['explanation_scope'] == 'local'
    assert len(out['top_features']) >= 3
    assert {t['direction'] for t in out['top_features']} <= {'aumenta', 'reduz'}


def test_permutacao_global_dummy():
    feat = _feat()
    pipe = construir_pipeline(DummyClassifier(strategy='prior'))
    X = dataframe_de_features(feat)
    Xs = _repeat(X, 40)
    y = [0] * 30 + [1] * 10
    pipe.fit(Xs, y)
    out = explicar_permutacao_global(pipe, Xs, y, k=5, n_repeats=2)
    assert out['explanation_method'] == 'permutacao'
    assert out['explanation_scope'] == 'global'
    aviso = (out.get('aviso') or '').lower()
    assert 'causal' in aviso and 'não' in aviso


def test_rf_sem_shap_usa_permutacao(monkeypatch):
    import lib.ml.explain as ex

    monkeypatch.setattr(ex, 'SHAP_DISPONIVEL', False)
    feat = _feat()
    pipe = construir_pipeline(RandomForestClassifier(n_estimators=8, random_state=42))
    X = dataframe_de_features(feat)
    Xs = _repeat(X, 20)
    y = [0, 1] * 10
    pipe.fit(Xs, y)
    out = ex.explicar(pipe, feat, X_ref=Xs, y_ref=y)
    assert out['explanation_method'] == 'permutacao'
    assert out['explanation_scope'] == 'global'
    assert len(out['top_features']) >= 3
