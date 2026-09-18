from __future__ import annotations

import pytest

from lib.ml.schema import DadosIncompletosError, parse_gestante


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


def test_gesta_inconsistente():
    with pytest.raises(Exception) as exc:
        parse_gestante(_ok(gestacoes=1, partos=1, abortos=1))
    msg = str(exc.value)
    assert 'gestacoes' in msg or 'partos' in msg
    assert '1' in msg


def test_pad_maior_que_pas():
    with pytest.raises(Exception) as exc:
        parse_gestante(_ok(pas_mmhg=100, pad_mmhg=110))
    msg = str(exc.value)
    assert 'pad_mmhg' in msg
    assert '100' in msg or '110' in msg


def test_lista_campos_faltantes():
    dados = _ok()
    del dados['idade']
    del dados['gemelaridade']
    with pytest.raises(DadosIncompletosError) as exc:
        parse_gestante(dados)
    assert set(exc.value.campos_faltantes) == {'idade', 'gemelaridade'}
