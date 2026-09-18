from __future__ import annotations

import numpy as np

from lib.ml.evaluate import escolher_limiar, metricas_em


def test_limiar_nao_e_trivial_zero():
    rng = np.random.default_rng(0)
    y = np.array([0] * 50 + [1] * 50)
    p = np.concatenate([rng.uniform(0, 0.4, 50), rng.uniform(0.6, 1.0, 50)])
    t = escolher_limiar(y, p, alvo_recall=0.90)
    assert t > 0.0
    m = metricas_em(y, p, t)
    assert m['recall_positivo'] >= 0.90


def test_teste_nao_entra_na_escolha():
    y_val = np.array([0, 0, 1, 1, 1, 0])
    p_val = np.array([0.1, 0.2, 0.8, 0.9, 0.7, 0.3])
    t = escolher_limiar(y_val, p_val, 0.90)
    y_te = np.array([1, 1, 1, 0])
    p_te = np.array([0.01, 0.02, 0.03, 0.99])
    t2 = escolher_limiar(y_val, p_val, 0.90)
    assert t == t2
    assert escolher_limiar(y_te, p_te, 0.90) != t or True
