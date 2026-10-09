from __future__ import annotations

import pytest
from pydantic import ValidationError

from lib.ml.schema import FEATURES, N_FEATURES, OPCIONAIS, OBRIGATORIAS, GestanteFeatures, parse_gestante


def _ok(**kwargs):
    base = dict(
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
    base.update(kwargs)
    return base


def test_n_features_24():
    assert N_FEATURES == 24
    assert len(FEATURES) == 24
    assert len(OBRIGATORIAS) == 11
    assert len(OPCIONAIS) == 13


def test_payload_valido():
    feat = parse_gestante(_ok())
    assert feat.idade == 28


def test_extra_proibido():
    dados = _ok()
    dados['pressao_arterial_sistolica'] = 120
    with pytest.raises((ValidationError, Exception)):
        parse_gestante(dados)


def test_idade_fora_da_faixa():
    with pytest.raises(Exception) as exc:
        parse_gestante(_ok(idade=12))
    assert 'idade' in str(exc.value).lower() or 'idade' in str(exc.value)
