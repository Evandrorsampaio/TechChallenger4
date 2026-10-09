# Execução local (evidência)

**Data:** 2026-09-18  
**Perfil:** ml-only / demo-cpu no Windows (Python 3.13.13, conda).  
**Comando observado neste ciclo (não é clone do zero; o repositório já estava no workspace).**

```
python scripts/train.py
# treino ok; limiares gravados em artifacts/metrics/limiar.json
# logistic_regression: 0.2782268517591518
# random_forest: 0.323043884645939

python scripts/run_demo.py
# D1_sucesso normal alto_risco
# D2_incompleto incompleto incompleto
# D3_emergencia bypass_regra alto_risco
# D4_degradado degradado alto_risco
# auditoria_linhas 4

python -m pytest -q
# 50 passed (depois 53+ com smoke de evaluate)
```

Dataset: `artifacts/data/risco_gestacional_v1.manifest.json` sha256 `6a3b6aefe9e2cf1bb3ec9123386cac4812fd4ef1602657d7950668d5abc20e2f`, n=8000, prevalência 0,20575.

Avisos: métricas sobre gerador sintético. Sem validação clínica.
