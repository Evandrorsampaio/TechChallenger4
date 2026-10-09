from __future__ import annotations

import pandas as pd

from lib.ml.dataset import N_REGISTROS, gerar_dataframe
from lib.ml.schema import FEATURES, N_FEATURES


def test_contrato_8000_e_24_features():
    df = gerar_dataframe(n=N_REGISTROS, seed=42)
    assert len(df) == 8000
    for col in FEATURES:
        assert col in df.columns
    assert len(FEATURES) == N_FEATURES == 24
    prev = float(df['alto_risco'].mean())
    assert abs(prev - 0.22) <= 0.02
    assert set(df['split'].unique()) == {'treino', 'validacao', 'teste'}
    assert df['risco_latente'].between(0, 1).all()
    assert (df['partos'] + df['abortos'] <= df['gestacoes']).all()
    assert (df['pad_mmhg'] < df['pas_mmhg']).all()
