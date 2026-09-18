from __future__ import annotations

import pytest

from lib.ml.schema import DadosIncompletosError, DominioInvalidoError, parse_gestante


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


def test_obrigatorio_ausente_nao_imputa():
    dados = _ok()
    del dados['pas_mmhg']
    with pytest.raises(DadosIncompletosError) as exc:
        parse_gestante(dados)
    assert 'pas_mmhg' in exc.value.campos_faltantes


def test_obrigatorio_none():
    with pytest.raises(DadosIncompletosError) as exc:
        parse_gestante(_ok(has_cronica=None))
    assert 'has_cronica' in exc.value.campos_faltantes


def test_chave_errada_nomeada():
    dados = _ok()
    dados['pressao_arterial_sistolica'] = 140
    with pytest.raises(Exception) as exc:
        parse_gestante(dados)
    assert 'pressao_arterial_sistolica' in str(exc.value)
