"""Baseline determinístico: disjunção de CRITERIOS_ALTO_RISCO sobre features cruas.

A mesma função alimenta a comparação de modelos e o modo degradado do workflow.
Critérios sem feature no contrato (malformação fetal, isoimunização Rh, álcool/drogas)
não disparam — limitação documentada.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin

from lib.ml.schema import FEATURES


def criterios_disparados(row: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    idade = row.get('idade')
    if idade is not None and (idade < 16 or idade > 35):
        hits.append('idade <16 ou >35a')
    has = row.get('has_cronica')
    pas = row.get('pas_mmhg')
    pad = row.get('pad_mmhg')
    if has or (pas is not None and pas >= 140) or (pad is not None and pad >= 90):
        hits.append('HAS prévia ou induzida')
    dm = row.get('diabetes_previo')
    glic = row.get('glicemia_jejum_mg_dl')
    if dm or (glic is not None and glic >= 126):
        hits.append('DM prévio ou gestacional')
    if row.get('cardiopatia'):
        hits.append('cardiopatia')
    if row.get('nefropatia'):
        hits.append('nefropatia')
    if row.get('tev_previo'):
        hits.append('TEV prévio')
    ces = row.get('cesareas_previas')
    if ces is not None and ces >= 2:
        hits.append('cesárea prévia (≥2)')
    abortos = row.get('abortos')
    if abortos is not None and abortos >= 2:
        hits.append('abortamento de repetição (≥2)')
    if row.get('natimorto_previo'):
        hits.append('natimorto prévio')
    if row.get('gemelaridade'):
        hits.append('gemelaridade')
    imc = row.get('imc_pre_gestacional')
    if imc is not None and imc >= 35:
        hits.append('IMC ≥35')
    if row.get('tabagismo'):
        hits.append('tabagismo / álcool / drogas')
    if row.get('infeccao_sexual_ativa'):
        hits.append('HIV / sífilis / hepatites')
    return hits


def predizer_regra_frame(X: pd.DataFrame) -> np.ndarray:
    flags = []
    for rec in X.to_dict(orient='records'):
        flags.append(1 if criterios_disparados(rec) else 0)
    return np.asarray(flags, dtype=int)


class BaselineRegra(BaseEstimator, ClassifierMixin):
    """Estimador sklearn: P=1 se qualquer critério dispara, senão P=0."""

    def fit(self, X, y=None):
        self.classes_ = np.array([0, 1])
        return self

    def predict(self, X):
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=list(FEATURES))
        return predizer_regra_frame(X)

    def predict_proba(self, X):
        y = self.predict(X)
        p = y.astype(float)
        return np.column_stack([1.0 - p, p])
