# Roadmap Técnico — Lista Executável de Tarefas

**Agente responsável:** `EvolutionOrchestratorAgent`
**Faixa de IDs:** `T-01` a `T-71`
**Rastreabilidade:** cada tarefa aponta um item `BL-xx` de `docs/requisitos/BACKLOG_PRIORIZADO.md`,
os requisitos `RF-xx`/`RNF-xx` que ela atende e o critério `CA-xx` que a prova.

> ## Banner de estado
>
> **Nenhuma tarefa de implementação foi iniciada.** Nenhum arquivo listado na coluna "Arquivos"
> existe, exceto os marcados **(existente)**, que serão estendidos de forma aditiva (ADR-001).
> Nenhum teste listado foi escrito. Nenhuma evidência foi produzida.
>
> As 5 tarefas da Sprint 1 marcadas `Concluído (documento)` entregaram **documentos**, não código.

---

## Como ler uma tarefa

```
**T-xx — Título**
- Sprint · Backlog · Requisitos · Critérios de aceite
- Agente responsável (catálogo de 15)
- Skills utilizadas (catálogo abaixo)
- Arquivos afetados — caminhos reais planejados; (existente) = estendido, não criado
- Dependências — outras tarefas T-xx que precisam estar prontas
- Teste que valida — arquivo de teste planejado
- Evidência esperada — artefato que prova a conclusão
- Definição de pronto — condição binária, verificável por execução
- Status
```

**Regra de status.** Uma tarefa só muda de `Não iniciado` quando o artefato da linha "Evidência
esperada" existir no repositório. Status é consequência de artefato, não de esforço.

---

## Catálogo de agentes (15)

| # | Agente | Domínio |
|---|---|---|
| 1 | `ProjectDiscoveryAgent` | Inventário, leitura de código, lacunas |
| 2 | `RequirementsAnalystAgent` | Requisitos, critérios de aceite, backlog, rastreabilidade |
| 3 | `ArchitectureAgent` | Arquitetura alvo, ADRs, contratos, configuração, higiene estrutural |
| 4 | `DataEngineeringAgent` | Contrato de dados, geração sintética, features, qualidade |
| 5 | `MachineLearningAgent` | Treino, avaliação, limiar, inferência, análise de erros |
| 6 | `ExplainabilityAgent` | SHAP, fallbacks, interpretação das predições |
| 7 | `RAGAgent` | Recuperação, metadados, citação, avaliação de recuperação |
| 8 | `LangGraphAgent` | Workflows, estados, roteamento, HIL, tratamento de erros |
| 9 | `LLMIntegrationAgent` | Contrato de entrada/saída do LLM, prompts, anti-alucinação |
| 10 | `SecurityAndComplianceAgent` | Regras de segurança, auditoria, LGPD, avisos clínicos |
| 11 | `TestingAndValidationAgent` | Suíte de testes, regressão, cobertura, evidências |
| 12 | `MLOpsAndDeploymentAgent` | Dependências, Docker, scripts, registry, observabilidade, CI |
| 13 | `DemoAndPresentationAgent` | Interface, demonstração, roteiros, apresentação |
| 14 | `DocumentationAgent` | README, relatórios, métricas publicadas, changelog |
| 15 | `EvolutionOrchestratorAgent` | Roadmap, sequenciamento, riscos, controle de escopo |

## Catálogo de skills

Nomes em `snake_case`, usados na linha "Skills" de cada tarefa.

| Grupo | Skills |
|---|---|
| Descoberta | `repo_inventory`, `code_reading`, `gap_analysis`, `risk_management`, `roadmap_planning` |
| Requisitos | `requirements_engineering`, `acceptance_criteria_design`, `traceability_matrix` |
| Arquitetura | `architecture_decision_record`, `component_contract_design`, `configuration_management`, `dependency_pinning` |
| Dados | `data_contract_design`, `synthetic_data_generation`, `dataset_profiling`, `data_leakage_audit`, `feature_engineering_pipeline`, `pydantic_schema_design` |
| ML | `classification_model_training`, `baseline_rule_modeling`, `hyperparameter_search`, `model_evaluation_metrics`, `threshold_selection`, `bootstrap_confidence_interval`, `calibration_analysis`, `error_analysis`, `subgroup_analysis`, `model_registry_versioning`, `inference_pipeline` |
| Explicabilidade | `shap_analysis`, `permutation_importance`, `linear_contribution_analysis`, `explainability_reporting` |
| RAG | `rag_retrieval_tuning`, `metadata_filtering`, `source_citation_policy` |
| LLM | `prompt_contract_design`, `hallucination_guardrails`, `llm_output_verification`, `llm_test_doubles` |
| Orquestração | `langgraph_workflow_design`, `conditional_routing`, `human_in_the_loop_design`, `error_path_design`, `structured_tool_design` |
| Dados/segurança | `database_schema_migration`, `audit_logging`, `privacy_by_design`, `security_scanning` |
| Operação | `structured_logging`, `cli_script_design`, `dockerfile_generation`, `docker_compose_orchestration`, `clean_environment_execution`, `ci_pipeline_setup` |
| Interface e entrega | `gradio_ui_extension`, `ux_error_messaging`, `demo_scripting`, `video_scripting`, `presentation_design` |
| Verificação | `pytest_suite_design`, `unit_testing`, `integration_testing`, `e2e_testing`, `regression_testing`, `coverage_reporting`, `structural_testing` |
| Documentação | `technical_writing`, `changelog_management`, `metrics_reporting` |

---

# Sprint 1 — Descoberta e diagnóstico

Escopo: BL-01…BL-08. **Nenhum código de produção é alterado nesta sprint.**

**T-01 — Reconciliar o status de BL-01…BL-08 no backlog**
- Sprint 1 · BL-06 · RNF-03 · —
- `RequirementsAnalystAgent`
- Skills: `traceability_matrix`, `technical_writing`
- Arquivos: `docs/requisitos/BACKLOG_PRIORIZADO.md` **(existente)**
- Dependências: —
- Teste: revisão documental registrada
- Evidência: BL-01…BL-08 com status coerente com a existência dos documentos
- **Pronto quando:** não há item de backlog em `Não iniciado` cujo entregável já exista no
  repositório, e a divergência apontada em `ROADMAP_EXECUTIVO.md` §8.2 deixou de existir
- Status: **Concluído (documento)** — BL-01…BL-08 em `Concluído (documento)`

**T-02 — Fechar a pendência PC-01: 23 ou 24 features**
- Sprint 1 · BL-08 · RF-24 · CA-12
- `DataEngineeringAgent`, `MachineLearningAgent`
- Skills: `data_contract_design`, `gap_analysis`
- Arquivos: `docs/ml/DEFINICAO_DO_PROBLEMA.md` §2 **(existente)**, `docs/dados/CONTRATO_DE_DADOS.md` §3 **(existente)**, `docs/dados/DICIONARIO_DE_DADOS.md` §1 **(existente)**
- Dependências: —
- Teste: `tests/unit/test_contrato_dataset.py` (conta as colunas do Parquet)
- Evidência: um único número de features declarado nos três documentos
- **Pronto quando:** `DEFINICAO_DO_PROBLEMA.md` §2 ("24 variáveis"), `CONTRATO_DE_DADOS.md` §3
  ("24 features") e `DICIONARIO_DE_DADOS.md` §2 ("24 features + 1 alvo + 4 de rastreabilidade")
  concordam, e PC-01 está marcada `Resolvida` em `DICIONARIO_DE_DADOS.md` §11
- Status: **Concluído (documento)** — decisão: 24 features

**T-03 — Medir `max_seq_length` real do encoder e reconciliar 128 vs 512 tokens**
- Sprint 1 · BL-04 · RF-11 · CA-20
- `RAGAgent`
- Skills: `rag_retrieval_tuning`, `code_reading`, `gap_analysis`
- Arquivos: `docs/00_INVENTARIO_PROJETO.md` §7.1 **(existente)**, `docs/rag/ESTRATEGIA_RAG.md` §3.1 **(existente)**
- Dependências: —
- Teste: script de verificação pontual (`SentenceTransformer(EMB_MODEL).max_seq_length`), saída anexada
- Evidência: valor medido registrado nos dois documentos, com a divergência marcada como resolvida
- **Pronto quando:** existe uma saída de execução com o valor real e os dois documentos citam o
  mesmo número; a estimativa de fração do chunk representada é recalculada a partir dele
- Status: **Não iniciado**

**T-04 — Resolver a divergência do RAG no caminho `incompleto`**
- Sprint 1 · BL-07 · RF-11, RF-21 · CA-07, CA-20
- `LangGraphAgent`, `RAGAgent`
- Skills: `error_path_design`, `rag_retrieval_tuning`
- Arquivos: `docs/langgraph/WORKFLOW_ML.md` §8 **(existente)**, `docs/rag/ESTRATEGIA_RAG.md` §7 **(existente)**
- Dependências: —
- Teste: `tests/e2e/test_fluxo_dados_incompletos.py` (verifica presença ou ausência declarada de fontes)
- Evidência: decisão registrada em um dos dois documentos, com o outro atualizado
- **Pronto quando:** `WORKFLOW_ML.md` §8 (caminho `incompleto` **não** passa pelo RAG) e
  `ESTRATEGIA_RAG.md` §7 deixam de se contradizer, por decisão registrada em qualquer uma das duas direções
- Status: **Concluído (documento)** — RAG **não** roda no caminho `incompleto`

**T-05 — Inventário, estado atual e mapa de componentes**
- Sprint 1 · BL-01, BL-02, BL-03 · base para todos · —
- `ProjectDiscoveryAgent`
- Skills: `repo_inventory`, `code_reading`
- Arquivos: `docs/00_INVENTARIO_PROJETO.md`, `docs/01_ESTADO_ATUAL.md`, `docs/02_MAPA_DE_COMPONENTES.md`
- Dependências: —
- Teste: revisão documental
- Evidência: os três documentos, com marcadores de origem por afirmação
- **Pronto quando:** toda afirmação carrega `[COD]`/`[CFG]`/`[DOC]`/`[INF]`/`[AUS]`/`[VAL]`
- Status: **Concluído (documento)**

**T-06 — Lacunas, riscos, requisitos, critérios de aceite e matriz**
- Sprint 1 · BL-04, BL-05, BL-06 · RF-01…RF-26, RNF-01…RNF-20 · CA-01…CA-40
- `ProjectDiscoveryAgent`, `RequirementsAnalystAgent`
- Skills: `gap_analysis`, `risk_management`, `requirements_engineering`, `acceptance_criteria_design`, `traceability_matrix`
- Arquivos: `docs/03_LACUNAS_E_RISCOS.md`, `docs/requisitos/*.md`
- Dependências: T-05
- Teste: conferência de contagem (46 requisitos × 46 linhas de matriz)
- Evidência: LAC-01…LAC-28, RIS-01…RIS-16, RF-01…RF-26, RNF-01…RNF-20, CA-01…CA-40, matriz completa
- **Pronto quando:** nenhum ID de requisito fica fora da matriz e todo critério de aceite é binário
- Status: **Concluído (documento)**

**T-07 — Arquitetura alvo, ADRs, contratos e especificações de ML/dados/LLM/RAG/LangGraph**
- Sprint 1 · BL-07, BL-08 · RNF-01, RNF-12, RF-05, RF-24 · —
- `ArchitectureAgent`, `MachineLearningAgent`, `DataEngineeringAgent`, `LangGraphAgent`, `LLMIntegrationAgent`, `RAGAgent`
- Skills: `architecture_decision_record`, `component_contract_design`, `data_contract_design`, `langgraph_workflow_design`, `prompt_contract_design`
- Arquivos: `docs/arquitetura/*.md`, `docs/ml/DEFINICAO_DO_PROBLEMA.md`, `docs/dados/*.md`, `docs/llm/*.md`, `docs/rag/*.md`, `docs/langgraph/*.md`
- Dependências: T-06
- Teste: revisão documental cruzada
- Evidência: ADR-001…ADR-012 com status; contratos de componentes; especificação dos 16 nós
- **Pronto quando:** toda decisão arquitetural tem alternativas avaliadas, justificativa e
  consequências; nenhuma especificação afirma que algo foi implementado
- Status: **Concluído (documento)**

---

# Sprint 2 — Dados

Escopo: BL-09…BL-16. Objetivo: existir dataset rotulado, reprodutível e validado — e o sistema
deixar de depender do Colab.

**T-08 — `lib/config.py`: configuração por variável de ambiente**
- Sprint 2 · BL-09 · RF-18, RNF-12 · CA-37
- `ArchitectureAgent`
- Skills: `configuration_management`, `architecture_decision_record`
- Arquivos: `lib/config.py` (novo)
- Dependências: T-07
- Teste: `tests/unit/test_configuracao_central.py`
- Evidência: `lib/config.py` resolvendo `HOSPITAL_DB_PATH`, `DRIVE_BASE`, `HF_TOKEN`, `PERFIL_EXECUCAO`, `ML_RISCO_HABILITADO`, `ARTIFACTS_DIR`, `RANDOM_SEED`
- **Pronto quando:** nenhum caminho absoluto literal existe fora de `lib/config.py` nos módulos
  novos, os defaults Colab de `lib/db.py:12` e `lib/llm.py:51` são preservados, e `ML_RISCO_HABILITADO` tem default `0`
- Status: **Não iniciado**

**T-09 — `.env.example` com as variáveis documentadas**
- Sprint 2 · BL-09 · RNF-12, RNF-13 · CA-37
- `ArchitectureAgent`, `SecurityAndComplianceAgent`
- Skills: `configuration_management`, `security_scanning`
- Arquivos: `.env.example` (novo)
- Dependências: T-08
- Teste: `tests/unit/test_configuracao_central.py`, `tests/unit/test_sem_segredos.py`
- Evidência: `.env.example` com 100 % das variáveis lidas por `lib/config.py`
- **Pronto quando:** toda variável usada está no arquivo e nenhum valor é um segredo real
  (padrões `hf_[A-Za-z0-9]{20,}`, `sk-`, `AKIA`, `password=` ausentes)
- Status: **Não iniciado**

**T-10 — Três arquivos de requisitos com versões pinadas**
- Sprint 2 · BL-10 · RF-18, RNF-02, RNF-11 · CA-35, CA-38
- `MLOpsAndDeploymentAgent`
- Skills: `dependency_pinning`
- Arquivos: `requirements.txt`, `requirements-ml.txt`, `requirements-llm.txt` (novos)
- Dependências: T-08
- Teste: instalação limpa em venv novo, log anexado
- Evidência: os três arquivos, todos com `==` em cada linha
- **Pronto quando:** 100 % das dependências têm versão exata; `requirements.txt` +
  `requirements-ml.txt` instalam sem `torch`, sem `transformers` e sem CUDA (ADR-005), e a
  instalação conclui em ambiente limpo Windows + Python 3.13
- Status: **Não iniciado**

**T-11 — `GestanteFeatures`: schema Pydantic do contrato v1.0.0**
- Sprint 2 · BL-11 · RF-01, RF-02 · CA-01, CA-02, CA-04
- `DataEngineeringAgent`
- Skills: `pydantic_schema_design`, `data_contract_design`
- Arquivos: `lib/ml/__init__.py`, `lib/ml/schema.py` (novos)
- Dependências: T-07, T-10
- Teste: `tests/unit/test_schema_gestante.py`, `tests/unit/test_validacao_entrada.py`
- Evidência: saída do `pytest` com os casos parametrizados por classe de violação
- **Pronto quando:** os 11 campos obrigatórios e 13 opcionais estão declarados com `ge`/`le`
  conforme `CONTRATO_DE_DADOS.md` §3, `model_config = ConfigDict(extra='forbid')` está ativo, e
  um payload com `pressao_arterial_sistolica` em vez de `pas_mmhg` é rejeitado nomeando a chave
- Status: **Não iniciado**

**T-12 — `DadosIncompletosError` e validadores cruzados obstétricos**
- Sprint 2 · BL-11 · RF-02, RF-03, RNF-17, RNF-18 · CA-03, CA-05
- `DataEngineeringAgent`
- Skills: `pydantic_schema_design`, `ux_error_messaging`
- Arquivos: `lib/ml/schema.py`
- Dependências: T-11
- Teste: `tests/unit/test_dados_incompletos.py`, `tests/unit/test_mensagens_de_erro.py`
- Evidência: mensagens de erro contendo campo, valor recebido e faixa aceita
- **Pronto quando:** `partos + abortos > gestacoes` e `pad_mmhg >= pas_mmhg` são rejeitados com
  mensagem explicativa; campo obrigatório ausente levanta `DadosIncompletosError` listando os
  campos e **nunca** aciona imputação
- Status: **Não iniciado**

**T-13 — `lib/ml/dataset.py`: gerador sintético determinístico de 8 000 registros**
- Sprint 2 · BL-12 · RF-24, RNF-02 · CA-10, CA-12
- `DataEngineeringAgent`
- Skills: `synthetic_data_generation`, `data_contract_design`
- Arquivos: `lib/ml/dataset.py` (novo)
- Dependências: T-08, T-11
- Teste: `tests/unit/test_dataset_reprodutivel.py`, `tests/unit/test_contrato_dataset.py`
- Evidência: `artifacts/data/risco_gestacional_v1.parquet`
- **Pronto quando:** `numpy.random.default_rng(42)` gera 8 000 registros; a prevalência de
  `alto_risco` fica em 0,22 ± 0,02; o rótulo vem do modelo latente logístico com interações e
  amostragem de Bernoulli (ADR-004), **não** da regra `CRITERIOS_ALTO_RISCO`; os splits
  70/15/15 são estratificados pelo alvo
- Status: **Não iniciado**

**T-14 — Manifesto SHA-256 versionado e `--verificar-dataset`**
- Sprint 2 · BL-12 · RF-24, RNF-02, RNF-15 · CA-10
- `DataEngineeringAgent`
- Skills: `synthetic_data_generation`, `cli_script_design`
- Arquivos: `lib/ml/dataset.py`, `artifacts/data/risco_gestacional_v1.manifest.json` (novo, **versionado**)
- Dependências: T-13
- Teste: `tests/unit/test_dataset_reprodutivel.py`
- Evidência: manifesto no git + log de duas gerações independentes com o mesmo hash
- **Pronto quando:** o manifesto tem os 7 campos (SHA-256, semente, versão do contrato, timestamp,
  contagem por classe, contagem por split, versão do gerador) e duas gerações em processos
  distintos produzem hash idêntico
- Status: **Não iniciado**

**T-15 — `lib/ml/features.py`: `ColumnTransformer` dentro de `Pipeline`**
- Sprint 2 · BL-13 · RF-05, RNF-18 · CA-06, CA-11
- `DataEngineeringAgent`
- Skills: `feature_engineering_pipeline`, `data_leakage_audit`
- Arquivos: `lib/ml/features.py` (novo)
- Dependências: T-11, T-13
- Teste: `tests/unit/test_features_pipeline.py`, `tests/unit/test_dataset_sem_vazamento.py`
- Evidência: objeto `Pipeline` serializável, idêntico em treino e inferência
- **Pronto quando:** imputação (mediana para numérico, `desconhecido` para categórico),
  `StandardScaler` e codificação ordinal de `proteinuria_fita` estão **dentro** do `Pipeline`;
  `fit` ocorre exclusivamente sobre o treino; os campos imputados são recuperáveis para popular
  `dados_imputados`
- Status: **Não iniciado**

**T-16 — Perfilamento, qualidade e auditoria de vazamento**
- Sprint 2 · BL-14 · RF-24, RNF-18 · CA-11, CA-12
- `DataEngineeringAgent`
- Skills: `dataset_profiling`, `data_leakage_audit`
- Arquivos: `docs/dados/QUALIDADE_DOS_DADOS.md` **(existente, preenchido)**, `docs/dados/RISCOS_DE_VAZAMENTO.md` **(existente)**, `artifacts/data/perfil_v1.json` (novo)
- Dependências: T-13
- Teste: `tests/unit/test_dataset_sem_vazamento.py`
- Evidência: `perfil_v1.json` com distribuição por coluna e matriz de correlação com o alvo
- **Pronto quando:** `risco_latente` está ausente da matriz de features, nenhuma feature tem
  |correlação| > 0,95 com o alvo sem justificativa registrada, e o perfil publicado vem de
  execução (nenhum número digitado à mão)
- Status: **Não iniciado**

**T-17 — `features_de_paciente`: ponte `hospital.db` → `GestanteFeatures`**
- Sprint 2 · BL-15 · RF-01, RF-03 · CA-05, CA-07
- `DataEngineeringAgent`
- Skills: `pydantic_schema_design`, `code_reading`
- Arquivos: `lib/ml/schema.py`
- Dependências: T-12
- Teste: `tests/unit/test_features_de_paciente.py`
- Evidência: payload parcial com a lista nominal dos 6 campos obrigatórios ausentes
- **Pronto quando:** as 5 features mapeáveis (`idade`, `ig_semanas`, `gestacoes`, `partos`,
  `abortos`) são derivadas do prontuário com verificação de plausibilidade, e as 6 não mapeáveis
  (`imc_pre_gestacional`, `pas_mmhg`, `pad_mmhg`, `has_cronica`, `diabetes_previo`,
  `gemelaridade`) são **declaradas ausentes**, nunca inferidas nem imputadas
- Status: **Não iniciado**

**T-18 — Testes unitários da camada de dados**
- Sprint 2 · BL-16 · RF-24, RNF-02, RNF-04 · CA-10, CA-11, CA-12
- `TestingAndValidationAgent`
- Skills: `unit_testing`, `pytest_suite_design`
- Arquivos: `tests/unit/test_dataset_reprodutivel.py`, `test_dataset_sem_vazamento.py`, `test_contrato_dataset.py`, `test_schema_gestante.py`, `test_validacao_entrada.py`, `test_dados_incompletos.py`, `test_features_pipeline.py` (novos)
- Dependências: T-13, T-14, T-15
- Teste: os próprios
- Evidência: saída do `pytest tests/unit/` anexada
- **Pronto quando:** os 7 arquivos existem, todos passam, e nenhum exige GPU, rede ou Google Drive
- Status: **Não iniciado**

---

# Sprint 3 — Modelos

Escopo: BL-17…BL-24. Objetivo: quatro modelos treinados, comparados com intervalo de confiança,
com limiar justificado.

**T-19 — `lib/ml/baseline.py`: baseline determinístico por regra**
- Sprint 3 · BL-18 · RF-05, RF-08 · CA-13, CA-15
- `MachineLearningAgent`
- Skills: `baseline_rule_modeling`, `code_reading`
- Arquivos: `lib/ml/baseline.py` (novo)
- Dependências: T-15
- Teste: `tests/unit/test_baseline_regra.py`
- Evidência: `artifacts/models/baseline_regra/model_card.json`
- **Pronto quando:** implementa `CRITERIOS_ALTO_RISCO` de `obstetrico.py:50-66` como disjunção
  booleana sobre as features validadas, expõe interface compatível com `predict`/`predict_proba`
  dos demais modelos, e é **a mesma função** consumida pelo nó `modo_degradado` do workflow —
  fallback em produção e piso de comparação na avaliação não podem divergir
- Status: **Não iniciado**

**T-20 — `lib/ml/train.py`: treino dos 4 modelos com busca de hiperparâmetros**
- Sprint 3 · BL-17 · RF-05 · CA-13
- `MachineLearningAgent`
- Skills: `classification_model_training`, `hyperparameter_search`
- Arquivos: `lib/ml/train.py` (novo)
- Dependências: T-15, T-19
- Teste: `tests/integration/test_treino_completo.py`
- Evidência: 4 arquivos `.joblib` em `artifacts/models/`
- **Pronto quando:** `DummyClassifier(strategy='prior')`, baseline por regra, `LogisticRegression`
  e `RandomForestClassifier` são treinados sobre o mesmo split identificado por hash;
  `GridSearchCV` + `StratifiedKFold(5)` roda **apenas sobre o treino**, otimizando
  `average_precision`; `class_weight='balanced'` nos dois modelos de ML; `RANDOM_SEED=42` reproduz
  as mesmas métricas em duas execuções
- Status: **Não iniciado**

**T-21 — `lib/ml/evaluate.py`: matriz de confusão e métricas obrigatórias**
- Sprint 3 · BL-19 · RF-08, RF-09, RNF-16 · CA-15, CA-16
- `MachineLearningAgent`
- Skills: `model_evaluation_metrics`, `metrics_reporting`
- Arquivos: `lib/ml/evaluate.py` (novo)
- Dependências: T-20
- Teste: `tests/integration/test_metricas_reportadas.py`
- Evidência: `artifacts/metrics/*.json` por modelo e por split
- **Pronto quando:** as 8 métricas (confusão absoluta e normalizada; precision/recall/F1 por classe
  e macro; ROC-AUC; PR-AUC; Brier; especificidade; NPV; acurácia **reportada mas não decisória**)
  saem em treino, validação e teste, e cada número gravado traz modelo, split, `dataset_version` e
  timestamp
- Status: **Não iniciado**

**T-22 — Intervalos de confiança por bootstrap sobre o teste**
- Sprint 3 · BL-19 · RF-08 · CA-13, CA-15
- `MachineLearningAgent`
- Skills: `bootstrap_confidence_interval`
- Arquivos: `lib/ml/evaluate.py`
- Dependências: T-21
- Teste: `tests/unit/test_bootstrap_ic.py`
- Evidência: `artifacts/metrics/comparacao.json` com ponto e IC por métrica e por modelo
- **Pronto quando:** 1000 reamostragens com semente fixa produzem IC idênticos em duas execuções e
  a tabela comparativa permite distinguir diferença real de ruído amostral
- Status: **Não iniciado**

**T-23 — Curva de calibração e Brier score**
- Sprint 3 · BL-19 · RF-09 · CA-16
- `MachineLearningAgent`
- Skills: `calibration_analysis`, `metrics_reporting`
- Arquivos: `lib/ml/evaluate.py`
- Dependências: T-21
- Teste: `tests/integration/test_metricas_reportadas.py`
- Evidência: `artifacts/metrics/curva_calibracao.png` + Brier em `artifacts/metrics/*.json`
- **Pronto quando:** a curva existe para LogReg e RF e a comparação com `risco_latente` (teto
  teórico / erro de Bayes) está registrada — uma probabilidade mal calibrada enviada ao LLM é
  desinformação travestida de número
- Status: **Não iniciado**

**T-24 — Seleção do limiar operacional por recall na validação**
- Sprint 3 · BL-20 · RF-06 · CA-14
- `MachineLearningAgent`
- Skills: `threshold_selection`
- Arquivos: `lib/ml/evaluate.py`, `artifacts/metrics/limiar.json` (novo)
- Dependências: T-21
- Teste: `tests/unit/test_limiar_operacional.py`
- Evidência: `limiar.json` + campo `threshold` no `model_card.json`
- **Pronto quando:** o limiar é o **menor** valor que atinge recall ≥ 0,90 **na validação**, a
  precisão resultante é reportada junto, e há prova de que o conjunto de teste não participou da
  escolha
- Status: **Não iniciado**

**T-25 — `lib/ml/registry.py` e `model_card.json`**
- Sprint 3 · BL-21 · RF-25, RNF-08, RNF-14 · CA-39
- `MLOpsAndDeploymentAgent`
- Skills: `model_registry_versioning`
- Arquivos: `lib/ml/registry.py` (novo), `artifacts/models/*/model_card.json`
- Dependências: T-20
- Teste: `tests/unit/test_registry_compatibilidade.py`, `tests/unit/test_versoes_declaradas.py`
- Evidência: 4 cards completos
- **Pronto quando:** cada card tem os 9 campos (nome, versão, `dataset_version`, limiar,
  hiperparâmetros, métricas de teste, semente, timestamp, versão do `Pipeline`) e carregar um
  modelo cuja `dataset_version` tenha MAJOR diferente do dataset corrente falha com erro citando
  **as duas versões**
- Status: **Não iniciado**

**T-26 — `lib/ml/predict.py`: inferência a partir do `Pipeline` serializado**
- Sprint 3 · BL-22 · RF-06, RF-07, RF-22 · CA-01, CA-23
- `MachineLearningAgent`
- Skills: `inference_pipeline`
- Arquivos: `lib/ml/predict.py` (novo)
- Dependências: T-25
- Teste: `tests/unit/test_payload_predicao.py`, `tests/regression/test_predicao_estavel.py`
- Evidência: payload de exemplo em `artifacts/demo/`
- **Pronto quando:** `prever()` devolve `predicao`, `probabilidades` com as duas chaves somando
  1,0 ± 1e-6, `threshold`, `dados_imputados`, `model_name`, `model_version`, `dataset_version`;
  vale a pós-condição `predicao == 'alto_risco' ⟺ probabilidades['alto_risco'] >= threshold`;
  modelo ausente levanta `ModeloIndisponivelError` com mensagem indicando o caminho esperado
- Status: **Não iniciado**

**T-27 — `scripts/train.py` com `--gerar-dataset` e `--verificar-dataset`**
- Sprint 3 · BL-23 · RF-05, RF-24, RNF-15 · CA-10, CA-13, CA-35
- `MLOpsAndDeploymentAgent`
- Skills: `cli_script_design`
- Arquivos: `scripts/train.py` (novo)
- Dependências: T-14, T-20
- Teste: `tests/integration/test_treino_completo.py`
- Evidência: log de execução em `docs/ml/REPRODUTIBILIDADE.md`
- **Pronto quando:** as três invocações (`--gerar-dataset`, `--verificar-dataset`, treino completo)
  terminam com código 0 em ambiente limpo, sem GPU; `--verificar-dataset` detecta qualquer
  divergência de hash
- Status: **Não iniciado**

**T-28 — `scripts/evaluate.py` e publicação das métricas**
- Sprint 3 · BL-23 · RF-08, RF-09, RNF-16 · CA-16
- `MLOpsAndDeploymentAgent`, `MachineLearningAgent`
- Skills: `cli_script_design`, `metrics_reporting`
- Arquivos: `scripts/evaluate.py` (novo)
- Dependências: T-22, T-24
- Teste: `tests/integration/test_metricas_reportadas.py`
- Evidência: `artifacts/metrics/comparacao.json`
- **Pronto quando:** o script regenera todos os JSON de métrica a partir dos modelos salvos, sem
  retreinar, e nenhum número publicado em `docs/ml/` fica sem chave correspondente no JSON
- Status: **Não iniciado**

**T-29 — Análise de erros e desempenho por subgrupo**
- Sprint 3 · BL-24 · RF-09 · CA-17
- `MachineLearningAgent`
- Skills: `error_analysis`, `subgroup_analysis`
- Arquivos: `lib/ml/evaluate.py`, `artifacts/metrics/analise_erros.json` (novo)
- Dependências: T-21
- Teste: revisão documental da seção obrigatória em `METRICAS_E_RESULTADOS.md`
- Evidência: `analise_erros.json` + seção dedicada no documento
- **Pronto quando:** cada falso negativo do teste é listado com os fatores de risco presentes que o
  modelo não capturou; os falsos positivos têm o perfil de superponderação identificado; há recorte
  por faixa etária e por idade gestacional
- Status: **Não iniciado**

---

# Sprint 4 — Explicabilidade

Escopo: BL-25…BL-28. Objetivo: toda predição acompanhada de contribuição por variável, com o
método declarado.

**T-30 — `lib/ml/explain.py` com SHAP `TreeExplainer` e detecção em import**
- Sprint 4 · BL-25 · RF-10 · CA-18
- `ExplainabilityAgent`
- Skills: `shap_analysis`
- Arquivos: `lib/ml/explain.py` (novo)
- Dependências: T-26
- Teste: `tests/unit/test_explicabilidade.py`
- Evidência: `artifacts/explainability/shap_exemplo.json`
- **Pronto quando:** a disponibilidade de `shap` é detectada em tempo de importação sem derrubar o
  módulo; `TreeExplainer` produz contribuição local para o Random Forest; `top_features` traz
  `feature`, `value`, `contribution` e `direction ∈ {aumenta, reduz}` com ao menos 3 entradas
- Status: **Não iniciado**

**T-31 — Fallback local: contribuição linear para a Regressão Logística**
- Sprint 4 · BL-26 · RF-10, RNF-09 · CA-19
- `ExplainabilityAgent`
- Skills: `linear_contribution_analysis`
- Arquivos: `lib/ml/explain.py`
- Dependências: T-30
- Teste: `tests/unit/test_explicabilidade_fallback.py`
- Evidência: payload com `explanation_method: 'coef_linear'`
- **Pronto quando:** com `shap` ausente, a explicação **local** continua sendo produzida por
  `coef × valor_padronizado`, e `explanation_method` no payload e na auditoria deixa de ser
  `shap_tree_explainer`
- Status: **Não iniciado**

**T-32 — Fallback global: `permutation_importance` com aviso de escopo**
- Sprint 4 · BL-26 · RF-10, RNF-09 · CA-19
- `ExplainabilityAgent`
- Skills: `permutation_importance`
- Arquivos: `lib/ml/explain.py`, `artifacts/explainability/importancia_global.json` (novo)
- Dependências: T-31
- Teste: `tests/unit/test_explicabilidade_fallback.py`
- Evidência: JSON de importância global
- **Pronto quando:** a cascata `shap_tree` → `contribuicao_linear` → `permutacao` está
  implementada; quando o escopo cai para `global`, o campo `aviso` é **obrigatório** e é propagado
  ao prompt do LLM e à interface; a função nunca levanta exceção — no pior caso devolve
  `top_features=[]` com aviso
- Status: **Não iniciado**

**T-33 — Documentação de explicabilidade com saída real**
- Sprint 4 · BL-27 · RF-10, RNF-10 · CA-18
- `ExplainabilityAgent`
- Skills: `explainability_reporting`, `technical_writing`
- Arquivos: `docs/ml/EXPLICABILIDADE.md` **(existente, preenchido)**, `docs/ml/INTERPRETACAO_DAS_PREDICOES.md` **(existente, preenchido)**
- Dependências: T-30, T-31, T-32
- Teste: revisão documental
- Evidência: exemplos copiados de `artifacts/explainability/`
- **Pronto quando:** todo exemplo publicado é saída literal de execução e a diferença de qualidade
  entre os três métodos está descrita, não escondida
- Status: **Não iniciado**

**T-34 — Testes de explicabilidade, inclusive sem `shap` instalado**
- Sprint 4 · BL-28 · RF-10, RNF-04 · CA-18, CA-19
- `TestingAndValidationAgent`
- Skills: `unit_testing`, `pytest_suite_design`
- Arquivos: `tests/unit/test_explicabilidade.py`, `tests/unit/test_explicabilidade_fallback.py` (novos)
- Dependências: T-32
- Teste: os próprios
- Evidência: saída do `pytest` nos dois cenários
- **Pronto quando:** existe um teste que simula a ausência de `shap` (monkeypatch do import) e
  verifica que a explicação continua sendo produzida com método diferente e **declarado**
- Status: **Não iniciado**

---

# Sprint 5 — Integração

Escopo: BL-29…BL-38. Objetivo: o modelo deixa de ser artefato isolado e passa a viver dentro do
sistema, com auditoria, contrato de LLM e caminhos de exceção.

**T-35 — Tabela `predicoes_ml` (aditiva a `lib/db.py`)**
- Sprint 5 · BL-29 · RF-15, RNF-06 · CA-31
- `SecurityAndComplianceAgent`
- Skills: `database_schema_migration`, `privacy_by_design`
- Arquivos: `lib/db.py` **(existente, +1 tabela)**
- Dependências: T-26
- Teste: `tests/unit/test_schema_auditoria.py`, `tests/regression/test_db_existente.py`
- Evidência: DDL aplicado + dump de exemplo
- **Pronto quando:** o DDL de `ARQUITETURA_ALVO.md` §5.3 está implementado com
  `CREATE TABLE IF NOT EXISTS`; `probabilidade` e `threshold` são anuláveis; não existe coluna com
  valor clínico em claro; as 7 tabelas atuais permanecem inalteradas
- Status: **Não iniciado**

**T-36 — Gravação de auditoria com `features_hash`**
- Sprint 5 · BL-29 · RF-15, RNF-03, RNF-06 · CA-30, CA-31, CA-32
- `SecurityAndComplianceAgent`
- Skills: `audit_logging`, `privacy_by_design`
- Arquivos: `lib/db.py`
- Dependências: T-35
- Teste: `tests/integration/test_auditoria_predicoes.py`
- Evidência: dump anonimizado em `docs/seguranca/`
- **Pronto quando:** `features_hash` é SHA-256 das features canonicalizadas; `top_features`
  persiste **sem** a chave `value`; duas submissões idênticas produzem o mesmo hash; falha de
  `INSERT` não é silenciada (marca `auditoria_falhou` e a resposta declara que não foi auditada)
- Status: **Não iniciado**

**T-37 — `lib/validacao.py`: promoção do validador determinístico**
- Sprint 5 · BL-30 · RF-23 · CA-26
- `LLMIntegrationAgent`
- Skills: `hallucination_guardrails`, `code_reading`
- Arquivos: `lib/validacao.py` (novo), `referencias/validador_resposta_llm.py` **(existente, com nota de depreciação)**
- Dependências: T-26
- Teste: `tests/unit/test_validador_anti_alucinacao.py`
- Evidência: os 6 casos do `__main__` original passando agora como testes coletados
- **Pronto quando:** o `ValidadorDeterministico` vive em `lib/validacao.py`, os 6 casos originais
  são coletados pelo `pytest`, o arquivo em `referencias/` continua existindo com nota de
  depreciação (não quebrar referências dos relatórios da Fase 3), e o `ValidadorLLM` permanece
  disponível e **desabilitado por padrão** com a razão documentada (ADR-010)
- Status: **Não iniciado**

**T-38 — Verificação de coerência numérica pós-geração**
- Sprint 5 · BL-30 · RF-23, RNF-19 · CA-26, CA-27
- `LLMIntegrationAgent`
- Skills: `llm_output_verification`, `hallucination_guardrails`
- Arquivos: `lib/validacao.py`
- Dependências: T-37
- Teste: `tests/unit/test_validador_anti_alucinacao.py`
- Evidência: métrica de taxa de descarte em `artifacts/metrics/taxa_descarte.json`
- **Pronto quando:** todo numeral do texto gerado é conferido contra o payload com tolerância de
  arredondamento; rótulo contraditório invalida o texto; a taxa de descarte é **medida e
  reportada**, não escondida; o custo é regex, sem segunda chamada ao modelo
- Status: **Não iniciado**

**T-39 — `lib/ml/llm_contract.py`: payload somente-leitura de 13 chaves**
- Sprint 5 · BL-31 · RF-13, RF-14, RNF-19 · CA-25, CA-28
- `LLMIntegrationAgent`
- Skills: `prompt_contract_design`
- Arquivos: `lib/ml/llm_contract.py` (novo)
- Dependências: T-32, T-38
- Teste: `tests/unit/test_contrato_llm.py`, `tests/unit/test_avisos_obrigatorios.py`
- Evidência: payload de exemplo por modo em `artifacts/demo/`
- **Pronto quando:** `montar_payload()` devolve as 13 chaves em **todos** os modos;
  `safety_notice` e `aviso_dados_sinteticos` são constantes do módulo e nunca omitidos; payload
  incompleto levanta `ContratoInvalidoError`
- Status: **Não iniciado**

**T-40 — Prompt de síntese e `resposta_estruturada` determinística**
- Sprint 5 · BL-31 · RF-13, RF-14 · CA-25
- `LLMIntegrationAgent`
- Skills: `prompt_contract_design`, `technical_writing`
- Arquivos: `lib/ml/llm_contract.py`
- Dependências: T-39
- Teste: `tests/unit/test_contrato_llm.py`
- Evidência: prompt e saída de exemplo por variante
- **Pronto quando:** as variantes de prompt (normal, bypass, degradado, incompleto) existem; os
  valores derivados são **pré-computados** e nunca calculados pelo LLM; e
  `resposta_estruturada(payload)` é boa o bastante para ser a única saída no perfil `ml-only`
- Status: **Não iniciado**

**T-41 — `lib/workflows/risco_ml.py`: os 16 nós**
- Sprint 5 · BL-32 · RF-12, RF-21, RF-22, RNF-09 · CA-22, CA-23, CA-24
- `LangGraphAgent`
- Skills: `langgraph_workflow_design`, `error_path_design`, `human_in_the_loop_design`
- Arquivos: `lib/workflows/risco_ml.py` (novo)
- Dependências: T-36, T-39
- Teste: `tests/integration/test_workflow_risco_ml.py`
- Evidência: diagrama do grafo compilado em `docs/arquitetura/DIAGRAMA_LANGGRAPH.md`
- **Pronto quando:** os 16 nós de `WORKFLOW_ML.md` §5 existem com `RiscoMLState` tipado;
  `build_risco_ml_workflow(chat_model, conn, retriever)` segue a assinatura dos 4 workflows
  existentes; `regras_seguranca` executa **antes** de `executar_modelo_ml` em todos os caminhos;
  exatamente uma linha de auditoria por invocação que alcance `compilar_resposta`
- Status: **Não iniciado**

**T-42 — Arestas condicionais e as quatro funções de rota**
- Sprint 5 · BL-32 · RF-12, RNF-09 · CA-09, CA-22, CA-24
- `LangGraphAgent`
- Skills: `conditional_routing`, `error_path_design`
- Arquivos: `lib/workflows/risco_ml.py`
- Dependências: T-41
- Teste: `tests/integration/test_ordem_dos_nos.py`, `tests/integration/test_caminhos_de_erro.py`
- Evidência: relatório dos 4 caminhos de exceção exercitados
- **Pronto quando:** existem 4 `add_conditional_edges`; `_rota_validacao`, `_rota_regras`,
  `_rota_modelo` e `_rota_validacao_llm` são funções puras testáveis com dicionário literal;
  `_rota_validacao_llm` roteia para o **descarte** quando `verificacao is None` (caso padrão
  conservador); nenhuma injeção de falha produz traceback na saída
- Status: **Não iniciado**

**T-43 — Nó de RAG com consulta derivada da predição e fallback sem filtro**
- Sprint 5 · BL-32 · RF-11 · CA-20, CA-21
- `RAGAgent`, `LangGraphAgent`
- Skills: `rag_retrieval_tuning`, `metadata_filtering`, `source_citation_policy`
- Arquivos: `lib/workflows/risco_ml.py`, `lib/workflows/common.py` **(existente, R-01 aditivo)**, `lib/tools.py` **(existente, R-02 `args_schema`)**
- Dependências: T-03, T-41
- Teste: `tests/integration/test_rag_no_fluxo_ml.py`, `tests/integration/test_rag_indisponivel.py`
- Evidência: payload com `retrieved_sources` e flag `fontes_sem_filtro`
- **Pronto quando:** `_montar_consulta` usa o dicionário fixo `TERMO_CLINICO` (nunca LLM, para não
  tornar a recuperação irreprodutível); busca com filtro `ginecologia_obstetricia`, repete sem
  filtro marcando `fontes_sem_filtro` se vier vazio, e declara ausência de cobertura se ainda
  assim vier vazio; exceção do Chroma degrada a citação, **não** a predição; R-01 (filtro nativo
  com detecção de suporte), R-02 (`args_schema` em `buscar_protocolo`), R-03 (truncamento
  proporcional por fonte, em vez de `[:2500]` no concatenado) e R-04 (contagem observável de
  fontes) estão implementados
- Status: **Não iniciado**

**T-44 — `FakeChatModel`: dublê determinístico de chat para o perfil `demo-cpu`**
- Sprint 5 · BL-33 · RF-19, RNF-04 · CA-36, CA-38
- `MLOpsAndDeploymentAgent`
- Skills: `llm_test_doubles`
- Arquivos: `lib/llm_fake.py` (novo)
- Dependências: T-10
- Teste: `tests/unit/test_fake_chat_model.py`
- Evidência: execução do workflow completo sem GPU e sem pesos
- **Pronto quando:** é um `BaseChatModel` que devolve respostas fixas por padrão de prompt, a mesma
  entrada produz sempre a mesma saída, e ele **não** aparece em nenhuma afirmação de qualidade do
  LLM real — seu papel é tornar o pipeline testável e o Docker verificável
- Status: **Não iniciado**

**T-45 — Nó de ML opcional em `obstetrico.py` sob flag**
- Sprint 5 · BL-34 · RF-12, RNF-20 · CA-40
- `LangGraphAgent`
- Skills: `langgraph_workflow_design`, `conditional_routing`
- Arquivos: `lib/workflows/obstetrico.py` **(existente, +1 nó sob flag)**
- Dependências: T-41
- Teste: `tests/regression/test_obstetrico_flag_desligada.py`, `tests/integration/test_obstetrico_flag_ligada.py`
- Evidência: comparação do grafo compilado nos dois estados da flag
- **Pronto quando:** com `ML_RISCO_HABILITADO=0` (padrão) o grafo compilado é idêntico ao atual;
  com a flag ligada, `classificacao_origem` passa a `'modelo_ml'` e o caminho do LLM continua
  disponível como fallback; `DadosIncompletosError` e `ModeloIndisponivelError` preservam a
  classificação do LLM sem `try/except` aninhado; o nó delega a `lib/ml/predict.py` — **o mesmo
  ponto** usado por `risco_ml.py` (mitigação de RIS-13)
- Status: **Não iniciado**

**T-46 — Décima tool `predizer_risco_gestacional`**
- Sprint 5 · BL-35 · RF-26 · CA-40
- `LLMIntegrationAgent`
- Skills: `structured_tool_design`, `pydantic_schema_design`
- Arquivos: `lib/tools.py` **(existente, +1 tool)**
- Dependências: T-26
- Teste: `tests/unit/test_tool_predicao.py`, `tests/regression/test_tools_existentes_intactas.py`
- Evidência: transcrição de consulta livre acionando a tool
- **Pronto quando:** `build_langchain_tools` devolve 10 tools, **todas** com `args_schema`
  declarado (incluindo `buscar_protocolo`, que hoje é a única sem — LAC-05); a nova tool devolve o
  mesmo payload do workflow, com os dois avisos, e mensagem de campos faltantes para entrada
  incompleta
- Status: **Não iniciado**

**T-47 — `lib/observabilidade.py`: logging estruturado com correlação**
- Sprint 5 · BL-36 · RNF-07 · —
- `MLOpsAndDeploymentAgent`
- Skills: `structured_logging`
- Arquivos: `lib/observabilidade.py` (novo)
- Dependências: T-41
- Teste: `tests/unit/test_observabilidade.py`
- Evidência: log estruturado de uma execução completa
- **Pronto quando:** cada nó de `risco_ml` emite evento de início e fim com duração; existe um
  `correlation_id` por execução; nível configurável por ambiente; zero `print` em `lib/ml/` e em
  `lib/workflows/risco_ml.py`
- Status: **Não iniciado**

**T-48 — Correção de LAC-07: devolver as 6 medidas de segurança**
- Sprint 5 · BL-37 · RF-14 · —
- `SecurityAndComplianceAgent`
- Skills: `code_reading`, `ux_error_messaging`
- Arquivos: `lib/workflows/violencia.py` **(existente)**, `lib/ui.py` **(existente)**
- Dependências: —
- Teste: `tests/regression/test_violencia_medidas.py`
- Evidência: as 6 medidas aparecendo na resposta renderizada
- **Pronto quando:** a lista `medidas` construída em `violencia.py:107-113` entra no dicionário de
  retorno do nó `_protocolo_seguranca` e chega à interface. **Melhor razão valor/esforço do
  backlog inteiro:** duas horas devolvem seis condutas de proteção a vítima de violência que o
  código já escreve e descarta
- Status: **Não iniciado**

**T-49 — Testes de integração dos caminhos e da auditoria**
- Sprint 5 · BL-38 · RF-04, RF-11, RF-15, RNF-09 · CA-08, CA-09, CA-20…CA-24, CA-30
- `TestingAndValidationAgent`
- Skills: `integration_testing`, `pytest_suite_design`
- Arquivos: `tests/integration/test_regra_precede_ml.py`, `test_ordem_dos_nos.py`, `test_modo_degradado.py`, `test_rag_no_fluxo_ml.py`, `test_rag_indisponivel.py`, `test_caminhos_de_erro.py`, `test_auditoria_predicoes.py`, `test_workflow_risco_ml.py` (novos)
- Dependências: T-42, T-43, T-44
- Teste: os próprios
- Evidência: saída do `pytest tests/integration/`
- **Pronto quando:** o caso com cefaleia intensa + escotomas + epigastralgia produz encaminhamento
  imediato **mesmo com um modelo dublê devolvendo probabilidade 0,05**, com auditoria em
  `modo='bypass_regra'`; os 4 modos gravam exatamente 1 linha cada; as 4 injeções de falha
  (modelo, LLM, retriever, banco) terminam em resposta estruturada
- Status: **Não iniciado**

---

# Sprint 6 — Interface e experiência

Escopo: BL-39…BL-43. Objetivo: o resultado do modelo chega ao profissional com incerteza,
explicação e limites visíveis.

**T-50 — Aba "Risco Gestacional (ML)" com formulário do contrato**
- Sprint 6 · BL-39 · RF-16 · CA-29, CA-33
- `DemoAndPresentationAgent`
- Skills: `gradio_ui_extension`
- Arquivos: `lib/ui.py` **(existente, +1 aba)**
- Dependências: T-41
- Teste: `tests/e2e/test_ui_aba_ml.py`, `tests/regression/test_ui_abas_existentes.py`
- Evidência: captura em `docs/demo/`
- **Pronto quando:** a 6ª aba renderiza o formulário com os 11 campos obrigatórios visualmente
  destacados e os 13 opcionais; as 5 abas atuais continuam presentes, na mesma ordem, com os
  mesmos componentes de entrada; a nova aba entra ao final, via o dicionário `workflows` que
  `build_ui` já aceita (`lib/ui.py:287-298`)
- Status: **Não iniciado**

**T-51 — Renderização de probabilidade, limiar, explicação, fontes e avisos**
- Sprint 6 · BL-40 · RF-14, RF-16, RNF-19 · CA-28, CA-29
- `DemoAndPresentationAgent`
- Skills: `gradio_ui_extension`, `explainability_reporting`
- Arquivos: `lib/ui.py`
- Dependências: T-50
- Teste: `tests/e2e/test_ui_aba_ml.py`
- Evidência: captura da saída completa
- **Pronto quando:** aparecem na tela classificação, probabilidade, **limiar aplicado**, faixa de
  probabilidade, `top_features` com direção, campos imputados, regras disparadas, fontes com
  `doc_id`, texto do LLM (quando aprovado) e os **dois** avisos — e um `<details>` com o trace dos
  nós, na convenção já usada por `_render_trace_e_fontes`
- Status: **Não iniciado**

**T-52 — Mensagens de interface para os 4 modos, sem traceback**
- Sprint 6 · BL-41 · RNF-09, RNF-17 · CA-23, CA-24
- `DemoAndPresentationAgent`
- Skills: `ux_error_messaging`
- Arquivos: `lib/ui.py`
- Dependências: T-50
- Teste: `tests/e2e/test_ui_aba_ml.py`, `tests/unit/test_mensagens_de_erro.py`
- Evidência: 4 capturas, uma por modo
- **Pronto quando:** `normal`, `incompleto`, `degradado` e `bypass_regra` têm mensagem própria
  dizendo **o que** falhou, **onde** e **o que fazer**; a degradação aparece na **primeira** seção
  da resposta, nunca em rodapé; nenhum traceback chega ao usuário
- Status: **Não iniciado**

**T-53 — `scripts/run_demo.py` com os 4 cenários**
- Sprint 6 · BL-42 · RF-17 · CA-34
- `DemoAndPresentationAgent`
- Skills: `demo_scripting`, `cli_script_design`
- Arquivos: `scripts/run_demo.py` (novo)
- Dependências: T-41, T-44
- Teste: `tests/e2e/test_run_demo.py`
- Evidência: `docs/demo/LOG_DEMO.md` + `artifacts/demo/*.json`
- **Pronto quando:** um comando prepara o banco (seed 42), reindexa os protocolos, carrega o
  modelo, roda os 4 cenários (normal, dados incompletos, emergência com bypass, modelo
  indisponível), termina com código 0 e grava as 4 saídas — **incluindo** a regeneração do banco e
  do índice, que é a mitigação direta de RIS-14
- Status: **Não iniciado**

**T-54 — Testes ponta a ponta da aba e do script de demonstração**
- Sprint 6 · BL-43 · RF-16, RF-17, RNF-04 · CA-29, CA-33, CA-34
- `TestingAndValidationAgent`
- Skills: `e2e_testing`
- Arquivos: `tests/e2e/test_ui_aba_ml.py`, `tests/e2e/test_fluxo_completo.py`, `tests/e2e/test_fluxo_dados_incompletos.py`, `tests/e2e/test_run_demo.py` (novos)
- Dependências: T-52, T-53
- Teste: os próprios
- Evidência: saída do `pytest tests/e2e/`
- **Pronto quando:** o fluxo incompleto é interrompido, complementado e retomado até a resposta
  completa dentro do teste; todos rodam com `FakeChatModel`, sem GPU e sem rede
- Status: **Não iniciado**

---

# Sprint 7 — Testes e Docker

Escopo: BL-44…BL-52. Objetivo: transformar "funciona" em evidência anexada.

**T-55 — Estrutura `tests/`, `conftest.py` e `pyproject.toml`**
- Sprint 7 · BL-44 · RF-20, RNF-04 · CA-38
- `TestingAndValidationAgent`
- Skills: `pytest_suite_design`
- Arquivos: `tests/conftest.py`, `tests/{unit,integration,e2e,regression}/`, `pyproject.toml` (novos)
- Dependências: T-18
- Teste: `pytest --collect-only`
- Evidência: coleta da suíte completa sem erro
- **Pronto quando:** as 4 pastas existem, `conftest.py` provê fixtures de banco temporário, dublê
  de chat e retriever falso, e `pyproject.toml` configura `pytest` e cobertura
- Status: **Não iniciado**

**T-56 — Testes de regressão do sistema anterior**
- Sprint 7 · BL-45 · RNF-20 · CA-33, CA-40
- `TestingAndValidationAgent`
- Skills: `regression_testing`
- Arquivos: `tests/regression/test_tools_existentes_intactas.py`, `test_grafos_existentes.py`, `test_obstetrico_flag_desligada.py`, `test_predicao_estavel.py`, `test_ui_abas_existentes.py`, `test_notebooks_intactos.py` (novos)
- Dependências: T-45, T-46
- Teste: os próprios
- Evidência: saída do `pytest tests/regression/`
- **Pronto quando:** as 9 tools originais mantêm nome, `args_schema` e formato de retorno; os 4
  grafos existentes mantêm estrutura; o obstétrico é idêntico com a flag desligada; os notebooks
  05–10 seguem executáveis (ADR-001); o mesmo payload produz a mesma probabilidade e o mesmo
  `features_hash` em duas execuções
- Status: **Não iniciado**

**T-57 — Testes estruturais: imports, docstrings, segredos, schema, versões**
- Sprint 7 · BL-46 · RNF-01, RNF-06, RNF-08, RNF-10, RNF-13 · CA-37, CA-39
- `TestingAndValidationAgent`
- Skills: `structural_testing`, `security_scanning`
- Arquivos: `tests/unit/test_arquitetura_imports.py`, `test_docstrings_publicas.py`, `test_sem_segredos.py`, `test_schema_auditoria.py`, `test_versoes_declaradas.py` (novos)
- Dependências: T-55
- Teste: os próprios
- Evidência: saída do `pytest`
- **Pronto quando:** 0 ciclos de importação em `lib/`; 0 imports de `lib.ui`, `lib.agent` ou
  `lib.llm` dentro de `lib/ml/`; 100 % das funções públicas de `lib/ml/` com docstring; 0
  ocorrências de padrão de segredo em arquivo versionado; o teste de schema **falha** se
  `predicoes_ml` ganhar coluna de valor clínico
- Status: **Não iniciado**

**T-58 — `Dockerfile` e `.dockerignore` do perfil `demo-cpu`**
- Sprint 7 · BL-47 · RF-19 · CA-36
- `MLOpsAndDeploymentAgent`
- Skills: `dockerfile_generation`
- Arquivos: `Dockerfile`, `.dockerignore` (novos)
- Dependências: T-44, T-53
- Teste: `docker build`
- Evidência: imagem construída, tamanho registrado
- **Pronto quando:** a imagem instala `requirements.txt` + `requirements-ml.txt` (**nunca**
  `requirements-llm.txt`), roda com `PERFIL_EXECUCAO=demo-cpu`, usa build em múltiplos estágios e
  base `slim`, não contém CUDA nem pesos de modelo, e o `.dockerignore` exclui `.git`, notebooks,
  `artifacts/models` e `files/`
- Status: **Não iniciado**

**T-59 — `docker-compose.yml`**
- Sprint 7 · BL-47 · RF-19 · CA-36
- `MLOpsAndDeploymentAgent`
- Skills: `docker_compose_orchestration`
- Arquivos: `docker-compose.yml` (novo)
- Dependências: T-58
- Teste: `docker compose up`
- Evidência: serviço subindo com a UI acessível
- **Pronto quando:** o compose expõe a porta do Gradio, monta `artifacts/` como volume e define as
  variáveis de ambiente a partir de `.env.example` sem exigir edição de código
- Status: **Não iniciado**

**T-60 — EXECUÇÃO REAL de `docker build` e `docker run`, com log**
- Sprint 7 · BL-48 · RF-19, RNF-11 · CA-36
- `MLOpsAndDeploymentAgent`
- Skills: `clean_environment_execution`, `dockerfile_generation`
- Arquivos: `docs/deploy/EXECUCAO_DOCKER.md` (novo)
- Dependências: T-58, T-59
- Teste: execução manual registrada
- Evidência: saída completa de `docker build` e `docker run` anexada ao documento
- **Pronto quando:** o documento contém o log **literal** das duas execuções, com data, tamanho da
  imagem e tempo. **Enquanto esse log não existir, RF-19 permanece não atendido e nenhum documento
  desta entrega pode afirmar que o Docker funciona** (ADR-005, RIS-01)
- Status: **Não iniciado**

**T-61 — EXECUÇÃO REAL do pipeline em ambiente local limpo, com log**
- Sprint 7 · BL-49 · RF-18, RNF-11 · CA-35
- `MLOpsAndDeploymentAgent`
- Skills: `clean_environment_execution`
- Arquivos: `docs/deploy/EXECUCAO_LOCAL.md` (novo)
- Dependências: T-27, T-28
- Teste: execução manual registrada
- Evidência: transcrição da sessão com tempos
- **Pronto quando:** a partir de clone limpo e venv novo, sem GPU e sem Drive, a sequência
  documentada gera o dataset, treina, avalia e produz uma predição; tempo total ≤ 15 minutos; zero
  edições de código-fonte
- Status: **Não iniciado**

**T-62 — Relatório de testes e cobertura persistidos**
- Sprint 7 · BL-50 · RF-20, RNF-04 · CA-38
- `TestingAndValidationAgent`
- Skills: `coverage_reporting`
- Arquivos: `docs/testes/RELATORIO_DE_TESTES.md`, `docs/testes/COBERTURA.md` (novos)
- Dependências: T-56, T-57
- Teste: `pytest --cov=lib/ml --cov-report=term-missing`
- Evidência: saída anexada aos dois documentos
- **Pronto quando:** 100 % dos testes passam no perfil `ml-only`, com rede desabilitada, em ≤ 5
  minutos; cobertura de linha ≥ 80 % em `lib/ml/`
- Status: **Não iniciado**

**T-63 — `pip-audit` e varredura de credenciais**
- Sprint 7 · BL-51 · RNF-05, RNF-13 · CA-37
- `SecurityAndComplianceAgent`
- Skills: `security_scanning`
- Arquivos: `docs/seguranca/AUDITORIA_DEPENDENCIAS.md` (novo)
- Dependências: T-55
- Teste: `tests/unit/test_sem_segredos.py` + `pip-audit -r requirements.txt -r requirements-ml.txt`
- Evidência: saída das duas varreduras
- **Pronto quando:** zero vulnerabilidades de severidade crítica e zero ocorrências de padrão de
  segredo na árvore de trabalho e no histórico
- Status: **Não iniciado**

**T-64 — CI no GitHub Actions para o perfil `ml-only`**
- Sprint 7 · BL-52 (`Could`) · RNF-04 · CA-38
- `MLOpsAndDeploymentAgent`
- Skills: `ci_pipeline_setup`
- Arquivos: `.github/workflows/ci.yml` (novo)
- Dependências: T-55
- Teste: execução do workflow no push
- Evidência: badge de build + log da execução
- **Pronto quando:** o pipeline instala `requirements.txt` + `requirements-ml.txt` e roda a suíte
  completa sem GPU. **Único item `Could` do backlog** — primeiro a sair se o prazo apertar
- Status: **Não iniciado**

---

# Sprint 8 — Documentação e apresentação

Escopo: BL-53…BL-58. Objetivo: fechar a rastreabilidade e comunicar com honestidade o que foi e o
que não foi validado.

**T-65 — Atualização do `README.md` e do relatório técnico**
- Sprint 8 · BL-53 · RNF-10 · —
- `DocumentationAgent`
- Skills: `technical_writing`
- Arquivos: `README.md` **(existente)**, `RELATORIO_TECNICO.md` **(existente)**, `RELATORIO_TECNICO_DETALHADO.md` **(existente)**
- Dependências: T-62
- Teste: revisão documental + verificação de links
- Evidência: documentos atualizados com a seção da nova fase
- **Pronto quando:** a nova fase está descrita; **todo número herdado da Fase 3** (6414 pares,
  5134 exemplos SFT, 1392 chunks, ROUGE-L 0,101→0,095, ~60 % de loops, +18,6 % de comprimento)
  aparece rotulado como "resultado da Fase 3, evidência externa ao repositório" (LAC-24, RIS-16);
  0 links quebrados
- Status: **Não iniciado**

**T-66 — `METRICAS_E_RESULTADOS.md` e `COMPARACAO_MODELOS.md` com saída real**
- Sprint 8 · BL-54 · RF-08, RF-09, RNF-16 · CA-16
- `DocumentationAgent`, `MachineLearningAgent`
- Skills: `metrics_reporting`, `technical_writing`
- Arquivos: `docs/ml/METRICAS_E_RESULTADOS.md` **(existente, preenchido)**, `docs/ml/COMPARACAO_MODELOS.md` **(existente, preenchido)**, `docs/ml/MODELOS_AVALIADOS.md` **(existente)**
- Dependências: T-28, T-29
- Teste: conferência cruzada documento × JSON
- Evidência: cada número com chave correspondente em `artifacts/metrics/`
- **Pronto quando:** nenhum número foi digitado à mão; a tabela comparativa traz ponto **e**
  intervalo de confiança; a acurácia consta mas não participa da regra de decisão; e, **se o ML
  não superar o baseline determinístico, o resultado é publicado como está** (RIS-03), sem
  reconfiguração do experimento
- Status: **Não iniciado**

**T-67 — `LIMITACOES_DO_MODELO.md` e consolidação dos avisos clínicos**
- Sprint 8 · BL-55 · RNF-19 · CA-27, CA-28
- `DocumentationAgent`, `SecurityAndComplianceAgent`
- Skills: `technical_writing`, `privacy_by_design`
- Arquivos: `docs/ml/LIMITACOES_DO_MODELO.md` **(existente, preenchido)**
- Dependências: T-66
- Teste: revisão de checklist documental + `tests/unit/test_avisos_obrigatorios.py`
- Evidência: documento + capturas da interface + roteiro de vídeo
- **Pronto quando:** está escrito, sem eufemismo, que (a) os dados são sintéticos, (b) as métricas
  medem a capacidade de recuperar um processo gerador que nós mesmos definimos, (c) não há
  validação clínica, (d) o modelo não é diagnóstico e não prediz desfecho materno ou fetal; e a
  taxa de descarte do texto do LLM está reportada
- Status: **Não iniciado**

**T-68 — `GUIA_DEMO.md` e `LOG_DEMO.md`**
- Sprint 8 · BL-56 · RF-17 · CA-34
- `DemoAndPresentationAgent`
- Skills: `demo_scripting`, `technical_writing`
- Arquivos: `docs/demo/GUIA_DEMO.md`, `docs/demo/LOG_DEMO.md` (novos)
- Dependências: T-53, T-60
- Teste: `tests/e2e/test_run_demo.py`
- Evidência: log real da demonstração
- **Pronto quando:** o guia diz **com todas as letras** que a demonstração em Docker usa dublê de
  LLM (`FakeChatModel`) e não o Llama 3.2 3B, e o log anexado é de execução real
- Status: **Não iniciado**

**T-69 — Atualização do roteiro de vídeo com os números reais**
- Sprint 8 · BL-56 · RF-17, RNF-19 · —
- `DemoAndPresentationAgent`
- Skills: `video_scripting`, `presentation_design`
- Arquivos: `docs/demo/ROTEIRO_VIDEO.md` **(existente, atualizado)**, `docs/demo/CHECKLIST_APRESENTACAO.md` **(existente)**
- Dependências: T-66, T-68
- Teste: revisão de roteiro contra `artifacts/metrics/`
- Evidência: roteiro com os placeholders substituídos por números de execução
- **Pronto quando:** nenhum número do roteiro é inventado; a narração contém a declaração explícita
  de dados sintéticos e de ausência de validação clínica; e o roteiro da Fase 3
  (`ROTEIRO_VIDEO.md` na raiz) continua intacto e referenciado
- Status: **Não iniciado**

**T-70 — Fechamento da matriz de rastreabilidade**
- Sprint 8 · BL-57 · RNF-03 · CA-16
- `DocumentationAgent`
- Skills: `traceability_matrix`
- Arquivos: `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md` **(existente)**, `docs/requisitos/CRITERIOS_DE_ACEITE.md` **(existente)**
- Dependências: todas
- Teste: conferência de contagem
- Evidência: 46 linhas com status real e caminho de evidência existente
- **Pronto quando:** cada uma das 46 linhas tem status coerente com a existência do artefato, e o
  placar dos 20 critérios da evolução reflete a realidade — inclusive se algum ficar em
  `Não atendido`
- Status: **Não iniciado**

**T-71 — `CHANGELOG.md` e higiene técnica**
- Sprint 8 · BL-58 · RNF-01, RNF-08 · —
- `ArchitectureAgent`
- Skills: `changelog_management`, `code_reading`
- Arquivos: `CHANGELOG.md` (novo), `lib/alertas.py`, `lib/mock_data.py`, `lib/tools.py`, `lib/workflows/prevencao.py`, `lib/agent.py` **(todos existentes)**
- Dependências: T-08
- Teste: `tests/unit/test_arquitetura_imports.py`, `tests/regression/test_grafos_existentes.py`
- Evidência: `CHANGELOG.md` + diff de higiene
- **Pronto quando:** `TODAY` passa a ter fonte única (resolvendo a divergência de `prevencao.py:34`
  = `2026-05-23` contra `2026-05-22` nos outros três pontos — LAC-04); os imports mortos
  (`tools.py:16`, `triagem.py:35`) foram removidos; `max_iterations` de `agent.py:54` é usado ou
  removido; o wrapper de RAG duplicado foi unificado; e nenhuma dessas mudanças alterou
  comportamento observável (regressão verde)
- Status: **Não iniciado**

---

## Consolidação

### Distribuição por sprint

| Sprint | Tarefas | IDs | Concluídas |
|---|---|---|---|
| 1 — Descoberta e diagnóstico | 7 | T-01…T-07 | 6 (documento); T-03 permanece `[VAL]` |
| 2 — Dados | 11 | T-08…T-18 | 0 |
| 3 — Modelos | 11 | T-19…T-29 | 0 |
| 4 — Explicabilidade | 5 | T-30…T-34 | 0 |
| 5 — Integração | 15 | T-35…T-49 | 0 |
| 6 — Interface e experiência | 5 | T-50…T-54 | 0 |
| 7 — Testes e Docker | 10 | T-55…T-64 | 0 |
| 8 — Documentação e apresentação | 7 | T-65…T-71 | 0 |
| **Total** | **71** | **T-01…T-71** | **6 de documentação, 0 de código** |

### Distribuição por agente

| Agente | Tarefas |
|---|---|
| `DataEngineeringAgent` | T-02, T-11, T-12, T-13, T-14, T-15, T-16, T-17 |
| `MachineLearningAgent` | T-02, T-19, T-20, T-21, T-22, T-23, T-24, T-26, T-28, T-29, T-66 |
| `ExplainabilityAgent` | T-30, T-31, T-32, T-33 |
| `RAGAgent` | T-03, T-04, T-43 |
| `LangGraphAgent` | T-04, T-41, T-42, T-43, T-45 |
| `LLMIntegrationAgent` | T-37, T-38, T-39, T-40, T-46 |
| `SecurityAndComplianceAgent` | T-09, T-35, T-36, T-48, T-63, T-67 |
| `MLOpsAndDeploymentAgent` | T-10, T-25, T-27, T-28, T-44, T-47, T-58, T-59, T-60, T-61, T-64 |
| `TestingAndValidationAgent` | T-18, T-34, T-49, T-54, T-55, T-56, T-57, T-62 |
| `DemoAndPresentationAgent` | T-50, T-51, T-52, T-53, T-68, T-69 |
| `DocumentationAgent` | T-65, T-66, T-67, T-70 |
| `ArchitectureAgent` | T-07, T-08, T-09, T-71 |
| `RequirementsAnalystAgent` | T-01, T-06 |
| `ProjectDiscoveryAgent` | T-05, T-06 |
| `EvolutionOrchestratorAgent` | coordenação, `ROADMAP_*.md`, controle de escopo |

### Tarefas do caminho crítico

`T-13 → T-15 → T-20 → T-21 → T-26 → T-30 → T-41 → T-50 → T-53 → T-58 → T-60`

Onze tarefas em sequência estrita. Atraso em qualquer uma desloca a entrega.
`T-08` e `T-10` não estão no caminho crítico mas **bloqueiam** `T-13`, `T-44` e `T-58` — são os
pré-requisitos silenciosos que mais costumam ser subestimados.

### Tarefas cuja conclusão depende de execução, não de código escrito

Merecem atenção específica porque são as que mais frequentemente são declaradas prontas sem
evidência:

| Tarefa | Por quê |
|---|---|
| T-14 | O manifesto só prova reprodutibilidade se as duas gerações foram realmente rodadas |
| T-60 | Escrever o `Dockerfile` (T-58) e executá-lo são coisas diferentes; o requisito exige a segunda |
| T-61 | O "ambiente limpo" precisa ser limpo de verdade, com log |
| T-62 | Cobertura declarada sem saída de `pytest --cov` não é cobertura |
| T-66 | Métrica publicada sem chave em `artifacts/metrics/` é número sem origem (RNF-16) |
