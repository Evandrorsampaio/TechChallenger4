# Roadmap de Novas Implementações e Finalização

**Projeto:** Guardiã AI — Saúde e Segurança da Mulher  
**Data:** 2026-10-09  
**Branch:** linha de entrega atual (mesma HEAD da evolução ML)  

---

## Status Geral das Fases

- [x] **Fase 1: Configuração do Ambiente e Suíte de Testes Local**
  - [x] Criar ambiente virtual local `.venv` com dependências atualizadas.
  - [x] Executar pipeline de treinamento de modelos (`scripts/train.py`).
  - [x] Rodar e validar 100% da suíte de testes (88 testes verdes em `pytest`).

- [x] **Fase 2: Integração Prontuário ↔ Formulário ML na UI (6ª Aba)**
  - [x] Adicionar botão de carregamento rápido no formulário ML (`lib/ui.py`).
  - [x] Conectar o manipulador `on_carregar_paciente_ml` à função `features_de_paciente` (`lib/ml/schema.py`) para preencher automaticamente o payload JSON.
  - [x] Adicionar teste automatizado E2E em `tests/e2e/test_ui_aba_ml.py`.

- [x] **Fase 3: RAG na demo CPU + chunking do notebook 06**
  - [x] `CHUNK_SIZE=1000` e `CHUNK_OVERLAP=200` em `06_indexar_protocolos.ipynb` (reindexação Chroma continua no Colab; Drive não está no Git).
  - [x] Subset lexical versionado (`artifacts/rag/protocolos_subset.json` + `lib/rag_local.py`) usado por `scripts/app.py` e `scripts/run_demo.py`, com `doc_id` real.
  - [x] Citações `doc_id` / `category` / `trecho` em `lib/workflows/common.py`.

- [ ] **Fase 4: Explicabilidade Avançada (SHAP) — opcional**
  - [ ] Instalar `shap` se o Python permitir. **Estado real:** `shap` comentado em `requirements-ml.txt`; cascata `coef_linear` / permutação em `lib/ml/explain.py` (`SHAP_DISPONIVEL=False` neste ambiente).

- [x] **Fase 5: Evidências Visuais e Preparação da Entrega Final**
  - [x] Executar gerador de artefatos de demonstração `scripts/run_demo.py` para gerar os 4 modos operacionais (`D1_sucesso`, `D2_incompleto`, `D3_emergencia`, `D4_degradado`) em `artifacts/demo/`.
  - [x] Criar o documento oficial de testes e guia de homologação [`docs/testes/ROADMAP_DE_TESTES.md`](../testes/ROADMAP_DE_TESTES.md).

---

## Log de Progresso

| Data | Fase / Tarefa | Descrição do Progresso | Status |
|---|---|---|---|
| 2026-09-21 | Inicialização | Roadmap de novas implementações criado | 🟢 Criado |
| 2026-09-21 | Fase 1 | Ambiente virtual `.venv` criado, dataset gerado e 4 modelos treinados; 88 testes pytest passando 100% | 🟢 Concluído |
| 2026-09-21 | Fase 2 | Botão "Carregar dados da paciente selecionada" e handler `on_carregar_paciente_ml` adicionados à 6ª aba do Gradio (`lib/ui.py`) com teste E2E | 🟢 Concluído |
| 2026-10-09 | Fase 3 | Notebook 06 alinhado a 1000/200; RAG CPU com subset JSON e `doc_id` estável | 🟢 Concluído |
| 2026-10-09 | Fase 4 | SHAP **não** instalado; fallback ADR-008 permanece | 🟡 Opcional |
| 2026-09-21 | Fase 5 | Criado o `ROADMAP_DE_TESTES.md` com guia completo de homologação tela a tela e matriz de 10 casos de aceite | 🟢 Concluído |
