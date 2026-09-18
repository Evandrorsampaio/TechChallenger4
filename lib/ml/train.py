"""Treino dos 4 modelos no split persistido (semente 42)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from lib.config import RANDOM_SEED, artifacts_dir
from lib.ml.baseline import BaselineRegra
from lib.ml.dataset import carregar_xy, caminho_parquet
from lib.ml.features import construir_pipeline
from lib.ml.registry import salvar_modelo

GRID_LOGREG = {'modelo__C': [0.1, 1.0, 10.0], 'modelo__penalty': ['l2']}
GRID_RF = {
    'modelo__n_estimators': [100, 200],
    'modelo__max_depth': [8, 16, None],
    'modelo__min_samples_leaf': [1, 4],
}


def _split(df: pd.DataFrame, nome: str):
    X, y, full = carregar_xy(df)
    mask = full['split'] == nome
    return X.loc[mask], y.loc[mask]


def treinar(df: pd.DataFrame | None = None, seed: int = RANDOM_SEED) -> dict:
    if df is None:
        df = pd.read_parquet(caminho_parquet())
    X_tr, y_tr = _split(df, 'treino')
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    dummy = construir_pipeline(DummyClassifier(strategy='prior', random_state=seed))
    dummy.fit(X_tr, y_tr)

    regra = BaselineRegra()
    regra.fit(X_tr, y_tr)

    logreg = construir_pipeline(
        LogisticRegression(max_iter=1000, class_weight='balanced', random_state=seed)
    )
    gs_lr = GridSearchCV(logreg, GRID_LOGREG, cv=cv, scoring='average_precision', n_jobs=1)
    gs_lr.fit(X_tr, y_tr)

    rf = construir_pipeline(
        RandomForestClassifier(class_weight='balanced', random_state=seed, n_jobs=1)
    )
    gs_rf = GridSearchCV(rf, GRID_RF, cv=cv, scoring='average_precision', n_jobs=1)
    gs_rf.fit(X_tr, y_tr)

    modelos = {
        'dummy_prior': dummy,
        'baseline_regra': regra,
        'logistic_regression': gs_lr.best_estimator_,
        'random_forest': gs_rf.best_estimator_,
    }
    hipers = {
        'dummy_prior': {'strategy': 'prior'},
        'baseline_regra': {'tipo': 'disjuncao_CRITERIOS_ALTO_RISCO'},
        'logistic_regression': gs_lr.best_params_,
        'random_forest': gs_rf.best_params_,
    }
    dest = artifacts_dir() / 'models'
    dest.mkdir(parents=True, exist_ok=True)
    for nome, est in modelos.items():
        salvar_modelo(nome, est, dest / nome)
    return {'modelos': modelos, 'hiperparametros': hipers, 'seed': seed}
