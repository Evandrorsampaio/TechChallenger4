# Log da demo

**2026-09-18** `python scripts/run_demo.py` (FakeChatModel, banco seed 42):

```
D1_sucesso normal alto_risco
D2_incompleto incompleto incompleto
D3_emergencia bypass_regra alto_risco
D4_degradado degradado alto_risco
auditoria_linhas 4
```

JSON: `artifacts/demo/D1_sucesso.json` … `D4_degradado.json`.

D1 com o caso “habitual clínico” saiu `alto_risco` porque o limiar operacional privilegia recall (P acima de 0,278 é comum). Isso ilustra o custo de precisão documentado em `METRICAS_E_RESULTADOS.md`.
