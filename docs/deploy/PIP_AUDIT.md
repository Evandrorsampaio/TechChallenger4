# T-63 — pip-audit (2026-09-18)

Comando:

```
python -m pip_audit -r requirements.txt -r requirements-ml.txt
```

**Resultado:** 92 avisos conhecidos em **10** pacotes (contagem com duplicatas de advisory). Nenhuma correção de versão foi aplicada neste ciclo: as pins da Fase 3 + ML devem permanecer estáveis para a demo. Atualizar LangGraph/Gradio/Pillow é dívida explícita, não parte do treino.

| Pacote | Versão auditada | IDs (amostra) | Correção sugerida pelo audit |
|---|---|---|---|
| python-dotenv | 1.1.0 | PYSEC-2026-2270 | 1.2.2 |
| pytest | 8.3.5 | PYSEC-2026-1845 | 9.0.3 |
| langchain-core | 0.3.59 | PYSEC-2026-1518 e outros | 0.3.80+ / 1.x |
| langgraph | 0.4.5 | PYSEC-2026-83 | 1.0.10 |
| langgraph-checkpoint | 2.1.2 | PYSEC-2026-1527 | 3.0.0+ |
| langsmith | 0.3.45 | PYSEC-2026-2583, CVE-2026-59152 | 0.7.31+ / 0.8.x |
| gradio | 5.29.0 | PYSEC-2025-119, PYSEC-2026-64, … | 5.31.0 / 6.x |
| starlette | 0.52.1 | PYSEC-2026-161, … | 1.0.1+ |
| pillow | 11.3.0 | PYSEC-2026-2249 e dezenas | 12.1.1–12.3.0 |
| pyarrow | 19.0.1 | PYSEC-2026-113 | 23.0.1 |

Varredura de credenciais: `tests/unit/test_sem_segredos.py` (código e config; docs podem citar a palavra `password` em exemplos).

CI (`T-64`): `.github/workflows/ci.yml` perfil `ml-only`, Python 3.12, pytest com cobertura de `lib/ml`.
