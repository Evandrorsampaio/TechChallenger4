from __future__ import annotations

import pandas as pd

from lib.ml.dataset import gerar_dataframe, verificar_dataset, salvar_dataset, carregar_xy


def test_duas_geracoes_identicas():
    a = gerar_dataframe(n=8000, seed=42)
    b = gerar_dataframe(n=8000, seed=42)
    pd.testing.assert_frame_equal(a, b)


def test_hash_persistido(tmp_path, monkeypatch):
    monkeypatch.setenv('ARTIFACTS_DIR', str(tmp_path))
    from importlib import reload
    import lib.config as cfg
    reload(cfg)
    import lib.ml.dataset as ds
    reload(ds)
    df = ds.gerar_dataframe(n=8000, seed=42)
    man = ds.salvar_dataset(df, seed=42)
    assert 'sha256' in man
    assert man['natureza'] == 'SINTETICO'
    out = ds.verificar_dataset(n=8000, seed=42)
    assert out['ok'] is True
    assert out['sha256'] == man['sha256']
