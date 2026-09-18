"""Contrato do payload de explicabilidade (caminho feliz LogReg)."""
from sklearn.linear_model import LogisticRegression

from lib.ml.explain import explicar
from lib.ml.features import construir_pipeline, dataframe_de_features
from lib.ml.schema import GestanteFeatures
from tests.conftest import CASO_OK


def test_payload_tem_metodo_escopo_e_tres_features():
    feat = GestanteFeatures.model_validate(CASO_OK)
    pipe = construir_pipeline(LogisticRegression(max_iter=200))
    X = dataframe_de_features(feat)
    Xs = X.loc[[0, 0]].reset_index(drop=True)
    pipe.fit(Xs, [0, 1])
    out = explicar(pipe, feat)
    assert set(out) >= {'explanation_method', 'explanation_scope', 'top_features', 'aviso'}
    assert out['explanation_method'] == 'coef_linear'
    assert out['explanation_scope'] == 'local'
    assert len(out['top_features']) >= 3
    for item in out['top_features']:
        assert set(item) >= {'feature', 'value', 'contribution', 'direction'}
        assert item['direction'] in {'aumenta', 'reduz'}
