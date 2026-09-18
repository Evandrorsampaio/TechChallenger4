# Skills reutilizáveis

**Agente responsável:** `EvolutionOrchestratorAgent`
**Uso:** cada tarefa T-xx cita skills por `snake_case`. A skill não substitui o plano da sprint; ela padroniza o *como*.

Formato de cada skill: Nome · Objetivo · Quando utilizar · Entradas · Saídas · Pré-condições · Passos · Critérios de qualidade · Erros comuns · Exemplo de uso.

---

## 1. Descoberta

### `project_inventory`
- **Objetivo.** Listar artefatos versionados e classificar origem.
- **Quando.** Início de ciclo; suspeita de arquivo fantasma.
- **Entradas.** Árvore do git, `.gitignore`.
- **Saídas.** `docs/00_INVENTARIO_PROJETO.md`.
- **Pré-condições.** Clone completo.
- **Passos.** Enumerar arquivos; marcar `[COD]/[CFG]/[DOC]/[INF]/[AUS]/[VAL]`; não assumir Drive.
- **Qualidade.** Toda afirmação tem origem. Nenhum path inventado.
- **Erros comuns.** Tratar menção no README como existência no repo.
- **Exemplo.** Inventário do ciclo 1: sem `tests/`, sem `Dockerfile`, sem sklearn.

### `repository_analysis`
- **Objetivo.** Entender pontos de entrada e fluxo real.
- **Quando.** Antes de estender um módulo.
- **Entradas.** `lib/*.py`, notebooks.
- **Saídas.** `docs/01_ESTADO_ATUAL.md`.
- **Pré-condições.** Inventário.
- **Passos.** Seguir `build_ui` → tools/workflows; anotar defaults Colab.
- **Qualidade.** Cada handler aponta arquivo:linha.
- **Erros comuns.** Descrever o sistema desejado em vez do atual.
- **Exemplo.** Aba 3 tem o único HIL formal (`confirmacao_clinica`).

### `technology_detection`
- **Objetivo.** Levantar stack e versões reais.
- **Quando.** Antes de pin de requirements.
- **Entradas.** Imports, células `pip install`.
- **Saídas.** Tabela de tecnologias do inventário.
- **Pré-condições.** —
- **Passos.** Distinguir pinado (notebook 03) vs solto.
- **Qualidade.** Versão “não pinada” é um achado, não um número chutado.
- **Erros comuns.** Copiar versões de memória.
- **Exemplo.** LangGraph sem pin; transformers pinado só no treino QLoRA.

### `architecture_reverse_engineering`
- **Objetivo.** Desenhar a arquitetura que o código implementa.
- **Quando.** Antes da arquitetura alvo.
- **Entradas.** Módulos e grafos.
- **Saídas.** `ARQUITETURA_ATUAL.md`, diagramas as-is.
- **Pré-condições.** `repository_analysis`.
- **Passos.** Camadas observadas; acoplamentos; dívidas.
- **Qualidade.** Diagrama bate com imports.
- **Erros comuns.** Desenhar camadas que não existem (ML, config).
- **Exemplo.** Decisão obstétrica no LLM, não numa camada de modelo.

### `dependency_analysis`
- **Objetivo.** Mapear acoplamento e ciclos.
- **Quando.** T-08, T-57, criação de `lib/ml/`.
- **Entradas.** Imports.
- **Saídas.** Regra: `lib/ml` não importa UI/agent/LLM.
- **Pré-condições.** —
- **Passos.** Grafo de imports; proibir ciclos novos.
- **Qualidade.** Teste estrutural T-57.
- **Erros comuns.** `risco_ml.py` importar `ui.py`.
- **Exemplo.** Tools capturam `conn` por closure — ok; estado global `_USUARIO_ATUAL` — dívida.

### `gap_analysis`
- **Objetivo.** Separar lacuna (presente) de risco (futuro).
- **Quando.** Sprint 1 e replanejamento.
- **Entradas.** Inventário + requisitos da nova fase.
- **Saídas.** LAC-01…28.
- **Pré-condições.** Código lido.
- **Passos.** Busca por sklearn/shap/pytest/Dockerfile; severidade.
- **Qualidade.** Cada lacuna tem evidência de path.
- **Erros comuns.** Misturar “pode acontecer” com “não existe”.
- **Exemplo.** LAC-01: zero ocorrências de `RandomForest`.

---

## 2. Requisitos

### `requirements_extraction`
- **Objetivo.** RF/RNF com ID e justificativa.
- **Quando.** Após lacunas.
- **Entradas.** Prompt mestre §§9–10 + código.
- **Saídas.** `REQUISITOS_*.md`.
- **Pré-condições.** Diagnóstico.
- **Passos.** Um requisito = um comportamento verificável.
- **Qualidade.** Sem “o sistema deve ser robusto” sem métrica.
- **Erros comuns.** Duplicar RF e RNF.
- **Exemplo.** RF-05 = pelo menos dois modelos preditivos.

### `acceptance_criteria_generation`
- **Objetivo.** Critérios binários Dado/Quando/Então.
- **Quando.** Junto dos requisitos.
- **Entradas.** RF/RNF.
- **Saídas.** `CRITERIOS_DE_ACEITE.md`.
- **Pré-condições.** IDs estáveis.
- **Passos.** Um CA prova um comportamento; evidência nomeada.
- **Qualidade.** Observável por teste ou log.
- **Erros comuns.** CA que depende de opinião clínica.
- **Exemplo.** CA-14: limiar escolhido na validação, não no teste.

### `traceability_matrix`
- **Objetivo.** Requisito → módulo → teste → evidência.
- **Quando.** Sprint 1 e fechamento Sprint 8.
- **Entradas.** RF/RNF, T-xx, paths de teste.
- **Saídas.** `MATRIZ_DE_RASTREABILIDADE.md`.
- **Pré-condições.** IDs.
- **Passos.** Nenhuma linha órfã; status = existência de artefato.
- **Qualidade.** Contagem RF+RNF = linhas.
- **Erros comuns.** Marcar atendido sem arquivo.
- **Exemplo.** T-70 só no fim.

### `backlog_prioritization`
- **Objetivo.** MoSCoW + sprints + caminho crítico.
- **Quando.** Após requisitos.
- **Entradas.** Lacunas, ADRs.
- **Saídas.** `BACKLOG_PRIORIZADO.md`.
- **Pré-condições.** —
- **Passos.** Must = bloqueante do desafio; Won't explícito.
- **Qualidade.** Caminho crítico declarado.
- **Erros comuns.** Docker só no fim sem T-08/T-10 cedo.
- **Exemplo.** BL-18 (baseline regra) é P e Must.

### `risk_analysis`
- **Objetivo.** Probabilidade, impacto, mitigação, contingência.
- **Quando.** Sprint 1; atualizar a cada sprint.
- **Entradas.** Lacunas, ADRs.
- **Saídas.** `ROADMAP_RISCOS.md`.
- **Pré-condições.** —
- **Passos.** Separar risco de afirmação (RIS-01/02) de risco técnico.
- **Qualidade.** Dono e indicador observável.
- **Erros comuns.** Mitigação vaga (“ter cuidado”).
- **Exemplo.** RIS-01 mitigado por T-60 com log literal.

---

## 3. Dados

### `dataset_profiling`
- **Objetivo.** Medir o que o gerador produziu.
- **Quando.** T-16, após T-13.
- **Entradas.** Parquet.
- **Saídas.** `perfil_v1.json`, seção em `QUALIDADE_DOS_DADOS.md`.
- **Pré-condições.** Dataset gerado.
- **Passos.** Distribuições, prevalência, missing; **números de execução**.
- **Qualidade.** Nenhum valor digitado à mão.
- **Erros comuns.** Copiar parâmetros do dicionário como se fossem estatísticas.
- **Exemplo.** Prevalência observada vs alvo 0,22 ± 0,02.

### `data_quality_analysis`
- **Objetivo.** Inconsistências e faixas.
- **Quando.** T-16 e testes de schema.
- **Entradas.** Contrato + Parquet.
- **Saídas.** Relatório de violações (deve ser zero no sintético controlado).
- **Pré-condições.** Contrato v1.
- **Passos.** `partos+abortos<=gestacoes`; PAD < PAS; nulos só em opcionais.
- **Qualidade.** Falha o teste se o gerador violar o contrato.
- **Erros comuns.** Aceitar PAD ≥ PAS “porque o modelo aguenta”.
- **Exemplo.** Validador cruzado em `GestanteFeatures`.

### `data_contract_generation`
- **Objetivo.** Schema versionado de features e alvo.
- **Quando.** Sprint 1 (doc) e T-11 (código).
- **Entradas.** Problema de ML, protocolos MS/FEBRASGO como vocabulário — não como rótulo.
- **Saídas.** `CONTRATO_DE_DADOS.md`, `schema.py`.
- **Pré-condições.** PC-01 fechada (24 features).
- **Passos.** Tipos, faixas, obrigatoriedade, rastreabilidade.
- **Qualidade.** `N_FEATURES` no código = enumeração do contrato.
- **Erros comuns.** 23 vs 24 silenciosos.
- **Exemplo.** 11 obrigatórios disparam HIL se ausentes.

### `labeling_strategy`
- **Objetivo.** Definir y sem circularidade.
- **Quando.** Antes do gerador.
- **Entradas.** ADR-004.
- **Saídas.** `ESTRATEGIA_DE_ROTULAGEM.md`, código do escore latente.
- **Pré-condições.** Baseline por regra especificado.
- **Passos.** Logit + interações + Bernoulli; persistir `risco_latente` só para auditoria.
- **Qualidade.** y não é função determinística das features de regra.
- **Erros comuns.** `alto_risco = any(criterios)`.
- **Exemplo.** Ruído de Bayes impede F1=1.

### `train_test_split_validation`
- **Objetivo.** Split estratificado sem vazamento.
- **Quando.** T-13.
- **Entradas.** y, seed 42.
- **Saídas.** Coluna `split`; hash no manifesto.
- **Pré-condições.** Alvo gerado.
- **Passos.** 70/15/15 estratificado; persistir; nunca resortear no treino.
- **Qualidade.** Proporção de positivos estável entre splits.
- **Erros comuns.** Split depois do scaler.
- **Exemplo.** Hash do split no `model_card`.

### `data_leakage_detection`
- **Objetivo.** Impedir features-proxy do rótulo.
- **Quando.** T-15, T-16, testes.
- **Entradas.** Colunas, correlações.
- **Saídas.** `RISCOS_DE_VAZAMENTO.md` + teste vermelho se `risco_latente` em X.
- **Pré-condições.** Loader escrito.
- **Passos.** Lista negra; correlação; pipeline fit treino.
- **Qualidade.** Teste dedicado obrigatório.
- **Erros comuns.** Deixar `risco_latente` “só um pouco”.
- **Exemplo.** `test_dataset_sem_vazamento.py`.

### `synthetic_data_generation`
- **Objetivo.** Gerar N=8000 determinístico.
- **Quando.** T-13, T-14.
- **Entradas.** Contrato, semente, coeficientes documentados.
- **Saídas.** Parquet + manifesto SHA-256.
- **Pré-condições.** `default_rng`.
- **Passos.** Amostrar X; calcular risco latente; Bernoulli; split; hash.
- **Qualidade.** Duas gerações, mesmo hash; banner SINTÉTICO.
- **Erros comuns.** `np.random.seed` legado; hash de objeto não canônico.
- **Exemplo.** `scripts/train.py --gerar-dataset`.

---

## 4. Machine Learning

### `problem_definition`
- **Objetivo.** Tarefa, alvo, métrica, o que o modelo não é.
- **Quando.** Sprint 1 e revisão de escopo.
- **Entradas.** Código obstétrico, ADR-002.
- **Saídas.** `DEFINICAO_DO_PROBLEMA.md`.
- **Pré-condições.** Lacunas.
- **Passos.** Escolher problema que já existe no sistema.
- **Qualidade.** Justificativa com path de código.
- **Erros comuns.** Escore de violência (rejeitado eticamente).
- **Exemplo.** Substituir `_avaliar_risco_gestacional`.

### `baseline_model_training`
- **Objetivo.** Piso Dummy + regra MS/FEBRASGO.
- **Quando.** T-19, antes dos modelos ML.
- **Entradas.** `CRITERIOS_ALTO_RISCO`, features.
- **Saídas.** `lib/ml/baseline.py`.
- **Pré-condições.** Schema.
- **Passos.** Disjunção documentada; mesma função do modo degradado.
- **Qualidade.** Interface `predict`/`predict_proba`.
- **Erros comuns.** Baseline só no notebook, outra função em produção.
- **Exemplo.** Idade <16 ou >35 → alto risco.

### `classification_model_training`
- **Objetivo.** Treinar LogReg e RF no split fixo.
- **Quando.** T-20.
- **Entradas.** Pipeline, y, seed.
- **Saídas.** joblib + cards.
- **Pré-condições.** T-15, T-19.
- **Passos.** GridSearchCV + StratifiedKFold(5) só no treino; `class_weight='balanced'`.
- **Qualidade.** Reproduzível; sem SMOTE.
- **Erros comuns.** CV no dataset inteiro.
- **Exemplo.** Otimizar `average_precision`.

### `model_comparison`
- **Objetivo.** Comparar 4 modelos com IC.
- **Quando.** T-22, T-66.
- **Entradas.** Métricas de teste.
- **Saídas.** `comparacao.json`, depois o doc.
- **Pré-condições.** Bootstrap.
- **Passos.** Recall/PR-AUC com IC; acurácia visível e não decisória.
- **Qualidade.** Empate reportado se IC sobrepõe.
- **Erros comuns.** Escolher pelo ponto sem IC.
- **Exemplo.** RIS-03.

### `metrics_evaluation`
- **Objetivo.** Família obrigatória de métricas.
- **Quando.** T-21.
- **Entradas.** y_true, y_prob, limiar.
- **Saídas.** JSON por modelo/split.
- **Pré-condições.** —
- **Passos.** Confusão, P/R/F1 por classe, ROC, PR, Brier, spec, NPV, acc.
- **Qualidade.** Metadados: modelo, split, dataset_version, timestamp.
- **Erros comuns.** Só acurácia.
- **Exemplo.** PR-AUC com 22 % de positivos.

### `confusion_matrix_analysis`
- **Objetivo.** Interpretar FN/FP.
- **Quando.** T-29.
- **Entradas.** Matriz de teste.
- **Saídas.** `analise_erros.json`.
- **Pré-condições.** Limiar fixo.
- **Passos.** Listar FN com fatores presentes; perfil de FP; subgrupos idade/IG.
- **Qualidade.** FN não agregados só em taxa.
- **Erros comuns.** Ignorar FN porque a acurácia é alta.
- **Exemplo.** Gestante HAS crônica classificada habitual.

### `class_imbalance_analysis`
- **Objetivo.** Não se deixar enganar pelo 78 % habitual.
- **Quando.** Treino e relatório.
- **Entradas.** Prevalência.
- **Saídas.** Dummy prior como piso; `class_weight`.
- **Pré-condições.** —
- **Passos.** Reportar prevalência por split.
- **Qualidade.** Dummy entra na tabela comparativa.
- **Erros comuns.** Oversample sintético em dado já sintético.
- **Exemplo.** Sem SMOTE (ADR de treino).

### `model_serialization`
- **Objetivo.** Versionar pipeline + card + recusa MAJOR.
- **Quando.** T-25.
- **Entradas.** Estimator fitted, métricas, limiar.
- **Saídas.** `registry.py`, `model_card.json`.
- **Pré-condições.** T-20.
- **Passos.** 9 campos do card; fail se dataset MAJOR ≠ corrente.
- **Qualidade.** Citar as duas versões no erro.
- **Erros comuns.** Pickle do modelo sem o preprocessor.
- **Exemplo.** joblib do Pipeline completo.

### `inference_pipeline_generation`
- **Objetivo.** `prever()` de produção.
- **Quando.** T-26.
- **Entradas.** `GestanteFeatures`, registry.
- **Saídas.** `predict.py` + payload.
- **Pré-condições.** Card + pipeline.
- **Passos.** Validar → transformar com pipeline salvo → limiar → payload.
- **Qualidade.** Pós-condição rótulo ⇔ P ≥ limiar; `ModeloIndisponivelError`.
- **Erros comuns.** Reinstanciar scaler na inferência.
- **Exemplo.** Tool e workflow chamam o mesmo `prever()`.

---

## 5. Explicabilidade

### `feature_importance`
- **Objetivo.** Importância global.
- **Quando.** T-32 e relatório.
- **Entradas.** Modelo + conjunto de validação.
- **Saídas.** `importancia_global.json`.
- **Pré-condições.** Modelo treinado.
- **Passos.** Permutação se não houver SHAP/coefs.
- **Qualidade.** Escopo `global` gera aviso.
- **Erros comuns.** Vender importância global como explicação do caso.
- **Exemplo.** Fallback quando shap falta.

### `shap_analysis`
- **Objetivo.** Contribuição local em árvores.
- **Quando.** T-30.
- **Entradas.** RF + instância.
- **Saídas.** `top_features` local.
- **Pré-condições.** Detecção de import.
- **Passos.** TreeExplainer; nunca derrubar o módulo se shap ausente.
- **Qualidade.** `explanation_method` correto.
- **Erros comuns.** Import no topo sem try.
- **Exemplo.** RIS-07.

### `prediction_explanation`
- **Objetivo.** Frase e lista para o LLM/UI.
- **Quando.** T-31, T-40, T-51.
- **Entradas.** top_features.
- **Saídas.** Texto associativo.
- **Pré-condições.** Contribuições da predição **atual**.
- **Passos.** Ordenar |contrib|; direção aumenta/reduz.
- **Qualidade.** Explicação da instância, não do treino.
- **Erros comuns.** “causou o risco”.
- **Exemplo.** “As variáveis que mais contribuíram…”

### `explanation_validation`
- **Objetivo.** Garantir correspondência explicação ↔ predição.
- **Quando.** T-34, T-33.
- **Entradas.** Payload.
- **Saídas.** Teste.
- **Pré-condições.** —
- **Passos.** Soma de sinais coerente; método declarado; fallback testado.
- **Qualidade.** Shap desinstalado ainda produz saída.
- **Erros comuns.** Explicar um modelo e servir outro.
- **Exemplo.** Monkeypatch do import.

---

## 6. LLM e RAG

### `prompt_engineering`
- **Objetivo.** Prompt de síntese com números pré-computados.
- **Quando.** T-40.
- **Entradas.** Payload 13 chaves.
- **Saídas.** Variantes normal/bypass/degradado/incompleto.
- **Pré-condições.** Contrato.
- **Passos.** Proibir o modelo de recalcular; instruir citação por `doc_id`.
- **Qualidade.** Valores derivados já vêm prontos.
- **Erros comuns.** Pedir “calcule a probabilidade”.
- **Exemplo.** `PROMPTS_DE_EXPLICACAO.md`.

### `structured_llm_output`
- **Objetivo.** Payload somente-leitura + resposta estruturada determinística.
- **Quando.** T-39.
- **Entradas.** Predição, explain, fontes, avisos.
- **Saídas.** `montar_payload()`, `resposta_estruturada()`.
- **Pré-condições.** —
- **Passos.** 13 chaves em todos os modos; avisos constantes de módulo.
- **Qualidade.** `ContratoInvalidoError` se faltar chave.
- **Erros comuns.** Omitir aviso no modo incompleto.
- **Exemplo.** Perfil `ml-only` usa só a estrutura.

### `hallucination_mitigation`
- **Objetivo.** Impedir invenção de números e de conduta sem fonte quando exigida.
- **Quando.** T-37, T-38.
- **Entradas.** Texto LLM + payload + validador determinístico.
- **Saídas.** Aprovado ou descarte.
- **Pré-condições.** Validador promovido a `lib/validacao.py`.
- **Passos.** Regex de numerais; rótulo; regras do validador existente.
- **Qualidade.** Sem segunda chamada ao LLM (ADR-010).
- **Erros comuns.** Integrar `ValidadorLLM` por padrão.
- **Exemplo.** Descarte se o texto diz `habitual` e o payload `alto_risco`.

### `rag_retrieval_validation`
- **Objetivo.** Medir e degradar com honestidade.
- **Quando.** T-43, avaliação.
- **Entradas.** Retriever, consulta fixa `TERMO_CLINICO`.
- **Saídas.** Fontes + flags `fontes_sem_filtro` / vazio.
- **Pré-condições.** Índice ou dublê.
- **Passos.** Filtro categoria; retry sem filtro; exceção não mata a predição.
- **Qualidade.** Consulta **não** gerada por LLM.
- **Erros comuns.** RAG no caminho incompleto (proibido nesta fase).
- **Exemplo.** R-01…R-04.

### `source_traceability`
- **Objetivo.** Metadados de fonte no payload.
- **Quando.** Indexação e T-43.
- **Entradas.** `doc_id`, `category`, `sensitive`, trecho.
- **Saídas.** `retrieved_sources`.
- **Pré-condições.** Metadados do notebook 06.
- **Passos.** Propagar metadados; não inventar `doc_id`.
- **Qualidade.** Trecho = o que entrou no prompt.
- **Erros comuns.** Citar 4 docs quando só 1 trecho coube.
- **Exemplo.** R-03 truncamento por fonte.

### `citation_validation`
- **Objetivo.** UI lista só fontes usadas.
- **Quando.** T-51, política de citação.
- **Entradas.** Prompt efetivo vs lista do retriever.
- **Saídas.** Lista filtrada.
- **Pré-condições.** `source_traceability`.
- **Passos.** Interseção pelo trecho anexado.
- **Qualidade.** Categoria `sensitive` exige âncora de rede (validador).
- **Erros comuns.** `citar_fontes` da Fase 3 sobre lista crua.
- **Exemplo.** ANALISE_DE_RISCOS citação falsa.

---

## 7. LangGraph

### `state_schema_design`
- **Objetivo.** `RiscoMLState` tipado `total=False`.
- **Quando.** T-41.
- **Entradas.** Contratos das camadas.
- **Saídas.** TypedDict.
- **Pré-condições.** Payload ML definido.
- **Passos.** Campos de modo, HIL, fontes, auditoria.
- **Qualidade.** Mesmo estilo dos 4 workflows atuais.
- **Erros comuns.** Estado gigante com features cruas duplicadas.
- **Exemplo.** `WORKFLOW_ML.md` §4.

### `workflow_design`
- **Objetivo.** 16 nós, assinatura `build_*(chat_model, conn, retriever)`.
- **Quando.** T-41.
- **Entradas.** Diagrama alvo.
- **Saídas.** `risco_ml.py`.
- **Pré-condições.** predict, explain, validacao, db.
- **Passos.** Implementar nós; depois rotas (T-42).
- **Qualidade.** Sem loops; compile sem checkpointer se HIL for sincrônico de sessão.
- **Erros comuns.** Enxertar 16 nós em `obstetrico.py`.
- **Exemplo.** ADR-012.

### `conditional_routing`
- **Objetivo.** Funções de rota puras.
- **Quando.** T-42.
- **Entradas.** Estado mínimo.
- **Saídas.** `_rota_*`.
- **Pré-condições.** Nós nomeados.
- **Passos.** 4 `add_conditional_edges`; default conservador no LLM (`verificacao is None` → descarte).
- **Qualidade.** Teste com dict literal, sem modelo.
- **Erros comuns.** Rota que chama LLM.
- **Exemplo.** `test_ordem_dos_nos.py`.

### `human_in_the_loop`
- **Objetivo.** Interromper quando faltam obrigatórios.
- **Quando.** T-41, T-54.
- **Entradas.** `DadosIncompletosError`.
- **Saídas.** Lista de campos + `requer_intervencao_humana`.
- **Pré-condições.** Schema.
- **Passos.** Não predizer; auditar `incompleto`; UI pede complemento e retoma.
- **Qualidade.** e2e de interrupção e retomada.
- **Erros comuns.** Imputar obrigatório para “não incomodar”.
- **Exemplo.** Ponte `hospital.db` com 6 ausentes.

### `error_recovery`
- **Objetivo.** Quatro caminhos de exceção sem traceback.
- **Quando.** T-42, T-49.
- **Entradas.** Falhas injetadas.
- **Saídas.** `resposta_estruturada` em todos.
- **Pré-condições.** Rotas.
- **Passos.** Modelo down → degradado; LLM diverge → estrutura; Chroma down → sem fontes.
- **Qualidade.** Nenhuma injeção explode o grafo.
- **Erros comuns.** `except Exception: pass`.
- **Exemplo.** `TRATAMENTO_DE_ERROS.md`.

### `workflow_observability`
- **Objetivo.** Eventos por nó com `correlation_id`.
- **Quando.** T-47.
- **Entradas.** Início/fim de nó.
- **Saídas.** `lib/observabilidade.py`.
- **Pré-condições.** T-41.
- **Passos.** Logging estruturado; zero `print` em `lib/ml` e `risco_ml`.
- **Qualidade.** Duração por nó.
- **Erros comuns.** Logar features cruas.
- **Exemplo.** Só hash e modo.

---

## 8. Qualidade

### `unit_test_generation`
- **Objetivo.** Testes rápidos sem I/O pesado.
- **Quando.** Toda tarefa de `lib/ml` e validação.
- **Entradas.** Função pura / schema.
- **Saídas.** `tests/unit/*`.
- **Pré-condições.** —
- **Passos.** Parametrizar violações de faixa.
- **Qualidade.** Sem GPU/rede/Drive.
- **Erros comuns.** Teste que treina RF completo em unit.
- **Exemplo.** `test_schema_gestante.py`.

### `integration_test_generation`
- **Objetivo.** Grafo + db + dublês.
- **Quando.** T-49, T-20.
- **Entradas.** Workflow compilado.
- **Saídas.** `tests/integration/*`.
- **Pré-condições.** `FakeChatModel`, retriever falso.
- **Passos.** Bypass, degradado, auditoria, ordem dos nós.
- **Qualidade.** 1 linha de auditoria por caso.
- **Erros comuns.** Chamar Llama real.
- **Exemplo.** P=0,05 não vence eclâmpsia.

### `regression_test_generation`
- **Objetivo.** Fase 3 intacta.
- **Quando.** T-56, a cada extensão.
- **Entradas.** Assinaturas atuais.
- **Saídas.** `tests/regression/*`.
- **Pré-condições.** Snapshot de nomes/schemas das 9 tools.
- **Passos.** Flag off; 5 abas; 4 grafos.
- **Qualidade.** Diff de grafo compilado.
- **Erros comuns.** Atualizar o snapshot “porque mudou”.
- **Exemplo.** `test_tools_existentes_intactas.py`.

### `e2e_test_generation`
- **Objetivo.** Jornada dos 4 cenários.
- **Quando.** T-54.
- **Entradas.** `run_demo` / UI.
- **Saídas.** `tests/e2e/*`.
- **Pré-condições.** T-41, T-44.
- **Passos.** Incompleto → complemento → resposta.
- **Qualidade.** FakeChatModel.
- **Erros comuns.** e2e que precisa de Colab.
- **Exemplo.** `test_fluxo_dados_incompletos.py`.

### `test_evidence_collection`
- **Objetivo.** Anexar saída real.
- **Quando.** T-62, T-60, T-61.
- **Entradas.** stdout.
- **Saídas.** `RELATORIO_DE_TESTES.md`, logs de deploy.
- **Pré-condições.** Comando executado.
- **Passos.** Colar log literal; data; comando.
- **Qualidade.** Reproduzível.
- **Erros comuns.** “todos passaram” sem arquivo.
- **Exemplo.** T-60.

### `documentation_validation`
- **Objetivo.** Cruzar doc × artefato.
- **Quando.** T-66, T-70.
- **Entradas.** Markdown + JSON.
- **Saídas.** Lista de números órfãos.
- **Pré-condições.** Métricas geradas.
- **Passos.** Cada cifra da tabela tem chave JSON.
- **Qualidade.** Zero órfãos.
- **Erros comuns.** Arredondar diferente sem dizer.
- **Exemplo.** Sprint 8.

---

## 9. Implantação

### `dockerfile_generation`
- **Objetivo.** Imagem `demo-cpu`.
- **Quando.** T-58.
- **Entradas.** requirements base+ml, entrypoint.
- **Saídas.** `Dockerfile`, `.dockerignore`.
- **Pré-condições.** T-44, T-53.
- **Passos.** slim multi-stage; sem `requirements-llm.txt`.
- **Qualidade.** Sem CUDA/pesos.
- **Erros comuns.** Copiar o adapter LoRA “por via das dúvidas”.
- **Exemplo.** ADR-005.

### `docker_build_validation`
- **Objetivo.** Provar build e run.
- **Quando.** T-60.
- **Entradas.** Dockerfile.
- **Saídas.** Log em `EXECUCAO_DOCKER.md`.
- **Pré-condições.** Docker instalado.
- **Passos.** `build` + `run` + colar stdout; tamanho; tempo.
- **Qualidade.** Sem parafrasear o log.
- **Erros comuns.** Só `docker build` sem `run`.
- **Exemplo.** RIS-01.

### `environment_configuration`
- **Objetivo.** Config por env, secrets fora do código.
- **Quando.** T-08, T-09.
- **Entradas.** Variáveis hoje lidas ad hoc.
- **Saídas.** `lib/config.py`, `.env.example`.
- **Pré-condições.** —
- **Passos.** Defaults Colab preservados; `ML_RISCO_HABILITADO=0`.
- **Qualidade.** Teste de ausência de padrões de segredo.
- **Erros comuns.** Hardcode novo path Windows.
- **Exemplo.** `HOSPITAL_DB_PATH`.

### `model_versioning`
- **Objetivo.** Card + compatibilidade de dataset.
- **Quando.** T-25, docs de deploy.
- **Entradas.** Treino.
- **Saídas.** `VERSIONAMENTO_MODELOS.md`, registry.
- **Pré-condições.** —
- **Passos.** SemVer; MAJOR se features mudam.
- **Qualidade.** Load recusa MAJOR.
- **Erros comuns.** Sobrescrever `1.0.0` sem card.
- **Exemplo.** `dataset_version` no payload.

### `reproducibility_validation`
- **Objetivo.** Mesma semente, mesmo hash/métrica.
- **Quando.** T-14, T-20, T-61.
- **Entradas.** Seeds, pins.
- **Saídas.** Logs de duas execuções.
- **Pré-condições.** Pins.
- **Passos.** Dois processos; comparar hash e, se viável, métrica.
- **Qualidade.** Divergência falha o teste, não é “quase”.
- **Erros comuns.** Aceitar hash diferente “por float”.
- **Exemplo.** `--verificar-dataset`.

---

## 10. Documentação

### `architecture_documentation`
- **Objetivo.** As-is e to-be com Mermaid e ADRs.
- **Quando.** Sprint 1; atualizar se ADR mudar.
- **Entradas.** Código + decisões.
- **Saídas.** `docs/arquitetura/*`.
- **Pré-condições.** Discovery.
- **Passos.** Contexto, alternativas, consequências.
- **Qualidade.** Status da ADR explícito.
- **Erros comuns.** ADR sem alternativa rejeitada.
- **Exemplo.** ADR-002.

### `technical_report_generation`
- **Objetivo.** Relatório da fase com limites.
- **Quando.** T-65.
- **Entradas.** Métricas, ADRs, riscos.
- **Saídas.** Relatórios técnicos.
- **Pré-condições.** T-62.
- **Passos.** Separar Fase 3 `[VAL]` da nova fase medida.
- **Qualidade.** Limitações não no apêndice escondido.
- **Erros comuns.** RIS-16.
- **Exemplo.** Banner sintético no topo.

### `readme_generation`
- **Objetivo.** Como rodar local e Docker.
- **Quando.** T-65.
- **Entradas.** Scripts, logs.
- **Saídas.** `README.md` atualizado.
- **Pré-condições.** T-61 ou declaração honesta do que falta.
- **Passos.** Quickstart `ml-only`; aviso clínico; link dos planos.
- **Qualidade.** Comandos copiáveis.
- **Erros comuns.** Quickstart que só roda no Drive do autor.
- **Exemplo.** Três perfis.

### `changelog_generation`
- **Objetivo.** Histórico por fase.
- **Quando.** T-71 e cada sprint.
- **Entradas.** Diff.
- **Saídas.** `CHANGELOG.md`.
- **Pré-condições.** —
- **Passos.** Added/Changed/Fixed; nada de “várias melhorias”.
- **Qualidade.** Paths reais.
- **Erros comuns.** Changelog antes do código.
- **Exemplo.** Sprint 2: `lib/config.py`.

### `demo_script_generation`
- **Objetivo.** Roteiro reproduzível dos 4 cenários.
- **Quando.** T-53, T-68, T-69.
- **Entradas.** Workflow, UI.
- **Saídas.** `run_demo.py`, `ROTEIRO_DEMO.md`.
- **Pré-condições.** T-41.
- **Passos.** Regenerar dados; gravar JSON; narrar avisos.
- **Qualidade.** Declara `FakeChatModel` no Docker.
- **Erros comuns.** Demo só do “caso bonito”.
- **Exemplo.** D3 emergência.

### `roadmap_generation`
- **Objetivo.** Quatro roadmaps vivos.
- **Quando.** Ciclo 1 e fim de sprint.
- **Entradas.** Backlog, T-xx, riscos.
- **Saídas.** `docs/roadmap/*`.
- **Pré-condições.** IDs estáveis.
- **Passos.** Status = artefato; nunca “quase pronto”.
- **Qualidade.** Caminho crítico visível.
- **Exemplo.** Este ciclo criou SPRINTS e RISCOS.
