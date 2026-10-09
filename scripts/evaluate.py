#!/usr/bin/env python3
"""Reavalia modelos salvos sem retreinar."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from lib.ml.evaluate import avaliar_modelos
    from lib.ml.registry import carregar_modelo, pasta_modelo

    nomes = ('dummy_prior', 'baseline_regra', 'logistic_regression', 'random_forest')
    modelos = {n: carregar_modelo(pasta_modelo(n)) for n in nomes}
    av = avaliar_modelos(modelos)
    print(json.dumps(av['limiares'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
