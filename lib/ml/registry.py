"""Versionamento de modelos serializados."""
from __future__ import annotations

import json
from pathlib import Path

import joblib

from lib.ml.dataset import DATASET_VERSION


class IncompatibilidadeDatasetError(RuntimeError):
    pass


def salvar_modelo(nome: str, estimador, pasta: Path) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimador, pasta / 'modelo.joblib')
    return pasta / 'modelo.joblib'


def escrever_card(pasta: Path, card: dict) -> Path:
    dest = pasta / 'model_card.json'
    dest.write_text(json.dumps(card, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return dest


def carregar_modelo(pasta: Path, dataset_version: str = DATASET_VERSION):
    card_path = pasta / 'model_card.json'
    if card_path.exists():
        card = json.loads(card_path.read_text(encoding='utf-8'))
        dv = card.get('dataset_version', '')
        if dv.split('.')[0] != dataset_version.split('.')[0]:
            raise IncompatibilidadeDatasetError(
                f'MAJOR incompatível: modelo treinado em dataset {dv}, '
                f'corrente {dataset_version}'
            )
    modelo_path = pasta / 'modelo.joblib'
    if not modelo_path.exists():
        raise FileNotFoundError(modelo_path)
    return joblib.load(modelo_path)


def pasta_modelo(nome: str) -> Path:
    from lib.config import artifacts_dir

    return artifacts_dir() / 'models' / nome
