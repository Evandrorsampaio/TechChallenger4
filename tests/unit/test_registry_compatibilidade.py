from __future__ import annotations

import json

import pytest

from lib.ml.registry import IncompatibilidadeDatasetError, escrever_card, pasta_modelo


def test_recusa_major(tmp_path):
    from lib.ml.registry import carregar_modelo

    pasta = tmp_path / 'm'
    pasta.mkdir()
    escrever_card(pasta, {'dataset_version': '2.0.0', 'nome': 'x'})
    (pasta / 'modelo.joblib').write_bytes(b'')
    import joblib
    from sklearn.dummy import DummyClassifier

    joblib.dump(DummyClassifier(), pasta / 'modelo.joblib')
    with pytest.raises(IncompatibilidadeDatasetError) as exc:
        carregar_modelo(pasta, dataset_version='1.0.0')
    assert '2.0.0' in str(exc.value)
    assert '1.0.0' in str(exc.value)
