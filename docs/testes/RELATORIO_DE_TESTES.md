# Relatório de testes

**Data:** 2026-09-18  
**Comando:** `python -m pytest -q`

Resultado observado neste ciclo: **66 testes** verdes (`python -m pytest -q`, 2026-09-18). Cobertura de linha `lib/ml`: **84 %** (849 stmts, 137 miss; `train.py` fora da suíte rápida). Meta 80 % atingida.

Regressão Fase 3: 10 tools com `args_schema`; obstétrico com flag `ML_RISCO_HABILITADO=0` mantém o ramo sem nó ML.

Integração: 4 modos do workflow (`normal`, `incompleto`, `bypass_regra`, `degradado`) em `tests/integration/test_risco_ml.py`.

Explicabilidade (2026-09-18): `tests/unit/test_explicabilidade.py` + `test_explicabilidade_fallback.py` verdes (4 testes). `pip-audit` em `docs/deploy/PIP_AUDIT.md` (92 avisos / 10 pacotes; pins não alteradas).
