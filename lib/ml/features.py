"""Pipeline sklearn de features — fit somente no treino."""
from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder, StandardScaler

from lib.ml.schema import FEATURES, OPCIONAIS, PROTEINURIA_NIVEIS, GestanteFeatures

BOOL_COLS = [
    'has_cronica',
    'diabetes_previo',
    'gemelaridade',
    'natimorto_previo',
    'pre_eclampsia_previa',
    'cardiopatia',
    'nefropatia',
    'tev_previo',
    'tabagismo',
    'infeccao_sexual_ativa',
]
CAT_COLS = ['proteinuria_fita']
NUM_COLS = [c for c in FEATURES if c not in BOOL_COLS and c not in CAT_COLS]


def _bool_as_float(X):
    import numpy as np

    return np.asarray(X, dtype=float)


def construir_preprocessor() -> ColumnTransformer:
    num = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
        ]
    )
    booleanas = Pipeline(
        steps=[
            ('to_float', FunctionTransformer(_bool_as_float, validate=False, feature_names_out='one-to-one')),
            ('imputer', SimpleImputer(strategy='most_frequent')),
        ]
    )
    cats = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='desconhecido')),
            (
                'ord',
                OrdinalEncoder(
                    categories=[list(PROTEINURIA_NIVEIS) + ['desconhecido']],
                    handle_unknown='use_encoded_value',
                    unknown_value=-1,
                ),
            ),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ('num', num, NUM_COLS),
            ('bool', booleanas, BOOL_COLS),
            ('cat', cats, CAT_COLS),
        ],
        remainder='drop',
    )


def construir_pipeline(estimador) -> Pipeline:
    return Pipeline(
        steps=[
            ('preprocess', construir_preprocessor()),
            ('modelo', estimador),
        ]
    )


def dataframe_de_features(features: GestanteFeatures | dict[str, Any]) -> pd.DataFrame:
    if isinstance(features, GestanteFeatures):
        dados = features.para_registro()
    else:
        dados = dict(features)
    return pd.DataFrame([{c: dados.get(c) for c in FEATURES}])


def campos_imputados(features: GestanteFeatures) -> list[str]:
    return [c for c in OPCIONAIS if getattr(features, c) is None]
