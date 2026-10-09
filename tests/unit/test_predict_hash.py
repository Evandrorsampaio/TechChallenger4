from lib.ml.predict import features_hash, parse_gestante
from tests.conftest import CASO_OK


def test_hash_estavel():
    a = features_hash(parse_gestante(CASO_OK))
    b = features_hash(parse_gestante(CASO_OK))
    assert a == b
    assert len(a) == 64
