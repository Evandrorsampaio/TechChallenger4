"""Métricas, limiar operacional, IC bootstrap e análise de erros."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)

from lib.config import RANDOM_SEED, artifacts_dir
from lib.ml.baseline import BaselineRegra
from lib.ml.dataset import carregar_xy, caminho_parquet


def _proba_positiva(est, X) -> np.ndarray:
    if isinstance(est, BaselineRegra):
        return est.predict_proba(X)[:, 1]
    return est.predict_proba(X)[:, 1]


def metricas_em(y_true, y_prob, limiar: float) -> dict:
    y_pred = (y_prob >= limiar).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=[0, 1], zero_division=0
    )
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    npv = tn / (tn + fn) if (tn + fn) else 0.0
    try:
        roc = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        roc = float('nan')
    try:
        pr = float(average_precision_score(y_true, y_prob))
    except ValueError:
        pr = float('nan')
    return {
        'limiar': float(limiar),
        'matriz_confusao': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
        'precision_por_classe': {'habitual': float(prec[0]), 'alto_risco': float(prec[1])},
        'recall_por_classe': {'habitual': float(rec[0]), 'alto_risco': float(rec[1])},
        'f1_por_classe': {'habitual': float(f1[0]), 'alto_risco': float(f1[1])},
        'precision_macro': float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
        'recall_macro': float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
        'f1_macro': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
        'recall_positivo': float(rec[1]),
        'precision_positivo': float(prec[1]),
        'roc_auc': roc,
        'pr_auc': pr,
        'brier': float(brier_score_loss(y_true, y_prob)),
        'especificidade': float(spec),
        'npv': float(npv),
        'acuracia': float(accuracy_score(y_true, y_pred)),
        'acuracia_nao_decisoria': True,
    }


def escolher_limiar(y_true, y_prob, alvo_recall: float = 0.90) -> float:
    """Maior limiar com recall ≥ alvo na validação (ponto mais específico que cumpre o recall).

    Interpretado a partir do requisito 'menor limiar que atinge recall ≥ 0,90' no sentido
    operacional: não usar 0,0 (recall trivial) nem o teste. Varre limiares crescentes e
    retém o último que ainda atinge o alvo.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    candidatos = np.unique(np.concatenate(([0.0], np.sort(y_prob), [1.0])))
    escolhido = 0.0
    for t in candidatos:
        rec = recall_score(y_true, (y_prob >= t).astype(int), pos_label=1, zero_division=0)
        if rec >= alvo_recall:
            escolhido = float(t)
        else:
            if t > 0:
                break
    return escolhido


def bootstrap_ic(y_true, y_prob, limiar: float, n: int = 1000, seed: int = RANDOM_SEED) -> dict:
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    stats = {'recall_positivo': [], 'precision_positivo': [], 'pr_auc': [], 'f1_macro': []}
    for _ in range(n):
        idx = rng.integers(0, len(y_true), size=len(y_true))
        m = metricas_em(y_true[idx], y_prob[idx], limiar)
        for k in stats:
            stats[k].append(m['pr_auc'] if k == 'pr_auc' else m[k] if k != 'f1_macro' else m['f1_macro'])
    out = {}
    for k, vals in stats.items():
        arr = np.asarray(vals, dtype=float)
        out[k] = {
            'ponto': float(np.nanmean(arr)),
            'ic95_low': float(np.nanpercentile(arr, 2.5)),
            'ic95_high': float(np.nanpercentile(arr, 97.5)),
        }
    return out


def analisar_erros(X: pd.DataFrame, y_true, y_prob, limiar: float) -> dict:
    y_pred = (np.asarray(y_prob) >= limiar).astype(int)
    y_true = np.asarray(y_true)
    fn_idx = np.where((y_true == 1) & (y_pred == 0))[0]
    fp_idx = np.where((y_true == 0) & (y_pred == 1))[0]
    fatores = ['has_cronica', 'diabetes_previo', 'gemelaridade', 'idade', 'imc_pre_gestacional']

    def perfil(indices):
        if len(indices) == 0:
            return {'n': 0}
        sub = X.iloc[indices]
        res = {'n': int(len(indices))}
        for f in fatores:
            if f in sub.columns:
                if sub[f].dtype == bool or set(pd.Series(sub[f].dropna().unique())) <= {0, 1, True, False}:
                    res[f'{f}_taxa'] = float(pd.Series(sub[f]).fillna(False).astype(bool).mean())
                else:
                    res[f'{f}_media'] = float(pd.Series(sub[f]).mean())
        return res

    def recorte(col, bins, labels):
        s = pd.cut(X[col], bins=bins, labels=labels, include_lowest=True)
        out = {}
        for lab in labels:
            m = s == lab
            if m.sum() == 0:
                continue
            yt = y_true[m.to_numpy()]
            yp = y_pred[m.to_numpy()]
            out[str(lab)] = {
                'n': int(m.sum()),
                'recall': float(recall_score(yt, yp, pos_label=1, zero_division=0)),
            }
        return out

    return {
        'falsos_negativos': perfil(fn_idx),
        'falsos_positivos': perfil(fp_idx),
        'subgrupo_idade': recorte('idade', [12, 19, 34, 51], ['<=19', '20-34', '>=35']),
        'subgrupo_ig': recorte('ig_semanas', [3, 13, 27, 43], ['T1', 'T2', 'T3']),
    }


def avaliar_modelos(modelos: dict, df: pd.DataFrame | None = None) -> dict:
    if df is None:
        df = pd.read_parquet(caminho_parquet())
    X, y, full = carregar_xy(df)
    dest = artifacts_dir() / 'metrics'
    dest.mkdir(parents=True, exist_ok=True)
    comparacao = {}
    limiares = {}
    for nome, est in modelos.items():
        bloco = {}
        probs = {}
        for split in ('treino', 'validacao', 'teste'):
            mask = full['split'] == split
            Xs, ys = X.loc[mask], y.loc[mask]
            prob = _proba_positiva(est, Xs)
            probs[split] = (ys.to_numpy(), prob)
            if split == 'validacao':
                limiar = escolher_limiar(ys.to_numpy(), prob)
                limiares[nome] = limiar
            else:
                limiar = limiares.get(nome, 0.5)
            met = metricas_em(ys.to_numpy(), prob, limiar)
            met['split'] = split
            met['modelo'] = nome
            met['dataset_version'] = 'v1.0.0'
            bloco[split] = met
            (dest / f'{nome}_{split}.json').write_text(
                json.dumps(met, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
            )
        y_te, p_te = probs['teste']
        bloco['bootstrap_teste'] = bootstrap_ic(y_te, p_te, limiares[nome])
        mask_te = full['split'] == 'teste'
        bloco['analise_erros_teste'] = analisar_erros(
            X.loc[mask_te].reset_index(drop=True), y_te, p_te, limiares[nome]
        )
        comparacao[nome] = bloco
    (dest / 'limiar.json').write_text(
        json.dumps(limiares, indent=2) + '\n', encoding='utf-8'
    )
    (dest / 'comparacao.json').write_text(
        json.dumps(comparacao, indent=2, default=str, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    (dest / 'analise_erros.json').write_text(
        json.dumps({k: v['analise_erros_teste'] for k, v in comparacao.items()}, indent=2, ensure_ascii=False)
        + '\n',
        encoding='utf-8',
    )
    return {'comparacao': comparacao, 'limiares': limiares}
