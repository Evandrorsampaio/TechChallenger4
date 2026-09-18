from __future__ import annotations

import numpy as np

from lib.ml.evaluate import bootstrap_ic


def test_bootstrap_reprodutivel():
    y = np.array([0, 1, 0, 1, 1, 0, 1, 0] * 10)
    p = np.linspace(0.1, 0.9, len(y))
    a = bootstrap_ic(y, p, 0.5, n=50, seed=42)
    b = bootstrap_ic(y, p, 0.5, n=50, seed=42)
    assert a == b
