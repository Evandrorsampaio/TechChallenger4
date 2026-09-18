# 03 — Lacunas e Riscos

**Agente responsável:** `ProjectDiscoveryAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Commit base:** `a8b26cd`

> **Distinção metodológica usada neste documento:**
> **Lacuna** é uma afirmação sobre o **presente** — algo que falta ou está defeituoso no
> repositório hoje, verificável por leitura de código. Tem severidade e bloqueia requisitos.
> **Risco** é uma afirmação sobre o **futuro** — algo que pode acontecer durante ou depois da
> evolução. Tem probabilidade, impacto e mitigação.
>
> Misturar os dois transforma diagnóstico em especulação. Aqui eles estão em seções separadas.

---

## Parte I — Lacunas (presente)

### Escala de severidade

| Severidade | Critério |
|---|---|
| **Bloqueante** | Impede a entrega de um requisito obrigatório do desafio. Sem isso, não há entrega |
| **Alta** | Compromete correção clínica, segurança, auditabilidade ou confiança no resultado |
| **Média** | Gera inconsistência, dívida técnica relevante ou fragilidade operacional |
| **Baixa** | Ruído, código morto ou imprecisão sem efeito funcional imediato |

### 1. Lacunas bloqueantes

| ID | Descrição | Evidência | Severidade | Requisito bloqueado |
|---|---|---|---|---|
| **LAC-01** | Não existe nenhum modelo de Machine Learning supervisionado no projeto | `[COD]` Busca por `sklearn`, `scikit-learn`, `train_test_split`, `RandomForest`, `LogisticRegression`, `XGBoost`, `GridSearchCV`, `cross_val` em todo `*.py` e `*.ipynb`: zero ocorrências. A decisão `habitual`/`alto_risco` é tomada pelo LLM em `obstetrico.py:124-144` | **Bloqueante** | RF-05, RF-06, RF-07, RF-08 |
| **LAC-02** | Não existe dataset tabular rotulado adequado a treinamento supervisionado | `[COD]` `hospital.db` (`db.py:30-103`): 50 pacientes, sem variável alvo, sem sinal vital, sem laboratório numérico, sem comorbidade estruturada. `sft_*.jsonl` são pares de chat. `files/chroma/` é índice vetorial | **Bloqueante** | RF-05, RF-24, RNF-15 |
| **LAC-03** | Não existe nenhuma forma de explicabilidade de modelo | `[COD]` Zero ocorrências de `shap`, `feature_importances_`, `permutation_importance`, `coef_`. O que existe é `raciocinio` (lista de strings descritivas dos nós) e `estimar_confianca` (heurística de 3 fatores, `common.py:99-111`) — nenhum dos dois é atribuição de contribuição por variável | **Bloqueante** | RF-10 |
| **LAC-13** | Não existe nenhum teste automatizado | `[COD]` `[AUS]` Não há `tests/`, `pytest.ini`, `conftest.py`, `pyproject.toml` nem `unittest`. A única verificação executável é o `__main__` com 6 asserts de `referencias/validador_resposta_llm.py`, que não é coletado por nenhum runner | **Bloqueante** | RF-20, RNF-04 |
| **LAC-14** | Não existe `Dockerfile`, `.dockerignore` ou `docker-compose.yml` | `[AUS]` | **Bloqueante** | RF-19, RNF-11 |
| **LAC-15** | Não existe `requirements.txt`; as dependências vivem em `!pip install -q` sem pin | `[CFG]` Apenas o notebook 03 declara faixas de versão (`transformers>=4.46,<4.50`, `peft>=0.13,<0.15`, `trl>=0.12,<0.14`). Os demais instalam sem restrição | **Bloqueante** | RF-18, RF-19, RNF-02, RNF-11 |
| **LAC-16** | Não existem scripts executáveis (`train`, `evaluate`, `predict`, `run_demo`) nem qualquer CLI | `[AUS]` Não há `scripts/`, `main.py` ou entrypoint de serviço. Todo caminho de execução passa por notebook | **Bloqueante** | RF-17, RF-18, RF-19 |
| **LAC-17** | Não existe camada de configuração; caminhos do Colab estão fixos no código | `[COD]` `lib/db.py:12` (`/content/drive/.../hospital.db`) e `lib/llm.py:51` (`DRIVE_BASE`). Não há `lib/config.py` nem `.env.example` | **Bloqueante** | RF-18, RNF-12 |

`[COD]` LAC-01, LAC-02 e LAC-03 são a tríade que define a nova fase: **não há o que avaliar, não há
com o que treinar e não há como explicar.** As demais bloqueantes são de infraestrutura e impedem
que qualquer resultado seja reproduzido fora do Colab do autor.

### 2. Lacunas de severidade alta

| ID | Descrição | Evidência | Severidade | Requisito bloqueado |
|---|---|---|---|---|
| **LAC-07** | O nó `_protocolo_seguranca` monta 6 medidas de conduta e não as devolve | `[COD]` `violencia.py:105-119`: lista `medidas` construída em `107-113`; `return` em `115-119` devolve apenas `protocolo_seguranca_ativado` e `raciocinio`. As medidas nunca chegam ao estado nem à UI | **Alta** | RF-14 |
| **LAC-18** | Nenhum dos 4 workflows tem tratamento de erro | `[COD]` Zero `try`/`except`, zero nó de fallback, zero retry, zero checkpointer em `lib/workflows/`. Exceção em `chat_model.invoke` ou `retriever.invoke` propaga até o Gradio | **Alta** | RF-22, RNF-09, RNF-17 |
| **LAC-19** | Não existe human-in-the-loop formal | `[COD]` Nenhum `interrupt`, nenhum checkpointer. O único gate humano é o checkbox `confirmacao_clinica` (`ui.py:524-527`), consumido em `violencia.py:141-145` — específico de um fluxo, não um mecanismo do sistema | **Alta** | RF-03, RF-21 |
| **LAC-20** | Não existe auditoria de decisão do sistema, apenas de acesso a dados | `[COD]` `log_acesso` (`db.py:74-82`) registra usuário, tabela, paciente e motivo — e é gravado somente nas funções de violência (`tools.py:168, 190`). Nenhuma decisão clínica (urgência, risco gestacional, plano preventivo) é persistida | **Alta** | RF-15, RNF-03 |
| **LAC-21** | O validador anti-alucinação existe, está testado e **não está integrado** | `[COD]` `referencias/validador_resposta_llm.py:217-242`, função `_esboco_integracao_NAO_USE`, termina em `raise NotImplementedError('Esboço apenas — não integrar antes da entrega')`. Nenhum módulo o importa | **Alta** | RF-23, RNF-19 |
| **LAC-22** | Não existe versionamento de artefatos de modelo, dataset ou métricas | `[AUS]` Não há `artifacts/`, `model_card.json`, manifesto de dataset nem arquivo de métricas. O `.gitignore` exclui `*.safetensors`, `*.bin`, `**/adapter_final/` `[CFG]` — o que é correto para binários, mas nada foi criado em seu lugar | **Alta** | RF-25, RNF-08, RNF-14, RNF-15, RNF-16 |

`[COD]` LAC-18 merece ênfase: o sistema atual tem exatamente **zero** caminhos de exceção
desenhados. Isso não é uma observação estética — significa que a arquitetura alvo introduz os quatro
primeiros caminhos de erro do projeto (`dados_incompletos`, `bypass_ml`, `modo_degradado`,
`usar_resposta_estruturada`), e que não há padrão interno a seguir.

### 3. Lacunas de severidade média

| ID | Descrição | Evidência | Severidade | Requisito bloqueado |
|---|---|---|---|---|
| **LAC-04** | `TODAY` replicado em 4 pontos, com `prevencao.py` um dia à frente | `[COD]` `alertas.py:16`, `mock_data.py:20`, `tools.py:100` = `2026-05-22`; `prevencao.py:34` = `2026-05-23`. `prevencao` calcula vencimentos (`107, 125`) e datas de agendamento (`185-191`) contra data diferente da fonte dos atrasos | **Média** | RNF-01, RNF-02 |
| **LAC-05** | `buscar_protocolo` é a única tool sem `args_schema` | `[COD]` `tools.py:301-306` vs. as outras 8 (`255, 261, 267, 273, 279, 286, 292, 299`) | **Média** | RF-11 |
| **LAC-06** | Dois dos quatro workflows compilam grafos lineares; o obstétrico ainda documenta um ramo que não existe | `[COD]` `obstetrico.py:1-27` desenha `emergência? → alerta_emerg`; `obstetrico.py:344-366` usa só `add_edge`. `prevencao.py:287-293` idem. Só `triagem` (`243-245`) e `violencia` (`258-262`) ramificam | **Média** | RF-12 |
| **LAC-10** | `_USUARIO_ATUAL` é estado global mutável de módulo | `[COD]` `tools.py:21`, escrito em `ui.py:318` e `violencia.py:157`. O Gradio cria uma thread por requisição (`db.py:22-24` reconhece isso ao usar `check_same_thread=False`), logo duas sessões compartilham o identificador | **Média** | RNF-05, RNF-06 |
| **LAC-11** | A existência de registros de violência é consultada fora do caminho auditado | `[COD]` `ui.py:63-66` faz `SELECT COUNT(*) FROM registros_violencia` direto, sem passar por `tools.consultar_violencia`, que exige motivo e grava em `log_acesso` | **Média** | RNF-06 |
| **LAC-23** | Não existe logging estruturado nem observabilidade | `[COD]` Não há `import logging` em `lib/`. A saída de diagnóstico é `print` (`llm.py:72, 74`, `mock_data.py:400`). Não há correlação de execução, tempo por nó, nem contagem de falhas | **Média** | RNF-07 |
| **LAC-24** | Os resultados da fase anterior não são verificáveis a partir do repositório | `[COD]` Outputs dos notebooks 02 e 04 limpos; `eval_report.json`, `sft_*.jsonl`, `files/chroma/` e `hospital.db` são gitignored `[CFG]`. Os números do `README.md` (6414, 5134, 1392, ROUGE-L 0,101→0,095, ~60 % de loops, +18,6 % de comprimento) são `[DOC]` sem respaldo `[COD]` | **Média** | RNF-03 |

`[COD]` Sobre LAC-24, a formulação precisa importa: **não há evidência de que esses números sejam
falsos.** Há ausência de evidência dentro do repositório, o que os torna `[VAL]` — dependentes de
artefatos externos. A consequência prática é que nenhum documento da nova fase pode reutilizá-los
como métrica própria sem rotulá-los como resultado da Fase 3 pendente de validação externa.

### 4. Lacunas de severidade baixa

| ID | Descrição | Evidência | Severidade | Requisito bloqueado |
|---|---|---|---|---|
| **LAC-08** | `build_agent` declara `max_iterations=6` e nunca o utiliza | `[COD]` `agent.py:54-55` na assinatura; `agent.py:65-69` não o repassa a `create_react_agent`. O limite real é `recursion_limit=12` (`agent.py:74, 94`) | **Baixa** | RNF-10 |
| **LAC-09** | Dois imports internos declarados e não usados | `[COD]` `tools.py:16` (`db_mod`), `triagem.py:35` (`tools_mod`) | **Baixa** | RNF-01 |
| **LAC-12** | O wrapper de RAG está duplicado em dois módulos | `[COD]` `common.rag_search` (`common.py:63-80`) e `tools.buscar_protocolo` (`tools.py:215-237`) implementam o mesmo algoritmo com defaults ligeiramente diferentes | **Baixa** | RNF-01 |
| **LAC-25** | Não existe `.env.example` nem documentação de variáveis de ambiente | `[AUS]` As três variáveis em uso (`HF_TOKEN`, `HOSPITAL_DB_PATH`, `DRIVE_BASE`) só são descobertas lendo código | **Baixa** | RNF-12, RNF-13 |
| **LAC-26** | Não existe CI/CD | `[AUS]` Sem `.github/workflows/`, sem `Makefile` | **Baixa** | RNF-04 |
| **LAC-27** | Os avisos de segurança clínica não são campo estruturado da resposta | `[COD]` Existe disclaimer em texto fixo na UI (`ui.py:430, 593-596`), mas nenhuma `resposta_estruturada` dos 4 workflows contém campo de aviso. O aviso é de apresentação, não do contrato de dados | **Baixa** | RF-14, RNF-19 |
| **LAC-28** | Os 6 templates clínicos em `lib/templates/` não são referenciados por nenhum código | `[COD]` Busca por `templates` em `lib/*.py` e `lib/workflows/*.py`: zero ocorrências | **Baixa** | RNF-10 |

### 5. Consolidação

| Severidade | Quantidade | IDs |
|---|---|---|
| Bloqueante | 8 | LAC-01, LAC-02, LAC-03, LAC-13, LAC-14, LAC-15, LAC-16, LAC-17 |
| Alta | 6 | LAC-07, LAC-18, LAC-19, LAC-20, LAC-21, LAC-22 |
| Média | 7 | LAC-04, LAC-05, LAC-06, LAC-10, LAC-11, LAC-23, LAC-24 |
| Baixa | 7 | LAC-08, LAC-09, LAC-12, LAC-25, LAC-26, LAC-27, LAC-28 |
| **Total** | **28** | — |

**Status de todas as lacunas:** `Não iniciado`. Nenhuma correção foi implementada.

---

## Parte II — Riscos (futuro)

### Escala

| Probabilidade | Critério | Impacto | Critério |
|---|---|---|---|
| Alta | Ocorre salvo ação deliberada | Crítico | Inviabiliza a entrega ou produz afirmação falsa publicada |
| Média | Plausível no horizonte de 8 sprints | Alto | Compromete um requisito obrigatório |
| Baixa | Exige conjunção de fatores | Moderado | Degrada qualidade, com contorno possível |

### Registro de riscos

| ID | Risco | Prob. | Impacto | Gatilho observável | Mitigação planejada | Responsável |
|---|---|---|---|---|---|---|
| **RIS-01** | Declarar "Docker funcional" sem ter executado `docker build` e `docker run` | **Alta** | **Crítico** | Documento de deploy sem log anexado | ADR-005 já condiciona a afirmação à evidência: nenhum documento pode afirmar que o Docker funciona antes do log estar em `docs/deploy/EXECUCAO_DOCKER.md`. Perfil `demo-cpu` sem GPU torna o build executável na máquina atual (Docker 29.3.1 verificado) | `MLOpsAndDeploymentAgent` |
| **RIS-02** | Apresentar métricas obtidas em dado sintético como se fossem validação clínica | **Alta** | **Crítico** | Qualquer frase de resultado sem o aviso de dados sintéticos | `aviso_dados_sinteticos` é campo **obrigatório** do payload (ARQUITETURA_ALVO §5.2) e aparece na UI, no relatório e na apresentação. Revisão explícita de linguagem em todo documento de resultado | `MachineLearningAgent`, `DocumentationAgent` |
| **RIS-03** | O modelo de ML não superar o baseline determinístico, tornando o ML injustificado | **Média** | **Alto** | Recall do RandomForest ≤ recall da regra `CRITERIOS_ALTO_RISCO`, com IC sobreposto | ADR-004 evita a circularidade (rótulo por modelo latente + ruído de Bernoulli), o que dá espaço real de superação. Se ainda assim empatar, o resultado será **reportado como está** e discutido em `LIMITACOES_DO_MODELO.md` — um empate honesto vale mais que um experimento ajustado para vencer | `MachineLearningAgent` |
| **RIS-04** | Vazamento de dados inflar as métricas | **Média** | **Alto** | Métrica de teste muito acima da validação; feature com \|correlação\| > 0,95 com o alvo | `risco_latente` removido no carregador, pré-processamento dentro do `Pipeline` com `fit` só no treino, limiar escolhido na validação, hash do split registrado. Teste dedicado `tests/unit/test_dataset_sem_vazamento.py` | `DataEngineeringAgent`, `TestingAndValidationAgent` |
| **RIS-05** | O LLM de 3B alterar ou inventar os números da predição na síntese | **Média** | **Crítico** | Numeral no texto gerado ausente do payload | ADR-007: verificação pós-geração por regex e **descarte** do texto em divergência, com entrega da resposta estruturada determinística | `LLMIntegrationAgent` |
| **RIS-06** | A taxa de descarte do texto do LLM ser tão alta que a demonstração pareça quebrada | **Média** | Moderado | Descarte acima de ~30 % nos casos de demonstração | Medir e **reportar** a taxa em vez de escondê-la; a resposta estruturada é completa por si só, então o sistema degrada sem perder conteúdo | `LLMIntegrationAgent`, `DemoAndPresentationAgent` |
| **RIS-07** | `shap` não instalar ou não funcionar em Python 3.13, deixando a explicabilidade indisponível | **Média** | **Alto** | Falha de import ou de build de `shap` no ambiente limpo | ADR-008: detecção em tempo de importação e fallback obrigatório (contribuição linear para LogReg, `permutation_importance` para o global), com o método usado registrado no payload e na auditoria | `ExplainabilityAgent` |
| **RIS-08** | A extensão de `db.py`, `tools.py`, `ui.py` e `obstetrico.py` quebrar os notebooks 05–10 | **Média** | **Alto** | Notebook que hoje roda passar a falhar | ADR-001 exige aditividade; a tabela `predicoes_ml` é `CREATE TABLE IF NOT EXISTS`; o nó de ML no obstétrico fica atrás da flag `ML_RISCO_HABILITADO` (ADR-012), com teste de regressão nos dois estados da flag | `ArchitectureAgent`, `TestingAndValidationAgent` |
| **RIS-09** | `HF_TOKEN` / aprovação Meta indisponível no momento da avaliação, inviabilizando o perfil `full-gpu` | **Média** | Moderado | Erro 401/403 ao baixar `meta-llama/Llama-3.2-3B-Instruct` | Os perfis `ml-only` e `demo-cpu` não dependem de modelo gated; toda a cadeia ML → explicabilidade → regras → RAG → auditoria é demonstrável sem o Llama | `MLOpsAndDeploymentAgent` |
| **RIS-10** | Divergência entre o pré-processamento de treino e o de inferência (*training/serving skew*) | **Baixa** | **Alto** | Mesma entrada produzindo probabilidades diferentes entre `evaluate` e `predict` | Um único `Pipeline` serializado é usado nas duas pontas; teste de regressão `tests/regression/test_predicao_estavel.py` fixa entradas e saídas esperadas | `MachineLearningAgent` |
| **RIS-11** | Mudança de versão de `numpy`/`scikit-learn` alterar o fluxo do RNG e quebrar a reprodutibilidade do dataset | **Baixa** | **Alto** | SHA-256 recomputado diferente do manifesto | `numpy.random.default_rng` (estável por contrato), versões pinadas em `requirements-ml.txt`, e `scripts/train.py --verificar-dataset` para detectar a divergência cedo | `DataEngineeringAgent` |
| **RIS-12** | Persistir dados clínicos sensíveis em claro na tabela de auditoria | **Baixa** | **Crítico** | Coluna com valor de feature legível em `predicoes_ml` | DDL já decide `features_hash` em vez de valores, e `top_features` sem o campo `value` (ARQUITETURA_ALVO §5.3). Teste que falha se o schema ganhar coluna de valor clínico | `SecurityAndComplianceAgent` |
| **RIS-13** | A flag `ML_RISCO_HABILITADO` criar dois caminhos divergentes para a mesma decisão clínica | **Baixa** | Moderado | Obstétrico e `risco_ml` classificando o mesmo caso de forma diferente | ADR-012 exige que ambos chamem `lib/ml/predict.py`; teste de equivalência entre os dois caminhos | `LangGraphAgent` |
| **RIS-14** | O avaliador não conseguir regenerar `hospital.db` e o índice Chroma localmente, impedindo a execução | **Média** | **Alto** | `docker run` subir com banco vazio e RAG sem resultados | `scripts/run_demo.py` deve regenerar banco (seed 42) e reindexar os protocolos no perfil `demo-cpu`; `GUIA_DEMO.md` documenta o passo a passo | `MLOpsAndDeploymentAgent`, `RAGAgent` |
| **RIS-15** | Escopo de 8 sprints exceder o tempo disponível, deixando testes e Docker para o fim e sem evidência | **Média** | **Alto** | Sprint 3 concluída com backlog das sprints 1–2 aberto | Backlog priorizado por MoSCoW com os itens `Must` de infraestrutura antecipados (`requirements.txt` e execução local já na Sprint 2); nenhum item de documentação depende de item de teste não iniciado | `EvolutionOrchestratorAgent` |
| **RIS-16** | Reutilizar os números não verificáveis da Fase 3 (LAC-24) como se fossem resultado da nova fase | **Média** | **Alto** | Número do `README.md` aparecendo em documento novo sem marcador `[VAL]` | Todo número herdado deve vir rotulado como "resultado da Fase 3, evidência externa ao repositório". Revisão cruzada obrigatória em `DocumentationAgent` | `DocumentationAgent` |

### Mapa probabilidade × impacto

| | Moderado | Alto | Crítico |
|---|---|---|---|
| **Alta** | — | — | RIS-01, RIS-02 |
| **Média** | RIS-06, RIS-09 | RIS-03, RIS-04, RIS-07, RIS-08, RIS-14, RIS-15, RIS-16 | RIS-05 |
| **Baixa** | RIS-13 | RIS-10, RIS-11 | RIS-12 |

`[INF]` Os dois riscos de probabilidade alta e impacto crítico — RIS-01 e RIS-02 — **não são
técnicos**. São riscos de **afirmação**: dizer que algo funciona sem ter executado, e apresentar um
resultado sintético como se fosse clínico. Ambos são evitáveis por disciplina de redação e por
anexar evidência; nenhum exige tecnologia adicional. São, por isso mesmo, os mais fáceis de
cometer sob pressão de prazo.

**Status de todos os riscos:** `Pendente` — nenhuma mitigação foi implementada.

---

## Próximos documentos

| Documento | Conteúdo |
|---|---|
| `docs/requisitos/REQUISITOS_FUNCIONAIS.md` | RF-01 a RF-26 |
| `docs/requisitos/REQUISITOS_NAO_FUNCIONAIS.md` | RNF-01 a RNF-20 |
| `docs/requisitos/CRITERIOS_DE_ACEITE.md` | Dado/Quando/Então por capacidade + checklist dos 20 critérios da evolução |
| `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md` | Requisito → arquitetura → módulo → teste → evidência |
| `docs/requisitos/BACKLOG_PRIORIZADO.md` | BL-01 em diante, MoSCoW, 8 sprints |
