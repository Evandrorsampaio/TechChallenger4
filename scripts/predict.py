#!/usr/bin/env python3
"""Predição CLI a partir de JSON (stdin ou --arquivo)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--arquivo', type=Path)
    p.add_argument('--modelo', default='random_forest')
    args = p.parse_args()
    if args.arquivo:
        dados = json.loads(args.arquivo.read_text(encoding='utf-8'))
    else:
        dados = json.loads(sys.stdin.read())
    from lib.ml.explain import explicar
    from lib.ml.predict import prever
    from lib.ml.registry import carregar_modelo, pasta_modelo
    from lib.ml.schema import parse_gestante

    payload = prever(dados, nome_modelo=args.modelo)
    try:
        est = carregar_modelo(pasta_modelo(args.modelo))
        expl = explicar(est, parse_gestante(dados))
        payload.update({k: expl[k] for k in ('explanation_method', 'explanation_scope', 'top_features')})
        if expl.get('aviso'):
            payload['aviso_explicacao'] = expl['aviso']
    except Exception as exc:
        payload['explanation_method'] = 'indisponivel'
        payload['top_features'] = []
        payload['aviso_explicacao'] = str(exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
