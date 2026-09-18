# Relatório técnico da evolução ML

**Data:** 2026-09-18

O assistente da Fase 3 permanece. A classificação obstétrica por LLM foi complementada (não apagada) por um classificador tabular sintético, orquestrado em `lib/workflows/risco_ml.py`.

Números: `docs/ml/METRICAS_E_RESULTADOS.md`. Limitações: dados sintéticos; precisão positiva baixa sob limiar de recall; Docker sem evidência de run. LLM no CPU é `FakeChatModel`.
