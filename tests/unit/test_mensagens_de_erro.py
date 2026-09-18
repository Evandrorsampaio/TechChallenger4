from __future__ import annotations

import pytest

from lib.ml.schema import parse_gestante


def test_mensagem_cita_campo_valor_faixa():
    with pytest.raises(Exception) as exc:
        parse_gestante(
            dict(
                idade=99,
                imc_pre_gestacional=24.0,
                ig_semanas=20,
                gestacoes=1,
                partos=0,
                abortos=0,
                pas_mmhg=120,
                pad_mmhg=70,
                has_cronica=False,
                diabetes_previo=False,
                gemelaridade=False,
            )
        )
    msg = str(exc.value)
    assert 'idade' in msg
    assert '99' in msg
    assert '13' in msg or '50' in msg or 'faixa' in msg.lower() or 'le=50' in msg or '50' in msg
