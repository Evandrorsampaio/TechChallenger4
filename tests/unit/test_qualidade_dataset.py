from lib.ml.dataset import perfilar
from lib.ml.schema import N_FEATURES


def test_perfil_mede_n_e_prevalencia():
    from lib.ml.dataset import gerar_dataframe

    df = gerar_dataframe(n=400, seed=42)
    p = perfilar(df)
    assert p['n'] == 400
    assert p['n_features'] == N_FEATURES
    assert 0.0 < p['prevalencia_alto_risco'] < 1.0
    assert p['natureza'] == 'SINTETICO'
