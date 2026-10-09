"""Inferência a partir do Pipeline serializado."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from lib.ml.dataset import DATASET_VERSION
from lib.ml.features import campos_imputados, dataframe_de_features
from lib.ml.registry import carregar_modelo, pasta_modelo
from lib.ml.schema import GestanteFeatures, parse_gestante


class ModeloIndisponivelError(RuntimeError):
    pass


SAFETY_NOTICE = (
    'Resultado de apoio à decisão. Não realiza diagnóstico definitivo. '
    'Não substitui profissionais de saúde. Não deve ser utilizado como única fonte de decisão. '
    'Situações críticas devem ser encaminhadas para avaliação humana.'
)
AVISO_SINTETICO = (
    'Modelo treinado em dados sintéticos. Sem validação clínica. '
    'Métricas medem a recuperação de um processo gerador definido por esta equipe.'
)


def features_hash(features: GestanteFeatures) -> str:
    canonic = json.dumps(features.para_registro(), sort_keys=True, default=str)
    return hashlib.sha256(canonic.encode('utf-8')).hexdigest()


def prever(
    dados: dict[str, Any] | GestanteFeatures,
    nome_modelo: str = 'random_forest',
    limiar: float | None = None,
) -> dict[str, Any]:
    features = dados if isinstance(dados, GestanteFeatures) else parse_gestante(dados)
    pasta = pasta_modelo(nome_modelo)
    try:
        est = carregar_modelo(pasta)
    except FileNotFoundError as exc:
        raise ModeloIndisponivelError(
            f'Modelo indisponível em {pasta / "modelo.joblib"}. '
            'Treine com `python scripts/train.py` ou ative o modo degradado.'
        ) from exc
    card = {}
    card_path = pasta / 'model_card.json'
    if card_path.exists():
        import json as _json

        card = _json.loads(card_path.read_text(encoding='utf-8'))
    if limiar is None:
        limiar = float(card.get('threshold', 0.5))
    X = dataframe_de_features(features)
    if hasattr(est, 'predict_proba'):
        proba = est.predict_proba(X)[0]
        if len(proba) == 2:
            p_pos = float(proba[1])
        else:
            p_pos = float(proba[0])
    else:
        p_pos = float(est.predict(X)[0])
    p_pos = min(max(p_pos, 0.0), 1.0)
    rotulo = 'alto_risco' if p_pos >= limiar else 'habitual'
    payload = {
        'model_name': card.get('nome', nome_modelo),
        'model_version': card.get('versao', '1.0.0'),
        'dataset_version': card.get('dataset_version', DATASET_VERSION),
        'prediction': rotulo,
        'threshold': float(limiar),
        'probabilities': {
            'habitual': round(1.0 - p_pos, 6),
            'alto_risco': round(p_pos, 6),
        },
        'dados_imputados': campos_imputados(features),
        'features_hash': features_hash(features),
        'safety_notice': SAFETY_NOTICE,
        'aviso_dados_sinteticos': AVISO_SINTETICO,
    }
    assert rotulo == 'alto_risco' or p_pos < limiar
    assert (rotulo == 'alto_risco') == (payload['probabilities']['alto_risco'] >= limiar - 1e-12)
    return payload
