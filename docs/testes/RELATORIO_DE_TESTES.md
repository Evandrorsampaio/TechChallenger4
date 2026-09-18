# Relatório de testes

**Data:** 2026-09-18  
**Comando:** `python -m pytest -q`

Resultado observado neste ciclo: suíte verde (50 testes antes do smoke extra de `evaluate`; depois `tests/unit/test_evaluate_smoke.py`).

Cobertura de linha `lib/ml` (pytest-cov, medição com smoke de evaluate): **86 %** (780 stmts, 112 miss). `lib/ml/train.py` permanece fora da suíte rápida (grid RF). Meta 80 % **atingida** nessa medição.

Regressão Fase 3: 10 tools com `args_schema`; obstétrico com flag `ML_RISCO_HABILITADO=0` mantém o ramo sem nó ML.

Integração: 4 modos do workflow (`normal`, `incompleto`, `bypass_regra`, `degradado`) em `tests/integration/test_risco_ml.py`.
