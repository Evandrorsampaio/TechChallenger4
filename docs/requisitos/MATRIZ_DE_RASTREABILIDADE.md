> **Status real (2026-09-18):** RF-01…RF-26 e RNF-01…RNF-20 desta evolução estão **Atendidos** no código/testes/artefatos, com ressalvas: RF-11 RAG real só no perfil GPU/Colab (FakeRetriever nos testes); SHAP opcional; encoder de embeddings sem pesos locais. A tabela longa abaixo foi o plano do ciclo 1 — a evidência viva está em `docs/requisitos/CRITERIOS_DE_ACEITE.md` (20 critérios) e na suíte pytest.

# Matriz de Rastreabilidade

**Agente responsável:** `RequirementsAnalystAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Cobertura:** 26 requisitos funcionais (`RF-01`–`RF-26`) + 20 não funcionais (`RNF-01`–`RNF-20`) = **46 linhas**

> ## Aviso obrigatório sobre o status
>
> **Todas as 46 linhas desta matriz estão com status `Pendente`.**
>
> Nenhum módulo listado na coluna "Módulo/arquivo" existe no repositório. Nenhum teste listado foi
> escrito. Nenhum artefato de evidência foi produzido. Todos os caminhos são **planejados** — eles
> descrevem onde a implementação **deverá** estar, conforme `docs/arquitetura/ARQUITETURA_ALVO.md`
> §7, e servem para que a implementação seja verificável contra o plano, não para sugerir que já
> ocorreu.
>
> Os únicos arquivos desta matriz que existem hoje são os documentos da coluna "Documento de
> arquitetura" e os módulos marcados com **(existente)**.

## Legenda

| Marcação | Significado |
|---|---|
| **(existente)** | Arquivo já presente no repositório; será **estendido** de forma aditiva |
| sem marcação | Arquivo **novo**, ainda não criado |
| `—` | Não aplicável a este requisito |

---

## 1. Requisitos funcionais

| Requisito | Documento de arquitetura | Módulo/arquivo que implementará | Teste que valida | Evidência esperada | Critérios | Status |
|---|---|---|---|---|---|---|
| **RF-01** Receber dados estruturados | `CONTRATO_DE_DADOS.md` §5; `ARQUITETURA_ALVO.md` §5.1 | `lib/ml/schema.py` | `tests/unit/test_schema_gestante.py` | `docs/demo/` (captura do formulário) | CA-01 | **Pendente** |
| **RF-02** Validar os dados | `CONTRATO_DE_DADOS.md` §5; `CONTRATOS_DE_COMPONENTES.md` | `lib/ml/schema.py` | `tests/unit/test_validacao_entrada.py` | Saída do `pytest` em `docs/testes/` | CA-01–CA-04 | **Pendente** |
| **RF-03** Identificar obrigatórios ausentes | `CONTRATO_DE_DADOS.md` §5; `ARQUITETURA_ALVO.md` §4 | `lib/ml/schema.py`, `lib/workflows/risco_ml.py` | `tests/unit/test_dados_incompletos.py` | Payload de exemplo com `dados_imputados` | CA-05, CA-06 | **Pendente** |
| **RF-04** Regras de segurança antes do ML | `DECISOES_ARQUITETURAIS.md` ADR-006; `FLUXOS_DE_EXECUCAO.md` | `lib/workflows/risco_ml.py` + `lib/alertas.py` **(existente)** + `SINAIS_ALARME_OBST` **(existente)** | `tests/integration/test_regra_precede_ml.py` | Linha de auditoria com `modo='bypass_regra'` | CA-08, CA-09 | **Pendente** |
| **RF-05** Dois ou mais modelos de ML | `DEFINICAO_DO_PROBLEMA.md` §4; `MODELOS_AVALIADOS.md` | `lib/ml/train.py`, `lib/ml/features.py` | `tests/integration/test_treino_completo.py` | `artifacts/models/*.joblib` | CA-13 | **Pendente** |
| **RF-06** Retornar classificação | `DEFINICAO_DO_PROBLEMA.md` §5.1; ADR-003 | `lib/ml/predict.py` | `tests/unit/test_limiar_operacional.py` | `artifacts/models/*/model_card.json` (campo `threshold`) | CA-01, CA-14 | **Pendente** |
| **RF-07** Retornar probabilidades | `ARQUITETURA_ALVO.md` §5.2 | `lib/ml/predict.py` | `tests/unit/test_payload_predicao.py` | Payload de exemplo | CA-01 | **Pendente** |
| **RF-08** Comparar modelos | `DEFINICAO_DO_PROBLEMA.md` §9 (ML-AC-02/03); `COMPARACAO_MODELOS.md` | `lib/ml/evaluate.py`, `scripts/evaluate.py` | `tests/unit/test_criterio_de_selecao.py` | `artifacts/metrics/comparacao.json` | CA-13, CA-15 | **Pendente** |
| **RF-09** Apresentar métricas | `DEFINICAO_DO_PROBLEMA.md` §5.2–5.4; `METRICAS_E_RESULTADOS.md` | `lib/ml/evaluate.py` | `tests/integration/test_metricas_reportadas.py` | `artifacts/metrics/*.json`, `curva_calibracao.png` | CA-16, CA-17 | **Pendente** |
| **RF-10** Explicabilidade | ADR-008; `EXPLICABILIDADE.md` | `lib/ml/explain.py` | `tests/unit/test_explicabilidade.py`, `tests/unit/test_explicabilidade_fallback.py` | `artifacts/explainability/` | CA-18, CA-19 | **Pendente** |
| **RF-11** RAG de protocolos | `ARQUITETURA_ALVO.md` §2 (camada 7) | `lib/workflows/risco_ml.py` + `lib/workflows/common.py::rag_search` **(existente)** | `tests/integration/test_rag_no_fluxo_ml.py`, `tests/integration/test_rag_indisponivel.py` | Payload com `retrieved_sources` | CA-20, CA-21 | **Pendente** |
| **RF-12** Integrar ao LangGraph | ADR-012; `DIAGRAMA_LANGGRAPH.md`; `FLUXOS_DE_EXECUCAO.md` | `lib/workflows/risco_ml.py`; `lib/workflows/obstetrico.py` **(existente, estendido sob flag)** | `tests/integration/test_workflow_risco_ml.py`, `tests/integration/test_ordem_dos_nos.py` | Diagrama do grafo compilado | CA-09, CA-22 | **Pendente** |
| **RF-13** LLM para síntese | ADR-007; `CONTRATO_ENTRADA_SAIDA_LLM.md` | `lib/ml/llm_contract.py` | `tests/unit/test_contrato_llm.py` | Prompt e resposta de exemplo | CA-25 | **Pendente** |
| **RF-14** Avisos de segurança | `ARQUITETURA_ALVO.md` §5.2 e §8 | `lib/ml/llm_contract.py`, `lib/workflows/risco_ml.py` | `tests/unit/test_avisos_obrigatorios.py` | Capturas da interface | CA-28, CA-29 | **Pendente** |
| **RF-15** Auditoria de predições | `ARQUITETURA_ALVO.md` §5.3; `POLITICA_DE_AUDITORIA.md` | `lib/db.py` **(existente, +tabela `predicoes_ml`)**, `lib/workflows/risco_ml.py` | `tests/integration/test_auditoria_predicoes.py` | Dump de `predicoes_ml` | CA-30, CA-32 | **Pendente** |
| **RF-16** Exibir na interface | `ARQUITETURA_ALVO.md` §2 (camada 11) e §3 | `lib/ui.py` **(existente, +1 aba)** | `tests/e2e/test_ui_aba_ml.py`, `tests/regression/test_ui_abas_existentes.py` | `docs/demo/` (capturas) | CA-29, CA-33 | **Pendente** |
| **RF-17** Demonstração ponta a ponta | `ARQUITETURA_ALVO.md` §6 (perfil `demo-cpu`) | `scripts/run_demo.py` | `tests/e2e/test_run_demo.py` | `docs/demo/LOG_DEMO.md`, `docs/demo/GUIA_DEMO.md` | CA-34 | **Pendente** |
| **RF-18** Execução local | ADR-005, ADR-009; `ESTRATEGIA_DE_ESCALABILIDADE.md` | `lib/config.py`, `requirements.txt`, `requirements-ml.txt`, `.env.example` | Execução manual registrada | `docs/deploy/EXECUCAO_LOCAL.md` (log de sessão) | CA-35 | **Pendente** |
| **RF-19** Execução via Docker | ADR-005; `DIAGRAMA_DEPLOYMENT.md` | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Execução manual registrada | `docs/deploy/EXECUCAO_DOCKER.md` (log de `build` + `run`) | CA-36 | **Pendente** |
| **RF-20** Evidências de teste | `ARQUITETURA_ALVO.md` §7 | `tests/` (unit, integration, e2e, regression), `pyproject.toml` | Suíte completa via `pytest` | `docs/testes/RELATORIO_DE_TESTES.md`, `docs/testes/COBERTURA.md` | CA-38 | **Pendente** |
| **RF-21** Human-in-the-loop | `ARQUITETURA_ALVO.md` §4 | `lib/workflows/risco_ml.py` | `tests/e2e/test_fluxo_dados_incompletos.py` | Transcrição do fluxo interrompido e retomado | CA-07 | **Pendente** |
| **RF-22** Modo degradado | `ARQUITETURA_ALVO.md` §4 e §8 | `lib/ml/predict.py`, `lib/workflows/risco_ml.py` | `tests/integration/test_modo_degradado.py` | Linha de auditoria com `modo='degradado'` | CA-23 | **Pendente** |
| **RF-23** Verificação anti-alucinação | ADR-007, ADR-010; `POLITICA_ANTI_ALUCINACAO.md` | `lib/validacao.py` (promove `referencias/validador_resposta_llm.py` **(existente)**) | `tests/unit/test_validador_anti_alucinacao.py` | Métrica de taxa de descarte | CA-26, CA-27 | **Pendente** |
| **RF-24** Dataset determinístico | ADR-011; `CONTRATO_DE_DADOS.md` §2 e §6; `ESTRATEGIA_DE_ROTULAGEM.md` | `lib/ml/dataset.py`, `scripts/train.py --gerar-dataset` | `tests/unit/test_dataset_reprodutivel.py`, `tests/unit/test_dataset_sem_vazamento.py`, `tests/unit/test_contrato_dataset.py` | `artifacts/data/risco_gestacional_v1.manifest.json` **(versionado)** | CA-10–CA-12 | **Pendente** |
| **RF-25** Registro de modelos versionados | `CONTRATO_DE_DADOS.md` §6; `ARQUITETURA_ALVO.md` §2 (camada 4) | `lib/ml/registry.py` | `tests/unit/test_registry_compatibilidade.py` | `artifacts/models/*/model_card.json` | CA-39 | **Pendente** |
| **RF-26** Tool de predição no agente | `ARQUITETURA_ALVO.md` §2 (camada 8); `COMPONENTES.md` | `lib/tools.py` **(existente, +1 tool)** | `tests/unit/test_tool_predicao.py`, `tests/regression/test_tools_existentes_intactas.py` | Transcrição de consulta livre acionando a tool | CA-40 | **Pendente** |

---

## 2. Requisitos não funcionais

| Requisito | Documento de arquitetura | Módulo/arquivo que implementará | Teste que valida | Evidência esperada | Critérios | Status |
|---|---|---|---|---|---|---|
| **RNF-01** Modularidade | `PRINCIPIOS_ARQUITETURA.md`; `DIAGRAMA_COMPONENTES.md` | `lib/ml/` (pacote), `lib/config.py`, `lib/observabilidade.py` | `tests/unit/test_arquitetura_imports.py` | Grafo de dependências atualizado | — | **Pendente** |
| **RNF-02** Reprodutibilidade | ADR-011; `DEFINICAO_DO_PROBLEMA.md` §6 | `lib/ml/dataset.py`, `lib/ml/train.py`, `requirements-ml.txt` | `tests/unit/test_dataset_reprodutivel.py` | `docs/ml/REPRODUTIBILIDADE.md` (2 execuções) | CA-10, CA-32 | **Pendente** |
| **RNF-03** Rastreabilidade | `ARQUITETURA_ALVO.md` §5.3 | `lib/db.py` **(existente)**, `lib/ml/registry.py`, esta matriz | `tests/integration/test_auditoria_predicoes.py` | `predicoes_ml` + `artifacts/metrics/` | CA-16, CA-30, CA-32 | **Pendente** |
| **RNF-04** Testabilidade | ADR-005 (perfis de execução) | `tests/conftest.py`, dublê determinístico de chat, `pyproject.toml` | `pytest --cov=lib/ml` | `docs/testes/COBERTURA.md` | CA-38 | **Pendente** |
| **RNF-05** Segurança | ADR-006; `ESTRATEGIA_DE_SEGURANCA.md` | `lib/workflows/risco_ml.py`, `lib/alertas.py` **(existente)** | `tests/integration/test_regra_precede_ml.py` + `pip-audit` | Saída do `pip-audit` | CA-08 | **Pendente** |
| **RNF-06** Privacidade | `ARQUITETURA_ALVO.md` §5.3; `LGPD_E_PRIVACIDADE.md` | `lib/db.py` **(existente, +`predicoes_ml`)** | `tests/unit/test_schema_auditoria.py` | Dump anonimizado | CA-31 | **Pendente** |
| **RNF-07** Observabilidade | `ESTRATEGIA_DE_OBSERVABILIDADE.md` | `lib/observabilidade.py` | `tests/unit/test_observabilidade.py` | Log estruturado de execução de exemplo | — | **Pendente** |
| **RNF-08** Versionamento | `CONTRATO_DE_DADOS.md` §6 | `lib/ml/registry.py`, `CHANGELOG.md` | `tests/unit/test_versoes_declaradas.py` | `CHANGELOG.md` | CA-04, CA-39 | **Pendente** |
| **RNF-09** Tratamento de erros | `ARQUITETURA_ALVO.md` §4; `FLUXOS_DE_EXECUCAO.md` | `lib/workflows/risco_ml.py` | `tests/integration/test_caminhos_de_erro.py` | Relatório dos 4 caminhos exercitados | CA-07, CA-19, CA-21, CA-23, CA-24 | **Pendente** |
| **RNF-10** Documentação | `COMPONENTES.md`; `CONTRATOS_DE_COMPONENTES.md` | docstrings de `lib/ml/*`, `README.md` **(existente, atualizado)** | `tests/unit/test_docstrings_publicas.py` | `docs/` revisada + verificação de links | — | **Pendente** |
| **RNF-11** Ambiente limpo | ADR-005 | `requirements*.txt`, `Dockerfile`, `scripts/` | Execução manual registrada | `docs/deploy/EXECUCAO_LOCAL.md`, `EXECUCAO_DOCKER.md` | CA-35, CA-36 | **Pendente** |
| **RNF-12** Configuração separada do código | ADR-009 | `lib/config.py`, `.env.example` | `tests/unit/test_configuracao_central.py` | `.env.example` completo | CA-37 | **Pendente** |
| **RNF-13** Sem credenciais hardcoded | ADR-009; `ESTRATEGIA_DE_SEGURANCA.md` | `.env.example`, `.gitignore` **(existente)** | `tests/unit/test_sem_segredos.py` | Saída da varredura | CA-37 | **Pendente** |
| **RNF-14** Versionamento de modelos | `CONTRATO_DE_DADOS.md` §6 | `lib/ml/registry.py` | `tests/unit/test_registry_compatibilidade.py` | `model_card.json` completo | CA-39 | **Pendente** |
| **RNF-15** Versionamento de datasets | ADR-011 | `lib/ml/dataset.py`, `scripts/train.py --verificar-dataset` | `tests/unit/test_dataset_reprodutivel.py` | Manifesto versionado no git | CA-10 | **Pendente** |
| **RNF-16** Registro de métricas | `DEFINICAO_DO_PROBLEMA.md` §9 (ML-AC-07) | `lib/ml/evaluate.py` | Conferência cruzada documento × JSON | `artifacts/metrics/*.json` | CA-16 | **Pendente** |
| **RNF-17** Mensagens claras de falha | `CONTRATOS_DE_COMPONENTES.md` | `lib/ml/schema.py`, `lib/ml/registry.py`, `lib/workflows/risco_ml.py` | `tests/unit/test_mensagens_de_erro.py` | Catálogo de mensagens | CA-02, CA-23, CA-24 | **Pendente** |
| **RNF-18** Dados incompletos | `CONTRATO_DE_DADOS.md` §5 | `lib/ml/schema.py`, `lib/ml/features.py` | `tests/unit/test_dados_incompletos.py` | Payload com `dados_imputados` | CA-05, CA-06, CA-11 | **Pendente** |
| **RNF-19** Limites de uso clínico | ADR-004; `LIMITACOES_DO_MODELO.md` | `lib/ml/llm_contract.py`, `lib/ui.py` **(existente)** | `tests/unit/test_avisos_obrigatorios.py` | Capturas + roteiro de vídeo | CA-27, CA-28 | **Pendente** |
| **RNF-20** Retrocompatibilidade | ADR-001, ADR-012 | `lib/db.py`, `lib/tools.py`, `lib/ui.py`, `lib/workflows/obstetrico.py` **(todos existentes, estendidos)** | `tests/regression/test_tools_existentes_intactas.py`, `test_grafos_existentes.py`, `test_obstetrico_flag_desligada.py` | `docs/testes/RELATORIO_DE_TESTES.md` | CA-33, CA-40 | **Pendente** |

---

## 3. Rastreabilidade inversa: lacuna → requisito → evidência

Esta seção fecha o ciclo do diagnóstico: cada lacuna bloqueante ou alta de
`docs/03_LACUNAS_E_RISCOS.md` é atacada por requisitos rastreáveis.

| Lacuna | Severidade | Requisitos que a fecham | Evidência que a encerra |
|---|---|---|---|
| LAC-01 ML supervisionado ausente | Bloqueante | RF-05, RF-06, RF-07, RF-08 | `artifacts/models/` + `comparacao.json` |
| LAC-02 Dataset rotulado ausente | Bloqueante | RF-24, RNF-15 | Manifesto versionado |
| LAC-03 Explicabilidade ausente | Bloqueante | RF-10 | `artifacts/explainability/` |
| LAC-13 Sem testes | Bloqueante | RF-20, RNF-04 | `docs/testes/RELATORIO_DE_TESTES.md` |
| LAC-14 Sem Dockerfile | Bloqueante | RF-19 | Log de `docker build` + `docker run` |
| LAC-15 Sem `requirements.txt` | Bloqueante | RF-18, RNF-02 | `requirements*.txt` + log de instalação limpa |
| LAC-16 Sem scripts executáveis | Bloqueante | RF-17, RF-18 | `scripts/` + `LOG_DEMO.md` |
| LAC-17 Sem camada de configuração | Bloqueante | RF-18, RNF-12 | `lib/config.py` + `.env.example` |
| LAC-07 `medidas` não retornada | Alta | RF-14 | Teste de conteúdo da resposta do fluxo de violência |
| LAC-18 Sem tratamento de erro | Alta | RF-22, RNF-09, RNF-17 | `test_caminhos_de_erro.py` |
| LAC-19 Sem human-in-the-loop | Alta | RF-03, RF-21 | `test_fluxo_dados_incompletos.py` |
| LAC-20 Sem auditoria de decisão | Alta | RF-15, RNF-03 | Dump de `predicoes_ml` |
| LAC-21 Validador não integrado | Alta | RF-23 | `lib/validacao.py` + testes |
| LAC-22 Sem versionamento de artefatos | Alta | RF-25, RNF-08, RNF-14, RNF-15, RNF-16 | `model_card.json` + manifesto |
| LAC-04 `TODAY` divergente | Média | RNF-01, RNF-02 | Constante única resolvida por configuração |
| LAC-05 Tool sem `args_schema` | Média | RF-26 | `test_tools_existentes_intactas.py` (10 tools, todas com schema) |
| LAC-06 Workflows lineares | Média | RF-12 | Diagrama do grafo compilado com arestas condicionais |
| LAC-10 Estado global de usuário | Média | RNF-05, RNF-06 | Identificação de sessão na auditoria |
| LAC-11 Consulta fora do caminho auditado | Média | RNF-06 | Revisão do caminho de leitura + teste |
| LAC-23 Sem observabilidade | Média | RNF-07 | Log estruturado de exemplo |
| LAC-24 Evidências não verificáveis | Média | RNF-03, RNF-16 | Todo número novo com artefato de origem |
| LAC-27 Avisos não estruturados | Baixa | RF-14, RNF-19 | `test_avisos_obrigatorios.py` |

`[INF]` As lacunas LAC-08, LAC-09, LAC-12, LAC-25, LAC-26 e LAC-28 (severidade baixa) não têm
requisito dedicado. Serão tratadas como itens de higiene técnica no backlog
(`docs/requisitos/BACKLOG_PRIORIZADO.md`), sem elevar o escopo obrigatório da entrega.

---

## 4. Consolidação

| Indicador | Valor |
|---|---|
| Requisitos funcionais rastreados | 26 de 26 |
| Requisitos não funcionais rastreados | 20 de 20 |
| Requisitos com módulo planejado definido | 46 de 46 |
| Requisitos com teste planejado definido | 46 de 46 |
| Requisitos com evidência esperada definida | 46 de 46 |
| **Requisitos implementados** | **0 de 46** |
| **Requisitos verificados** | **0 de 46** |
| Status de todas as linhas | **Pendente** |

A matriz está completa como **plano de verificação**. Ela só passa a ter valor probatório quando a
coluna Status começar a mudar — e cada mudança exigirá o artefato da coluna "Evidência esperada",
não a afirmação de que o trabalho foi feito.
