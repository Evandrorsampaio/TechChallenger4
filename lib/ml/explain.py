"""Explicabilidade local com cascata SHAP → coeficientes → permutação."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from lib.config import artifacts_dir
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


def caminho_importancia_global() -> Path:
    return artifacts_dir() / 'explainability' / 'importancia_global.json'


def explicar_permutacao_global(est, X: pd.DataFrame, y, k: int = 5, n_repeats: int = 5) -> dict[str, Any]:
    from sklearn.inspection import permutation_importance

    r = permutation_importance(
        est, X, y, n_repeats=n_repeats, random_state=42, scoring='average_precision', n_jobs=1
    )
    pares = []
    cols = list(X.columns)
    for i, nome in enumerate(cols):
        pares.append((nome, float(r.importances_mean[i]), None))
    return {
        'explanation_method': 'permutacao',
        'explanation_scope': 'global',
        'top_features': _top(pares, k),
        'aviso': (
            'Importância global por permutação (average_precision). '
            'Não interpretar como efeito causal nem como contribuição desta paciente.'
        ),
    }


def _from_cache_global(valores: dict[str, Any], k: int) -> dict[str, Any] | None:
    path = caminho_importancia_global()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    tops = []
    for t in (data.get('top_features') or [])[:k]:
        nome = t.get('feature')
        tops.append(
            {
                'feature': nome,
                'value': valores.get(nome),
                'contribution': t.get('contribution'),
                'direction': t.get('direction'),
            }
        )
    if len(tops) < 3:
        return None
    return {
        'explanation_method': 'permutacao',
        'explanation_scope': 'global',
        'top_features': tops,
        'aviso': data.get('aviso')
        or 'Importância global cacheada. Não interpretar como efeito causal nesta paciente.',
    }


def explicar(
    est,
    features: GestanteFeatures,
    k: int = 5,
    X_ref: pd.DataFrame | None = None,
    y_ref=None,
) -> dict[str, Any]:
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
            tops = _top(pares, k)
            if len(tops) >= 3:
                return {
                    'explanation_method': 'shap_tree_explainer',
                    'explanation_scope': 'local',
                    'top_features': tops,
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
            (
                nomes[i] if i < len(nomes) else f'f{i}',
                float(coef[i] * Xt[i]),
                valores.get(nomes[i] if i < len(nomes) else ''),
            )
            for i in range(n)
        ]
        return {
            'explanation_method': 'coef_linear',
            'explanation_scope': 'local',
            'top_features': _top(pares, k),
            'aviso': None,
        }

    if X_ref is not None and y_ref is not None:
        glob = explicar_permutacao_global(est, X_ref, y_ref, k=k)
        for t in glob['top_features']:
            t['value'] = valores.get(t['feature'])
        return glob

    cached = _from_cache_global(valores, k)
    if cached:
        return cached

    if hasattr(modelo, 'feature_importances_'):
        nomes = _nomes_pos_preprocess(est)
        imps = np.asarray(modelo.feature_importances_).reshape(-1)
        pares = [
            (nomes[i] if i < len(nomes) else f'f{i}', float(imps[i]), valores.get(nomes[i] if i < len(nomes) else None))
            for i in range(len(imps))
        ]
        return {
            'explanation_method': 'permutacao',
            'explanation_scope': 'global',
            'top_features': _top(pares, k),
            'aviso': (
                'SHAP indisponível; contribuições derivadas de importância de impureza do ensemble, '
                'escopo global. Não interpretar como efeito causal nesta paciente.'
            ),
        }

    return {
        'explanation_method': 'permutacao',
        'explanation_scope': 'global',
        'top_features': [],
        'aviso': (
            'Explicação local indisponível e permutação global sem amostra de referência. '
            'Não interpretar ausência de top_features como ausência de risco.'
        ),
    }
