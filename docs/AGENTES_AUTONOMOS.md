# Agentes autônomos da evolução

**Agente responsável:** `EvolutionOrchestratorAgent`
**Uso:** cada ciclo nomeia os agentes acionados. Um agente não avança com premissa não comprovada: se a origem for `[INF]` ou `[VAL]`, a tarefa registra a hipótese e a evidência que a fecharia.

Convenção: agentes são papéis de trabalho neste repositório, não processos externos. O orquestrador pode ser a mesma sessão, desde que o relatório do ciclo identifique o papel.

---

## EvolutionOrchestratorAgent

- **Objetivo.** Coordenar ciclos Inspecionar → Planejar → Delegar → Implementar → Testar → Revisar → Documentar → Atualizar roadmap.
- **Quando acionar.** Início e fim de cada sprint; qualquer bloqueio; mudança de ADR.
- **Entradas.** Inventário, backlog, roadmaps, diffs.
- **Saídas.** Relatório no formato da seção 12; status T-xx/BL-xx; decisão de corte de escopo.
- **Pré-condições.** Leitura do plano da sprint.
- **Não faz.** Implementar código de ML/UI “no lugar” dos especialistas sem registrar o papel.
- **Bloqueios que escala a humano.** RIS-03 empate; falha de `docker build`; pedido para apagar a Fase 3.

## ProjectDiscoveryAgent

- **Responsabilidade.** Ler o que existe de verdade. Classificar origem.
- **Entregáveis.** `docs/00_INVENTARIO_PROJETO.md`, `01_ESTADO_ATUAL.md`, `02_MAPA_DE_COMPONENTES.md`, `03_LACUNAS_E_RISCOS.md`.
- **Skills.** `project_inventory`, `repository_analysis`, `technology_detection`, `architecture_reverse_engineering`, `dependency_analysis`, `gap_analysis`.
- **Status.** Entregáveis do ciclo 1 produzidos.

## RequirementsAnalystAgent

- **Entregáveis.** `docs/requisitos/*`.
- **Skills.** `requirements_extraction`, `acceptance_criteria_generation`, `traceability_matrix`, `backlog_prioritization`, `risk_analysis`.
- **Regra.** Todo RF/RNF tem ID, critério de aceite, evidência, status, responsável, risco.

## ArchitectureAgent

- **Entregáveis.** `docs/arquitetura/*`, `lib/config.py` (T-08), higiene T-71.
- **Skills.** `architecture_documentation`, contratos, ADRs.
- **Regra de ouro.** ADR-001: aditivo. Lista “Não tocar” em `ARQUIVOS_AFETADOS.md`.

## DataEngineeringAgent

- **Entregáveis.** Contrato, dicionário, gerador, pipeline de features, manifesto.
- **Skills.** `dataset_profiling`, `data_quality_analysis`, `data_contract_generation`, `labeling_strategy`, `train_test_split_validation`, `data_leakage_detection`, `synthetic_data_generation`.
- **Regra.** Declarar ausência de dataset real; nunca rotular com a regra baseline.

## MachineLearningAgent

- **Entregáveis.** Treino, avaliação, comparação, inferência, análise de erros.
- **Skills.** `problem_definition`, `baseline_model_training`, `classification_model_training`, `model_comparison`, `metrics_evaluation`, `confusion_matrix_analysis`, `class_imbalance_analysis`, `model_serialization`, `inference_pipeline_generation`.
- **Regra.** Acurácia não decide. FN tem prioridade clínica. Empate com baseline é resultado válido.

## ExplainabilityAgent

- **Entregáveis.** `lib/ml/explain.py`, docs de interpretação, artefatos SHAP/fallback.
- **Skills.** `feature_importance`, `shap_analysis`, `prediction_explanation`, `explanation_validation`.
- **Regra.** Sem linguagem causal. Método sempre declarado.

## LLMIntegrationAgent

- **Entregáveis.** `llm_contract.py`, `validacao.py`, 10ª tool, casos de teste de prompt.
- **Skills.** `prompt_engineering`, `structured_llm_output`, `hallucination_mitigation`.
- **Regra.** LLM não altera `prediction`, `probabilities`, métricas.

## RAGAgent

- **Entregáveis.** Estratégia, avaliação, citação, metadados; nó de recuperação em `risco_ml`.
- **Skills.** `rag_retrieval_validation`, `source_traceability`, `citation_validation`.
- **Regra.** Caminho `incompleto` não chama RAG. Citação = trecho que entrou no prompt.

## LangGraphAgent

- **Entregáveis.** `risco_ml.py`, estados, erros, HIL; nó opcional no obstétrico.
- **Skills.** `state_schema_design`, `workflow_design`, `conditional_routing`, `human_in_the_loop`, `error_recovery`, `workflow_observability`.
- **Regra.** Sem loops. Quatro caminhos de exceção desde o primeiro commit do grafo.

## SecurityAndComplianceAgent

- **Entregáveis.** Análise de riscos, LGPD, auditoria, controles, avisos clínicos; DDL `predicoes_ml`.
- **Skills.** `risk_analysis`, privacidade, varredura de segredos.
- **Regra.** Sem valor clínico em claro na auditoria. Human-in-the-loop em incompleto e em violência (já existente).

## TestingAndValidationAgent

- **Entregáveis.** `tests/unit|integration|e2e|regression`, plano/relatório/matriz de cobertura.
- **Skills.** geração de testes nos 4 níveis, `test_evidence_collection`, `documentation_validation`.
- **Regra.** Requisito implementado sem evidência permanece `Não atendido`.

## MLOpsAndDeploymentAgent

- **Entregáveis.** requirements pinados, scripts, Dockerfile, compose, registry, logs de execução.
- **Skills.** `dockerfile_generation`, `docker_build_validation`, `environment_configuration`, `model_versioning`, `reproducibility_validation`.
- **Regra.** Não escrever “funciona” sem log.

## DocumentationAgent

- **Entregáveis.** README, relatórios, glossário, changelog, fechamento da matriz.
- **Skills.** `technical_report_generation`, `readme_generation`, `changelog_generation`.
- **Regra.** Número sem artefato = invenção.

## DemoAndPresentationAgent

- **Entregáveis.** 6ª aba, `run_demo.py`, roteiros, checklist.
- **Skills.** `demo_script_generation`, UI Gradio.
- **Regra.** Quatro cenários obrigatórios. Declarar dublê de LLM no Docker.

---

## Matriz agente × sprint

| Sprint | Agentes principais |
|---|---|
| 1 | Discovery, Requirements, Architecture, Orchestrator |
| 2 | Architecture, DataEngineering, Testing, MLOps |
| 3 | MachineLearning, MLOps |
| 4 | Explainability, Testing |
| 5 | LangGraph, LLM, RAG, Security, Testing |
| 6 | Demo, Testing |
| 7 | Testing, MLOps, Security |
| 8 | Documentation, Demo, Architecture (higiene) |
