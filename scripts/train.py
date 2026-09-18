#!/usr/bin/env python3
"""CLI: gerar dataset, verificar hash e treinar modelos."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--gerar-dataset', action='store_true')
    p.add_argument('--verificar-dataset', action='store_true')
    p.add_argument('--avaliar', action='store_true', help='avalia após treinar')
    p.add_argument('--perfilar', action='store_true')
    args = p.parse_args()
    from lib.ml.dataset import gerar_e_salvar, gravar_perfil, verificar_dataset

    if args.gerar_dataset:
        man = gerar_e_salvar()
        print(json.dumps(man, indent=2, ensure_ascii=False))
        return 0
    if args.perfilar:
        path = gravar_perfil()
        print(path)
        return 0
    if args.verificar_dataset:
        print(json.dumps(verificar_dataset(), indent=2))
        return 0

    from lib.ml.evaluate import avaliar_modelos
    from lib.ml.registry import escrever_card, pasta_modelo
    from lib.ml.train import treinar

    out = treinar()
    av = avaliar_modelos(out['modelos'])
    for nome, est in out['modelos'].items():
        met_teste = av['comparacao'][nome]['teste']
        card = {
            'nome': nome,
            'versao': '1.0.0',
            'dataset_version': 'v1.0.0',
            'threshold': av['limiares'][nome],
            'hiperparametros': out['hiperparametros'][nome],
            'metricas_teste': {
                'recall_positivo': met_teste['recall_positivo'],
                'precision_positivo': met_teste['precision_positivo'],
                'pr_auc': met_teste['pr_auc'],
                'roc_auc': met_teste['roc_auc'],
                'f1_macro': met_teste['f1_macro'],
                'brier': met_teste['brier'],
                'acuracia': met_teste['acuracia'],
            },
            'semente': out['seed'],
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'pipeline_version': '1.0.0',
        }
        escrever_card(pasta_modelo(nome), card)
    print('treino ok; limiares=', json.dumps(av['limiares']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
