"""Gerador sintético determinístico de risco gestacional (contrato v1.0.0)."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from lib.config import RANDOM_SEED, artifacts_dir
from lib.ml.schema import FEATURES, N_FEATURES, PROTEINURIA_NIVEIS

DATASET_VERSION = 'v1.0.0'
GERADOR_VERSION = '1.0.0'
N_REGISTROS = 8000
CONTRATO_VERSION = 'v1.0.0'
UUID_NS = uuid.uuid5(uuid.NAMESPACE_URL, 'https://techchallenger4.local/risco-gestacional/v1')

COLUNAS_RASTREIO = ('registro_id', 'dataset_version', 'split', 'risco_latente')
COLUNA_ALVO = 'alto_risco'
PROIBIDAS_EM_X = frozenset({*COLUNAS_RASTREIO, COLUNA_ALVO})

PROTEINURIA_PAS_BAIXA = np.array([0.72, 0.15, 0.08, 0.035, 0.015])
PROTEINURIA_PAS_ALTA = np.array([0.45, 0.20, 0.18, 0.11, 0.06])


def _sigmoid(z: np.ndarray | float) -> np.ndarray | float:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _trunc_normal(rng: np.random.Generator, mu: float, sigma: float, lo: float, hi: float) -> float:
    for _ in range(64):
        x = float(rng.normal(mu, sigma))
        if lo <= x <= hi:
            return x
    return float(np.clip(rng.normal(mu, sigma), lo, hi))


def _escore_latente(row: dict[str, Any]) -> float:
    # Intercepto calibrado para prevalência ≈ 0,22 com semente 42 (spec original −3,10
    # produzia ~0,09 nesta amostragem). Mudança registrada no gerador 1.0.0, antes
    # de qualquer manifesto versionado.
    z = -1.80
    z += 1.60 * int(row['has_cronica'])
    z += 1.45 * int(row['diabetes_previo'])
    z += 1.70 * int(row['pre_eclampsia_previa'])
    z += 1.90 * int(row['cardiopatia'])
    z += 1.75 * int(row['nefropatia'])
    z += 1.30 * int(row['gemelaridade'])
    z += 1.20 * int(row['tev_previo'])
    z += 1.10 * int(row['natimorto_previo'])
    z += 0.38 * (row['pas_mmhg'] - 120) / 10.0
    z += 0.32 * (row['pad_mmhg'] - 75) / 10.0
    z += 0.34 * (row['imc_pre_gestacional'] - 24) / 5.0
    if row['idade'] < 16:
        z += 1.15
    if row['idade'] >= 28:
        z += 0.40 * (row['idade'] - 28) / 10.0
    if row['abortos'] >= 2:
        z += 0.75
    if row['cesareas_previas'] >= 2:
        z += 0.60
    z += 0.85 * int(row['infeccao_sexual_ativa'])
    z += 0.45 * int(row['tabagismo'])
    prot = row['proteinuria_fita']
    if prot in {'1+', '2+', '3+'}:
        z += 0.95
    if row['hemoglobina_g_dl'] < 11:
        z += 0.50
    if row['glicemia_jejum_mg_dl'] >= 92:
        z += 0.55
    intervalo = row['intervalo_interpartal_meses']
    if intervalo is not None and intervalo < 18:
        z += 0.40
    z += -0.04 * row['escolaridade_anos']
    if row['idade'] >= 35 and row['has_cronica']:
        z += 0.80
    if row['imc_pre_gestacional'] >= 30 and row['diabetes_previo']:
        z += 0.70
    if row['gemelaridade']:
        z += 0.45 * (row['pas_mmhg'] - 120) / 10.0
    return float(z)


def _gerar_linha(rng: np.random.Generator) -> dict[str, Any]:
    idade = int(round(_trunc_normal(rng, 27, 6, 13, 50)))
    imc = round(_trunc_normal(rng, 26.0, 5.0, 15.0, 55.0), 1)
    escolaridade = int(round(_trunc_normal(rng, 10, 3.5, 0, 20)))
    faixa = int(rng.choice([0, 1, 2], p=[0.30, 0.40, 0.30]))
    if faixa == 0:
        ig = int(rng.integers(4, 14))
    elif faixa == 1:
        ig = int(rng.integers(14, 28))
    else:
        ig = int(rng.integers(28, 43))
    gestacoes = int(min(12, 1 + rng.poisson(0.9)))
    n_prev = max(gestacoes - 1, 0)
    abortos = int(min(6, rng.binomial(n_prev, 0.15))) if n_prev else 0
    n_partos_max = max(gestacoes - 1 - abortos, 0)
    partos = int(min(10, rng.binomial(n_partos_max, 0.88))) if n_partos_max else 0
    cesareas = int(min(5, rng.binomial(partos, 0.42))) if partos else 0
    natimorto = bool(rng.random() < 0.03) if partos >= 1 else False
    pre_ecl = bool(rng.random() < 0.06) if partos >= 1 else False
    if partos >= 1:
        log_med = np.log(30.0)
        intervalo = float(np.clip(rng.lognormal(log_med, 0.6), 3.0, 300.0))
        intervalo = round(intervalo, 1)
    else:
        intervalo = None

    p_has = float(_sigmoid(-3.4 + 0.055 * (idade - 28) + 0.07 * (imc - 26)))
    has_cronica = bool(rng.random() < p_has)
    p_dm = float(_sigmoid(-3.6 + 0.10 * (imc - 26) + 0.03 * (idade - 28)))
    diabetes = bool(rng.random() < p_dm)
    cardiopatia = bool(rng.random() < 0.015)
    nefropatia = bool(rng.random() < 0.012)
    tev = bool(rng.random() < 0.020)
    gemelaridade = bool(rng.random() < 0.016)
    tabagismo = bool(rng.random() < 0.100)
    infeccao = bool(rng.random() < 0.040)

    pas = _trunc_normal(rng, 112, 12, 80, 200)
    if has_cronica:
        pas += 18
    pas += rng.normal(0, 4)
    pas = int(np.clip(round(pas), 80, 200))
    pad = _trunc_normal(rng, 71, 9, 50, 130)
    if has_cronica:
        pad += 12
    pad += rng.normal(0, 4)
    pad = int(np.clip(round(pad), 50, min(130, pas - 15)))
    if pad >= pas:
        pad = max(50, pas - 15)

    hb = round(_trunc_normal(rng, 12.2, 1.3, 5.0, 16.0), 1)
    glic = float(np.clip(rng.lognormal(np.log(85.0), 0.13), 60.0, 200.0))
    if diabetes:
        glic += 25.0
    glic = round(float(np.clip(glic, 60.0, 200.0)), 1)
    pesos = PROTEINURIA_PAS_ALTA if pas >= 140 else PROTEINURIA_PAS_BAIXA
    proteinuria = str(rng.choice(PROTEINURIA_NIVEIS, p=pesos / pesos.sum()))

    row = {
        'idade': idade,
        'imc_pre_gestacional': imc,
        'escolaridade_anos': escolaridade,
        'ig_semanas': ig,
        'gestacoes': gestacoes,
        'partos': partos,
        'abortos': abortos,
        'cesareas_previas': cesareas,
        'natimorto_previo': natimorto,
        'pre_eclampsia_previa': pre_ecl,
        'intervalo_interpartal_meses': intervalo,
        'pas_mmhg': pas,
        'pad_mmhg': pad,
        'hemoglobina_g_dl': hb,
        'glicemia_jejum_mg_dl': glic,
        'proteinuria_fita': proteinuria,
        'has_cronica': has_cronica,
        'diabetes_previo': diabetes,
        'cardiopatia': cardiopatia,
        'nefropatia': nefropatia,
        'tev_previo': tev,
        'gemelaridade': gemelaridade,
        'tabagismo': tabagismo,
        'infeccao_sexual_ativa': infeccao,
    }
    z = _escore_latente(row)
    p = float(_sigmoid(z))
    row['risco_latente'] = p
    row['alto_risco'] = bool(rng.random() < p)
    return row


def _mascarar(rng: np.random.Generator, row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if rng.random() < 0.12:
        out['hemoglobina_g_dl'] = None
    if rng.random() < 0.15:
        out['glicemia_jejum_mg_dl'] = None
    taxa_prot = 0.30 if row['ig_semanas'] < 20 else 0.05
    if rng.random() < taxa_prot:
        out['proteinuria_fita'] = None
    if rng.random() < 0.20:
        out['escolaridade_anos'] = None
    if row['partos'] == 0:
        out['intervalo_interpartal_meses'] = None
    return out


def _atribuir_split(y: np.ndarray, seed: int) -> np.ndarray:
    from sklearn.model_selection import train_test_split

    idx = np.arange(len(y))
    treino, resto = train_test_split(idx, test_size=0.30, stratify=y, random_state=seed)
    valid, teste = train_test_split(resto, test_size=0.50, stratify=y[resto], random_state=seed)
    labels = np.empty(len(y), dtype=object)
    labels[treino] = 'treino'
    labels[valid] = 'validacao'
    labels[teste] = 'teste'
    return labels


def gerar_dataframe(n: int = N_REGISTROS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    linhas = []
    for i in range(n):
        completo = _gerar_linha(rng)
        mascarado = _mascarar(rng, completo)
        mascarado['registro_id'] = str(uuid.uuid5(UUID_NS, f'{seed}:{i}'))
        mascarado['dataset_version'] = DATASET_VERSION
        linhas.append(mascarado)
    df = pd.DataFrame(linhas)
    y = df['alto_risco'].astype(int).to_numpy()
    df['split'] = _atribuir_split(y, seed)
    ordem = list(FEATURES) + [COLUNA_ALVO, *COLUNAS_RASTREIO]
    return df[ordem]


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for bloco in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def caminho_parquet() -> Path:
    return artifacts_dir() / 'data' / 'risco_gestacional_v1.parquet'


def caminho_manifesto() -> Path:
    return artifacts_dir() / 'data' / 'risco_gestacional_v1.manifest.json'


def manifesto_de(df: pd.DataFrame, parquet_path: Path, seed: int) -> dict[str, Any]:
    return {
        'sha256': sha256_arquivo(parquet_path),
        'semente': seed,
        'contrato_version': CONTRATO_VERSION,
        'dataset_version': DATASET_VERSION,
        'gerador_version': GERADOR_VERSION,
        'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'n_registros': int(len(df)),
        'n_features': N_FEATURES,
        'natureza': 'SINTETICO',
        'aviso': (
            'Dataset sintético demonstrativo. Métricas não são validação clínica.'
        ),
        'contagem_por_classe': {
            'habitual': int((~df['alto_risco']).sum()),
            'alto_risco': int(df['alto_risco'].sum()),
        },
        'contagem_por_split': df['split'].value_counts().to_dict(),
        'prevalencia_alto_risco': float(df['alto_risco'].mean()),
    }


def salvar_dataset(df: pd.DataFrame, seed: int = RANDOM_SEED) -> dict[str, Any]:
    dest = caminho_parquet()
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dest, index=False)
    man = manifesto_de(df, dest, seed)
    man_path = caminho_manifesto()
    man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return man


def gerar_e_salvar(n: int = N_REGISTROS, seed: int = RANDOM_SEED) -> dict[str, Any]:
    df = gerar_dataframe(n=n, seed=seed)
    return salvar_dataset(df, seed=seed)


def verificar_dataset(n: int = N_REGISTROS, seed: int = RANDOM_SEED) -> dict[str, Any]:
    man_path = caminho_manifesto()
    if not man_path.exists():
        raise FileNotFoundError(f'Manifesto ausente: {man_path}')
    esperado = json.loads(man_path.read_text(encoding='utf-8'))
    df = gerar_dataframe(n=n, seed=seed)
    tmp = caminho_parquet().with_suffix('.verify.parquet')
    df.to_parquet(tmp, index=False)
    atual = sha256_arquivo(tmp)
    tmp.unlink(missing_ok=True)
    if atual != esperado.get('sha256'):
        raise ValueError(
            f'Hash divergente: manifesto={esperado.get("sha256")} regenerado={atual}'
        )
    return {'ok': True, 'sha256': atual}


def perfilar(df: pd.DataFrame | None = None) -> dict[str, Any]:
    """T-16: estatísticas medidas do Parquet (não inventadas)."""
    if df is None:
        df = pd.read_parquet(caminho_parquet())
    nulos = {c: int(df[c].isna().sum()) for c in FEATURES if c in df.columns}
    return {
        'n': int(len(df)),
        'n_features': N_FEATURES,
        'prevalencia_alto_risco': float(df['alto_risco'].mean()) if 'alto_risco' in df.columns else None,
        'splits': {str(k): int(v) for k, v in df['split'].value_counts().items()} if 'split' in df.columns else {},
        'nulos_por_feature': nulos,
        'natureza': 'SINTETICO',
    }


def gravar_perfil(df: pd.DataFrame | None = None) -> Path:
    data = perfilar(df)
    path = artifacts_dir() / 'data' / 'perfil_v1.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return path


def carregar_xy(df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Devolve X (24 features), y, e o frame completo. Remove risco_latente de X."""
    if df is None:
        df = pd.read_parquet(caminho_parquet())
    faltando = [c for c in FEATURES if c not in df.columns]
    if faltando:
        raise ValueError(f'Colunas de feature ausentes: {faltando}')
    vazamento = [c for c in PROIBIDAS_EM_X if c in FEATURES]
    if vazamento:
        raise RuntimeError(f'vazamento no contrato: {vazamento}')
    X = df.loc[:, list(FEATURES)].copy()
    if 'risco_latente' in X.columns:
        raise RuntimeError('risco_latente vazou para X')
    y = df[COLUNA_ALVO].astype(int)
    return X, y, df
