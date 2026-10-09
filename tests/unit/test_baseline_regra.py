from __future__ import annotations

import pandas as pd

from lib.ml.baseline import BaselineRegra, criterios_disparados


def test_idade_extrema_dispara():
    hits = criterios_disparados(dict(idade=15, pas_mmhg=110, pad_mmhg=70, imc_pre_gestacional=22, gestacoes=1, partos=0, abortos=0))
    assert 'idade <16 ou >35a' in hits


def test_sem_criterio_nao_dispara():
    hits = criterios_disparados(
        dict(
            idade=28,
            pas_mmhg=110,
            pad_mmhg=70,
            imc_pre_gestacional=22,
            has_cronica=False,
            diabetes_previo=False,
            gemelaridade=False,
            abortos=0,
            cesareas_previas=0,
        )
    )
    assert hits == []


def test_interface_sklearn():
    X = pd.DataFrame(
        [
            dict(idade=40, pas_mmhg=150, pad_mmhg=95, imc_pre_gestacional=36, has_cronica=True, diabetes_previo=False, gemelaridade=False, abortos=0, cesareas_previas=0, cardiopatia=False, nefropatia=False, tev_previo=False, natimorto_previo=False, tabagismo=False, infeccao_sexual_ativa=False, glicemia_jejum_mg_dl=80),
        ]
    )
    est = BaselineRegra().fit(X, [1])
    y = est.predict(X)
    p = est.predict_proba(X)
    assert y[0] == 1
    assert p[0, 1] == 1.0
