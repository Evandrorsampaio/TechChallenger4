from __future__ import annotations

from lib.ml.dataset import PROIBIDAS_EM_X, carregar_xy, gerar_dataframe
from lib.ml.features import NUM_COLS, construir_preprocessor
from lib.ml.schema import FEATURES


def test_risco_latente_fora_de_x():
    df = gerar_dataframe(n=400, seed=42)
    X, y, _ = carregar_xy(df)
    assert 'risco_latente' not in X.columns
    assert list(X.columns) == list(FEATURES)
    assert 'alto_risco' not in X.columns
    for col in PROIBIDAS_EM_X:
        assert col not in X.columns


def test_preprocessor_fit_so_treino():
    df = gerar_dataframe(n=400, seed=42)
    X, y, full = carregar_xy(df)
    treino = full['split'] == 'treino'
    pre = construir_preprocessor()
    pre.fit(X.loc[treino])
    Xt = pre.transform(X.loc[~treino])
    assert Xt.shape[0] == int((~treino).sum())
    assert Xt.shape[1] > 0
