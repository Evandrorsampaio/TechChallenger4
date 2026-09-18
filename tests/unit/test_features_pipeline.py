from __future__ import annotations

import joblib

from lib.ml.features import campos_imputados, construir_pipeline, dataframe_de_features
from lib.ml.schema import GestanteFeatures, parse_gestante
from sklearn.linear_model import LogisticRegression

from lib.ml.dataset import carregar_xy, gerar_dataframe


def _ok():
    return parse_gestante(
        dict(
            idade=28,
            imc_pre_gestacional=24.0,
            ig_semanas=20,
            gestacoes=2,
            partos=1,
            abortos=0,
            pas_mmhg=120,
            pad_mmhg=70,
            has_cronica=False,
            diabetes_previo=False,
            gemelaridade=False,
        )
    )


def test_pipeline_serializavel(tmp_path):
    df = gerar_dataframe(n=300, seed=42)
    X, y, full = carregar_xy(df)
    mask = full['split'] == 'treino'
    pipe = construir_pipeline(LogisticRegression(max_iter=200, class_weight='balanced'))
    pipe.fit(X.loc[mask], y.loc[mask])
    dest = tmp_path / 'pipe.joblib'
    joblib.dump(pipe, dest)
    loaded = joblib.load(dest)
    p1 = pipe.predict_proba(X.iloc[:5])
    p2 = loaded.predict_proba(X.iloc[:5])
    assert (p1 == p2).all()


def test_campos_imputados_listados():
    feat = _ok()
    ausentes = campos_imputados(feat)
    assert 'hemoglobina_g_dl' in ausentes
    assert 'idade' not in ausentes


def test_dataframe_uma_linha():
    df = dataframe_de_features(_ok())
    assert df.shape == (1, 24)
