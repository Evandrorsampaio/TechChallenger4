from lib.ml.explain import explicar
from lib.ml.schema import GestanteFeatures
from sklearn.dummy import DummyClassifier

from lib.ml.features import construir_pipeline, dataframe_de_features


def test_explain_fallback_nao_quebra():
    feat = GestanteFeatures(
        idade=28, imc_pre_gestacional=24, ig_semanas=20, gestacoes=1, partos=0, abortos=0,
        pas_mmhg=110, pad_mmhg=70, has_cronica=False, diabetes_previo=False, gemelaridade=False,
    )
    pipe = construir_pipeline(DummyClassifier(strategy='prior'))
    X = dataframe_de_features(feat)
    y = [0]
    pipe.fit(X, y)
    out = explicar(pipe, feat)
    assert out['explanation_method']
    assert 'top_features' in out
