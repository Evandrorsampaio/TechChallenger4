# Changelog

## 0.4.0 — 2026-09-18

Evolução aditiva: dataset sintético v1, quatro modelos, workflow `risco_ml`, aba Gradio, auditoria `predicoes_ml`, FakeChatModel.

**Não atendido neste ciclo:** nenhum bloqueio de execução. Docker comprovado em `docs/deploy/EXECUCAO_DOCKER.md`. Ressalvas: SHAP opcional; RAG de produção (Chroma/Colab) não reindexado nesta imagem CPU; pesos do encoder de embeddings ausentes localmente (T-03 = 128 via config do Hub).

Números em `artifacts/metrics/`. Fase 3 (Llama, 9 tools originais, 4 grafos) permanece; tools passaram a 10 com `args_schema` em `buscar_protocolo`.

**T-71 higiene:** `TODAY` unificado em `REFERENCE_DATE`; `buscar_protocolo` delega a `rag_search`; `max_iterations` usado em `run_consulta` (`recursion_limit`); imports mortos removidos em tools/triagem; CI `ml-only` em `.github/workflows/ci.yml`.
