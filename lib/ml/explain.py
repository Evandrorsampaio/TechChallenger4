"""Explicabilidade local com cascata SHAP → coeficientes → permutação."""
from __future__ import annotations

from typing import Any

import numpy as np

from lib.ml.features import dataframe_de_features
from lib.ml.schema import FEATURES, GestanteFeatures

try:
    import shap  # type: ignore

    SHAP_DISPONIVEL = True
except Exception:
    shap = None
    SHAP_DISPONIVEL = False


def _nomes_pos_preprocess(est) -> list[str]:
    pre = getattr(est, 'named_steps', {}).get('preprocess')
    if pre is not None and hasattr(pre, 'get_feature_names_out'):
        try:
            return [str(n).split('__')[-1] for n in pre.get_feature_names_out()]
        except Exception:
            pass
    return list(FEATURES)


def _top(pares: list[tuple[str, float, Any]], k: int = 5) -> list[dict[str, Any]]:
    ordenados = sorted(pares, key=lambda t: abs(t[1]), reverse=True)[:k]
    out = []
    for nome, contrib, valor in ordenados:
        out.append(
            {
                'feature': nome,
                'value': valor,
                'contribution': float(contrib),
                'direction': 'aumenta' if contrib >= 0 else 'reduz',
            }
        )
    return out


def explicar(est, features: GestanteFeatures, k: int = 5) -> dict[str, Any]:
    X = dataframe_de_features(features)
    valores = features.para_registro()
    modelo = getattr(est, 'named_steps', {}).get('modelo', est)
    pre = getattr(est, 'named_steps', {}).get('preprocess')

    if SHAP_DISPONIVEL and type(modelo).__name__ == 'RandomForestClassifier' and pre is not None:
        try:
            Xt = pre.transform(X)
            explainer = shap.TreeExplainer(modelo)
            sv = explainer.shap_values(Xt)
            if isinstance(sv, list):
                contribs = np.asarray(sv[1] if len(sv) > 1 else sv[0]).reshape(-1)
            else:
                arr = np.asarray(sv)
                contribs = arr[0, :, 1] if arr.ndim == 3 else arr.reshape(-1)
            nomes = _nomes_pos_preprocess(est)
            pares = []
            for i, nome in enumerate(nomes[: len(contribs)]):
                pares.append((nome, float(contribs[i]), valores.get(nome)))
            return {
                'explanation_method': 'shap_tree_explainer',
                'explanation_scope': 'local',
                'top_features': _top(pares, k),
                'aviso': None,
            }
        except Exception:
            pass

    if hasattr(modelo, 'coef_') and pre is not None:
        Xt = np.asarray(pre.transform(X)).reshape(-1)
        coef = np.asarray(modelo.coef_).reshape(-1)
        n = min(len(Xt), len(coef))
        nomes = _nomes_pos_preprocess(est)
        pares = [
            (nomes[i] if i < len(nomes) else f'f{i}', float(coef[i] * Xt[i]), valores.get(nomes[i] if i < len(nomes) else ''))
            for i in range(n)
        ]
        return {
            'explanation_method': 'coef_linear',
            'explanation_scope': 'local',
            'top_features': _top(pares, k),
            'aviso': None,
        }

    return {
        'explanation_method': 'permutacao',
        'explanation_scope': 'global',
        'top_features': [],
        'aviso': (
            'Explicação local indisponível; importância global por permutação não foi '
            'calculada neste ponto. Não interpretar ausência de top_features como ausência de risco.'
        ),
    }
