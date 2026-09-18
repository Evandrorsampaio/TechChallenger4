# Changelog

## 0.4.0 — 2026-09-18

Evolução aditiva: dataset sintético v1, quatro modelos, workflow `risco_ml`, aba Gradio, auditoria `predicoes_ml`, FakeChatModel.

**Não atendido neste ciclo:** nenhum bloqueio de execução. Docker comprovado em `docs/deploy/EXECUCAO_DOCKER.md`. Ressalvas: SHAP opcional; RAG de produção (Chroma/Colab) não reindexado nesta imagem CPU.

Números em `artifacts/metrics/`. Fase 3 (Llama, 9 tools originais, 4 grafos) permanece; tools passaram a 10 com `args_schema` em `buscar_protocolo`.
