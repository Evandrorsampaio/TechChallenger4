# Requisitos Funcionais

**Agente responsável:** `RequirementsAnalystAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Base:** os 20 requisitos funcionais mínimos do desafio, mais 6 requisitos derivados dos documentos
vinculantes (`ARQUITETURA_ALVO.md`, `DECISOES_ARQUITETURAIS.md`, `CONTRATO_DE_DADOS.md`,
`DEFINICAO_DO_PROBLEMA.md`).

> **Status global: nada foi implementado.** Todos os requisitos deste documento estão em
> `Não iniciado`. Nenhum critério de aceite foi verificado; nenhuma evidência foi produzida.

## Convenções

| Campo | Significado |
|---|---|
| **Tipo** | `Entrada` · `Processamento` · `Saída` · `Integração` · `Operação` |
| **Prioridade** | `Obrigatório` (exigido pelo desafio) · `Desejável` (aumenta qualidade da entrega) · `Futuro` (fora do escopo desta fase) |
| **Critério de aceite** | Condição binária, verificável por execução — não por leitura |
| **Evidência esperada** | Caminho do artefato que prova o atendimento (todos **planejados**, nenhum existe) |
| **Responsável** | Um dos 15 agentes do ciclo de evolução |
| **Risco associado** | ID em `docs/03_LACUNAS_E_RISCOS.md`, Parte II |

**Faixa de IDs:** `RF-01` a `RF-26`.
`RF-01`–`RF-20` correspondem 1:1 aos 20 requisitos mínimos do desafio.
`RF-21`–`RF-26` são derivados e estão marcados como tal.

---

## 1. Entrada e validação de dados

### RF-01 — Receber dados clínicos estruturados

| Campo | Conteúdo |
|---|---|
| **Descrição** | O sistema deve aceitar um conjunto de variáveis clínicas estruturadas de uma gestante, nomeadas por campo e tipadas, conforme o contrato `risco_gestacional v1.0.0`. A entrada deve ser possível por três vias equivalentes: formulário da interface, ferramenta do agente ReAct e chamada programática (`scripts/predict.py`). |
| **Tipo** | Entrada |
| **Prioridade** | Obrigatório |
| **Justificativa** | Hoje o fluxo obstétrico recebe **texto livre** e delega ao LLM a extração dos campos (`lib/workflows/obstetrico.py:96-121`). Extração por LLM não é entrada estruturada: não tem tipo, não tem domínio e não é reprodutível. `[COD]` |
| **Dependências** | RF-24 (o schema deriva do contrato de dados) |
| **Critério de aceite** | `GestanteFeatures` aceita um payload com os 11 campos obrigatórios e os 13 opcionais, e a mesma entrada produz o mesmo objeto validado em execuções distintas. |
| **Evidência esperada** | `tests/unit/test_schema_gestante.py`; captura da aba "Risco Gestacional (ML)" em `docs/demo/` |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | — |

### RF-02 — Validar os dados de entrada

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo payload deve ser validado antes de qualquer inferência: tipo, faixa de domínio por campo, rejeição de campo desconhecido (`extra='forbid'`) e validadores cruzados de consistência obstétrica (`partos + abortos > gestacoes` e `pad_mmhg >= pas_mmhg` são inválidos). A falha deve indicar campo, valor recebido e faixa aceita. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §5. Sem `extra='forbid'`, uma feature renomeada passa silenciosamente e o modelo recebe uma matriz diferente da de treino. |
| **Dependências** | RF-01 |
| **Critério de aceite** | Cada uma das 4 classes de violação (tipo, domínio, campo desconhecido, inconsistência cruzada) produz erro identificando o campo; nenhuma delas chega ao modelo. |
| **Evidência esperada** | `tests/unit/test_validacao_entrada.py` (casos parametrizados, um por classe de violação) |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | — |

### RF-03 — Identificar e declarar campos obrigatórios ausentes

| Campo | Conteúdo |
|---|---|
| **Descrição** | Quando um campo **obrigatório** estiver ausente, o sistema não deve imputar nem predizer. Deve devolver `DadosIncompletosError` com a lista nominal dos campos faltantes e encaminhar o fluxo ao caminho human-in-the-loop (RF-21). Campos **opcionais** ausentes são imputados pelo `Pipeline` e registrados como imputados em `dados_imputados`. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §5: imputar a pressão arterial de uma gestante pela mediana da população e devolver uma probabilidade como se fosse medida é silêncio perigoso. A distinção obrigatório/opcional é o que separa "não sei" de "estimei". |
| **Dependências** | RF-02, RF-21 |
| **Critério de aceite** | Payload sem `pas_mmhg` não produz probabilidade alguma e devolve `['pas_mmhg']`; payload sem `hemoglobina_g_dl` produz predição com `dados_imputados: ['hemoglobina_g_dl']`. |
| **Evidência esperada** | `tests/unit/test_dados_incompletos.py`; `tests/e2e/test_fluxo_dados_incompletos.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | — |

---

## 2. Regras de segurança e modelos

### RF-04 — Executar regras determinísticas de segurança antes do ML

| Campo | Conteúdo |
|---|---|
| **Descrição** | O nó de regras determinísticas (`SINAIS_ALARME_OBST`, `lib/workflows/obstetrico.py:36-47`) deve executar **antes** do modelo. Quando dispara sinal de alarme, o encaminhamento imediato prevalece e o ML é ignorado — a auditoria registra `modo='bypass_regra'` e `probabilidade=NULL`. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-006. Permitir que uma probabilidade de 0,12 rebaixe "crise convulsiva em gestante" é inaceitável. O padrão já existe no projeto: `triagem.py:125-136` checa `SINAIS_EMERGENCIA` antes de consultar o LLM. `[COD]` |
| **Dependências** | RF-02 |
| **Critério de aceite** | Caso com cefaleia intensa + escotomas + epigastralgia produz encaminhamento imediato **independentemente** da probabilidade do modelo, e o registro de auditoria tem `modo='bypass_regra'`. |
| **Evidência esperada** | `tests/integration/test_regra_precede_ml.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent`, `LangGraphAgent` |
| **Risco associado** | — |

### RF-05 — Executar ao menos dois modelos de Machine Learning supervisionado

| Campo | Conteúdo |
|---|---|
| **Descrição** | Treinar e disponibilizar quatro modelos sobre o mesmo split: `DummyClassifier(strategy='prior')`, baseline determinístico por regra (`CRITERIOS_ALTO_RISCO`), Regressão Logística e Random Forest. Os dois últimos satisfazem o mínimo de "dois modelos"; os dois primeiros existem como piso de comparação. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `DEFINICAO_DO_PROBLEMA.md` §4. O baseline por regra é a peça central: ele transforma "o modelo tem boa métrica?" em "o modelo supera a regra que já temos?" — a única pergunta que justifica acrescentar ML a um sistema que já funciona. |
| **Dependências** | RF-24, RF-02 |
| **Critério de aceite** | `scripts/train.py` treina os 4, grava 4 artefatos `.joblib` e 4 `model_card.json`, com `RANDOM_SEED=42` reproduzindo as mesmas métricas em duas execuções. |
| **Evidência esperada** | `artifacts/models/*.joblib`, `artifacts/models/*/model_card.json`, log de execução em `docs/ml/` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | RIS-03 |

### RF-06 — Retornar a classificação de risco

| Campo | Conteúdo |
|---|---|
| **Descrição** | Devolver o rótulo `habitual` ou `alto_risco`, obtido pela aplicação do **limiar operacional versionado** sobre a probabilidade — nunca pelo `predict()` padrão de 0,5. O limiar usado deve acompanhar a resposta. |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-003 (binário) e `DEFINICAO_DO_PROBLEMA.md` §5.1: com falso negativo assimetricamente mais grave, o limiar é escolhido por recall ≥ 0,90 na validação, não herdado do default da biblioteca. |
| **Dependências** | RF-05, RF-07 |
| **Critério de aceite** | O payload contém `prediction` ∈ {`habitual`, `alto_risco`} e `threshold` com o mesmo valor registrado no `model_card.json` do modelo carregado. |
| **Evidência esperada** | `tests/unit/test_limiar_operacional.py`; `artifacts/metrics/limiar.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | — |

### RF-07 — Retornar as probabilidades por classe

| Campo | Conteúdo |
|---|---|
| **Descrição** | Devolver `probabilities` como dicionário nomeado por classe — `{"habitual": p0, "alto_risco": p1}` — com `p0 + p1 = 1` dentro da tolerância de ponto flutuante. A probabilidade deve ser exibida ao usuário junto do limiar. |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §5.2 preserva o **formato** do payload do enunciado (dicionário por classe) com a cardinalidade binária da estratificação MS/FEBRASGO (ADR-003). Um rótulo sem grau de confiança é exatamente o que o LLM já entrega hoje. |
| **Dependências** | RF-05 |
| **Critério de aceite** | Para qualquer entrada válida, o payload traz as duas chaves, ambas em [0, 1] e somando 1,0 ± 1e-6. |
| **Evidência esperada** | `tests/unit/test_payload_predicao.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | — |

### RF-08 — Comparar os modelos entre si

| Campo | Conteúdo |
|---|---|
| **Descrição** | Comparar os 4 modelos no **mesmo split** e nas **mesmas métricas**, com intervalo de confiança por bootstrap (1000 reamostragens) sobre o conjunto de teste, e registrar a justificativa da escolha do modelo final. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `DEFINICAO_DO_PROBLEMA.md` §9, ML-AC-02 e ML-AC-03. Sem IC, uma diferença de 0,02 em recall pode ser ruído de amostragem apresentado como superioridade. |
| **Dependências** | RF-05, RF-09 |
| **Critério de aceite** | `docs/ml/COMPARACAO_MODELOS.md` contém a tabela dos 4 modelos com ponto e IC por métrica, e cada número é rastreável a uma chave de `artifacts/metrics/comparacao.json`. |
| **Evidência esperada** | `artifacts/metrics/comparacao.json`; `docs/ml/COMPARACAO_MODELOS.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | RIS-03 |

### RF-09 — Apresentar as métricas de avaliação

| Campo | Conteúdo |
|---|---|
| **Descrição** | Reportar, em treino / validação / teste: matriz de confusão (absoluta e normalizada), precision/recall/F1 por classe e macro, ROC-AUC, **PR-AUC**, Brier score, curva de calibração, especificidade e NPV. A acurácia é reportada mas **proibida como critério isolado de escolha**. Inclui análise de erros: perfil dos falsos negativos e dos falsos positivos, e desempenho por subgrupo (faixa etária e idade gestacional). |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | `DEFINICAO_DO_PROBLEMA.md` §5.2–5.4. Com 22 % de prevalência, prever sempre "habitual" já entrega 78 % de acurácia — por isso o `DummyClassifier` existe, e por isso a acurácia isolada é enganosa. |
| **Dependências** | RF-05 |
| **Critério de aceite** | `docs/ml/METRICAS_E_RESULTADOS.md` cobre as 8 métricas nos 3 conjuntos, e nenhum número aparece sem origem em `artifacts/metrics/`. |
| **Evidência esperada** | `artifacts/metrics/*.json`; `artifacts/metrics/curva_calibracao.png`; `docs/ml/METRICAS_E_RESULTADOS.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | RIS-02, RIS-04 |

### RF-10 — Apresentar a explicabilidade da predição

| Campo | Conteúdo |
|---|---|
| **Descrição** | Para cada predição, devolver as principais variáveis que a sustentam, com nome, valor, contribuição numérica e direção (`aumenta`/`reduz`). O **método usado** deve constar do payload (`explanation_method`) e da auditoria. Explicabilidade global (importância por permutação) deve acompanhar o relatório do modelo. |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-008. Hoje a única "explicação" é a lista `raciocinio` (strings descritivas dos nós) e a heurística `estimar_confianca` (`lib/workflows/common.py:99-111`) — nenhuma das duas atribui contribuição por variável. `[COD]` |
| **Dependências** | RF-05, RF-06 |
| **Critério de aceite** | O payload traz `top_features` com ao menos 3 entradas e `explanation_method` ∈ {`shap_tree_explainer`, `coef_linear`, `permutacao`}; com `shap` desinstalado, a explicação continua sendo produzida e o método declarado muda. |
| **Evidência esperada** | `tests/unit/test_explicabilidade_fallback.py`; `artifacts/explainability/`; `docs/ml/EXPLICABILIDADE.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `ExplainabilityAgent` |
| **Risco associado** | RIS-07 |

---

## 3. Integração com o sistema existente

### RF-11 — Recuperar protocolos clínicos no RAG

| Campo | Conteúdo |
|---|---|
| **Descrição** | Após a predição, recuperar trechos de protocolo pertinentes ao perfil de risco e anexá-los ao payload em `retrieved_sources`, com `doc_id`, `category` e trecho. A resposta final deve citar as fontes recuperadas. |
| **Tipo** | Integração |
| **Prioridade** | Obrigatório |
| **Justificativa** | O RAG já existe (`common.rag_search`, `common.py:63-80`) e é reaproveitado sem alteração. O que muda é que a busca passa a ser **condicionada pela saída do modelo**, não pela descrição em texto livre. |
| **Dependências** | RF-06 |
| **Critério de aceite** | Com índice disponível, o payload traz ≥ 1 fonte com `doc_id` não nulo; com índice indisponível, o fluxo continua e declara `retrieved_sources: []` sem lançar exceção. |
| **Evidência esperada** | `tests/integration/test_rag_no_fluxo_ml.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `RAGAgent` |
| **Risco associado** | RIS-14 |

### RF-12 — Integrar o modelo ao LangGraph

| Campo | Conteúdo |
|---|---|
| **Descrição** | Criar `lib/workflows/risco_ml.py` com o workflow completo — validação, dados incompletos, human-in-the-loop, regras de segurança, inferência, explicabilidade, RAG, síntese, verificação, avisos, auditoria e compilação da resposta — incluindo **arestas condicionais reais** para os quatro caminhos de exceção. Adicionar a `obstetrico.py` um nó de ML opcional sob a flag `ML_RISCO_HABILITADO`, preservando o caminho LLM como fallback. |
| **Tipo** | Integração |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-012. Hoje apenas 2 dos 4 workflows têm aresta condicional (`triagem.py:243-245`, `violencia.py:258-262`) e o obstétrico documenta um ramo que não constrói (`obstetrico.py:1-27` vs. `344-366`). `[COD]` |
| **Dependências** | RF-02, RF-04, RF-05, RF-10, RF-11, RF-13, RF-15, RF-21, RF-22 |
| **Critério de aceite** | O grafo compilado de `risco_ml` possui ≥ 3 `add_conditional_edges`, e cada um dos 4 caminhos de exceção é alcançado por ao menos um teste. Com `ML_RISCO_HABILITADO=false`, o comportamento do obstétrico é idêntico ao atual. |
| **Evidência esperada** | `tests/integration/test_workflow_risco_ml.py`; `tests/regression/test_obstetrico_flag_desligada.py`; diagrama em `docs/arquitetura/DIAGRAMA_LANGGRAPH.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `LangGraphAgent` |
| **Risco associado** | RIS-08, RIS-13 |

### RF-13 — Usar o LLM para sintetizar a resposta clínica

| Campo | Conteúdo |
|---|---|
| **Descrição** | O LLM recebe o payload já fechado (predição, probabilidades, limiar, explicação, fontes, regras disparadas) e produz um texto clínico em PT-BR. Ele consome os números como **somente leitura** e não participa da decisão. |
| **Tipo** | Integração |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-007. O valor do LLM aqui é reunir predição, explicação e protocolo num texto coerente — não decidir. A decisão sai da camada 4/5. |
| **Dependências** | RF-06, RF-07, RF-10, RF-11 |
| **Critério de aceite** | O prompt enviado contém os números do payload, e a resposta gerada passa pela verificação de RF-23 antes de ser exibida. |
| **Evidência esperada** | `tests/unit/test_contrato_llm.py`; `docs/llm/CONTRATO_ENTRADA_SAIDA_LLM.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `LLMIntegrationAgent` |
| **Risco associado** | RIS-05 |

### RF-14 — Apresentar avisos de segurança e limites de uso

| Campo | Conteúdo |
|---|---|
| **Descrição** | Toda resposta deve conter, como **campos estruturados** (não apenas texto decorativo da interface): `safety_notice` (apoio à decisão, não substitui avaliação profissional) e `aviso_dados_sinteticos` (modelo treinado em dados sintéticos, sem validação clínica). Ambos são obrigatórios no payload e devem ser exibidos em todas as saídas. |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | Hoje o disclaimer existe apenas como Markdown fixo da UI (`lib/ui.py:430, 593-596`) e não faz parte do contrato de dados — some se a resposta for consumida por outra via. `[COD]` LAC-27. |
| **Dependências** | RF-06 |
| **Critério de aceite** | Nenhum payload de resposta é considerado válido sem os dois campos preenchidos; teste falha se qualquer caminho (inclusive `bypass_regra` e `degradado`) os omitir. |
| **Evidência esperada** | `tests/unit/test_avisos_obrigatorios.py`; captura da interface |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent` |
| **Risco associado** | RIS-02 |

### RF-15 — Registrar auditoria de cada predição

| Campo | Conteúdo |
|---|---|
| **Descrição** | Persistir, na nova tabela `predicoes_ml`, um registro por execução: timestamp, usuário, paciente, nome e versão do modelo, versão do dataset, `features_hash` (SHA-256, não os valores), predição, probabilidade, limiar, método de explicação, `top_features` sem o campo `value`, regras disparadas e `modo` (`normal`/`degradado`/`bypass_regra`/`incompleto`). |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §5.3. Hoje só existe `log_acesso`, que registra acesso a `registros_violencia` (`lib/tools.py:168, 190`) — nenhuma decisão clínica é persistida. `[COD]` LAC-20. |
| **Dependências** | RF-06, RF-10 |
| **Critério de aceite** | Toda execução do workflow, **inclusive as que não produzem predição**, grava exatamente uma linha com `modo` coerente; `probabilidade` e `threshold` são `NULL` nos modos sem inferência. |
| **Evidência esperada** | `tests/integration/test_auditoria_predicoes.py`; dump de exemplo em `docs/seguranca/` |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent` |
| **Risco associado** | RIS-12 |

### RF-16 — Exibir o resultado na interface

| Campo | Conteúdo |
|---|---|
| **Descrição** | Acrescentar a aba "Risco Gestacional (ML)" à UI Gradio, com formulário das variáveis do contrato (os 11 campos obrigatórios visualmente destacados), e exibição de: classificação, probabilidade, limiar aplicado, variáveis mais influentes, campos imputados, regras disparadas, fontes do RAG, texto do LLM (quando aprovado) e os dois avisos de segurança. As 5 abas atuais permanecem inalteradas. |
| **Tipo** | Saída |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §2, camada 11. `build_ui` já aceita um dicionário de workflows (`lib/ui.py:287-298`), então a extensão é aditiva por construção. `[COD]` |
| **Dependências** | RF-12, RF-14 |
| **Critério de aceite** | A aba renderiza o resultado completo para um caso válido e exibe mensagem específica (não exceção) para os casos incompleto, degradado e bypass. |
| **Evidência esperada** | `tests/e2e/test_ui_aba_ml.py`; capturas em `docs/demo/` |
| **Status** | **Não iniciado** |
| **Responsável** | `DemoAndPresentationAgent` |
| **Risco associado** | RIS-08 |

---

## 4. Execução, entrega e evidência

### RF-17 — Permitir demonstração ponta a ponta

| Campo | Conteúdo |
|---|---|
| **Descrição** | Um comando único (`python scripts/run_demo.py`) deve executar a cadeia completa: preparar o banco (seed 42), indexar protocolos, carregar o modelo, processar um conjunto de casos de demonstração (normal, dados incompletos, emergência com bypass, modelo indisponível) e imprimir/salvar as saídas. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | Hoje não existe nenhum caminho de execução fora de notebook (`[AUS]`, LAC-16). Sem comando único, a demonstração depende de sequência manual no Colab. |
| **Dependências** | RF-12, RF-18 |
| **Critério de aceite** | Em ambiente limpo, o comando termina com código de saída 0 e produz as 4 saídas esperadas em `artifacts/demo/`. |
| **Evidência esperada** | `scripts/run_demo.py`; log completo em `docs/demo/LOG_DEMO.md`; `docs/demo/GUIA_DEMO.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `DemoAndPresentationAgent` |
| **Risco associado** | RIS-14 |

### RF-18 — Permitir execução local documentada

| Campo | Conteúdo |
|---|---|
| **Descrição** | Documentar e viabilizar a execução em máquina local sem Colab, Drive ou GPU, com `requirements.txt` + `requirements-ml.txt`, configuração por variável de ambiente (`lib/config.py` + `.env.example`) e perfis `ml-only` e `demo-cpu`. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-005 e ADR-009. Os caminhos do Colab estão fixos em `lib/db.py:12` e `lib/llm.py:51`; sem camada de configuração, nada roda fora do Colab e o Docker é impossível. `[COD]` LAC-17. |
| **Dependências** | RF-24 |
| **Critério de aceite** | A partir de um clone limpo em ambiente virtual novo, a sequência documentada treina o modelo e produz uma predição, sem editar código-fonte e sem GPU. |
| **Evidência esperada** | `docs/deploy/EXECUCAO_LOCAL.md` com log de sessão real; `requirements*.txt`; `.env.example` |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-11 |

### RF-19 — Permitir execução via Docker

| Campo | Conteúdo |
|---|---|
| **Descrição** | Fornecer `Dockerfile`, `.dockerignore` e `docker-compose.yml` que construam e executem o perfil `demo-cpu` — pipeline completo com dublê determinístico de LLM, sem GPU e sem pesos do Llama. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-005. A imagem com PyTorch CUDA + `bitsandbytes` + pesos do 3B passa de 8 GB e não é validável na máquina de desenvolvimento; a imagem de CPU é. |
| **Dependências** | RF-18 |
| **Critério de aceite** | `docker build` conclui sem erro e `docker run` executa a demonstração ponta a ponta, **com o log das duas execuções anexado**. Enquanto o log não existir, o requisito permanece não atendido — nenhum documento pode afirmar o contrário. |
| **Evidência esperada** | `Dockerfile`; `docs/deploy/EXECUCAO_DOCKER.md` com saída de `docker build` e `docker run` |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-01 |

### RF-20 — Produzir evidências de teste

| Campo | Conteúdo |
|---|---|
| **Descrição** | Implementar suíte automatizada em quatro níveis — unitário, integração, ponta a ponta e regressão — executável por um comando, com relatório de cobertura e saída persistida como evidência. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | Não existe **nenhum** teste automatizado hoje (`[AUS]`, LAC-13). Sem suíte, "o sistema funciona" é opinião. |
| **Dependências** | RF-01 a RF-19 |
| **Critério de aceite** | `pytest` roda a suíte completa no perfil `ml-only` com 100 % dos testes passando; o relatório de execução e a cobertura ficam versionados como evidência. |
| **Evidência esperada** | `tests/`; `docs/testes/RELATORIO_DE_TESTES.md`; `docs/testes/COBERTURA.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `TestingAndValidationAgent` |
| **Risco associado** | RIS-15 |

---

## 5. Requisitos derivados dos documentos vinculantes

> Os seis requisitos a seguir **não constam da lista mínima do desafio**. Decorrem de decisões já
> registradas em `DECISOES_ARQUITETURAIS.md` e `ARQUITETURA_ALVO.md` e são necessários para que os
> 20 anteriores sejam atendidos com correção.

### RF-21 — Solicitar complemento humano quando faltarem dados obrigatórios *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | Ao detectar campos obrigatórios ausentes, o workflow deve seguir para um nó de human-in-the-loop que devolve a lista de campos e interrompe a execução sem predizer, permitindo retomada com os dados complementados. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §4. Hoje não existe human-in-the-loop formal: o único gate humano do sistema é o checkbox `confirmacao_clinica` do fluxo de violência (`lib/ui.py:524-527`). `[COD]` LAC-19. |
| **Dependências** | RF-03, RF-12 |
| **Critério de aceite** | Entrada incompleta produz estado `dados_incompletos` com a lista de campos, sem chamada ao modelo; ao reenviar com os campos preenchidos, o fluxo prossegue normalmente. |
| **Evidência esperada** | `tests/e2e/test_fluxo_dados_incompletos.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `LangGraphAgent` |
| **Risco associado** | — |

### RF-22 — Operar em modo degradado declarado *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | Se o modelo não carregar ou a inferência falhar, o sistema deve cair para a regra determinística `CRITERIOS_ALTO_RISCO`, **declarar ao usuário** que está degradado e registrar `modo='degradado'` na auditoria, com `probabilidade=NULL`. Falha silenciosa é proibida. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §4 e §8. Nenhum workflow atual tem tratamento de erro (`[COD]` LAC-18); hoje uma exceção do modelo propagaria até o Gradio. |
| **Dependências** | RF-05, RF-12, RF-15 |
| **Critério de aceite** | Com o arquivo do modelo removido, o fluxo conclui, a resposta declara o modo degradado e a auditoria grava `modo='degradado'` com `probabilidade` nula. |
| **Evidência esperada** | `tests/integration/test_modo_degradado.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `LangGraphAgent`, `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-07 |

### RF-23 — Verificar a resposta do LLM e descartá-la em divergência *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | Após a geração, extrair os numerais do texto e verificar se cada um aparece no payload (com tolerância de arredondamento) e se o rótulo citado coincide com `prediction`. Havendo número não justificado ou contradição, **descartar o texto** e entregar a resposta estruturada determinística, declarando a substituição. Medir e reportar a taxa de descarte. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-007 e ADR-010. O validador determinístico já existe, é testado e está deliberadamente fora do pacote (`referencias/validador_resposta_llm.py:217-242`, `NotImplementedError`). `[COD]` LAC-21. |
| **Dependências** | RF-13 |
| **Critério de aceite** | Texto contendo probabilidade inexistente no payload é descartado; texto coerente é aprovado; a taxa de descarte é registrada em métrica. |
| **Evidência esperada** | `tests/unit/test_validador_anti_alucinacao.py`; `lib/validacao.py`; `docs/llm/POLITICA_ANTI_ALUCINACAO.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `LLMIntegrationAgent` |
| **Risco associado** | RIS-05, RIS-06 |

### RF-24 — Gerar e verificar o dataset sintético de forma determinística *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | `lib/ml/dataset.py` deve gerar 8 000 registros com semente 42, gravar Parquet + manifesto JSON com SHA-256, e oferecer `--verificar-dataset`, que regenera e compara o hash. O carregador deve remover `risco_latente` da matriz de features. |
| **Tipo** | Processamento |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-011 e `CONTRATO_DE_DADOS.md` §6. Não existe dataset tabular rotulado no projeto (`[COD]` LAC-02); o manifesto versionado é o que torna "reprodutível" uma afirmação verificável em vez de declarativa. |
| **Dependências** | — |
| **Critério de aceite** | Duas gerações independentes produzem o mesmo SHA-256; `--verificar-dataset` detecta qualquer divergência; `risco_latente` nunca aparece na matriz de treino. |
| **Evidência esperada** | `artifacts/data/risco_gestacional_v1.manifest.json` (versionado); `tests/unit/test_dataset_reprodutivel.py`; `tests/unit/test_dataset_sem_vazamento.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | RIS-04, RIS-11 |

### RF-25 — Registrar e carregar modelos versionados *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | `lib/ml/registry.py` deve salvar cada modelo com `model_card.json` contendo nome, versão, `dataset_version`, limiar operacional, hiperparâmetros, métricas de teste, semente e timestamp; e recusar, com erro explícito, o carregamento de modelo cuja `dataset_version` tenha MAJOR diferente do dataset corrente. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §6 e `ARQUITETURA_ALVO.md` §2, camada 4. Sem vínculo modelo↔dataset, uma mudança de feature produz predição silenciosamente errada. Não há hoje nenhum versionamento de artefato (`[AUS]`, LAC-22). |
| **Dependências** | RF-05, RF-24 |
| **Critério de aceite** | Carregar modelo treinado em `v1.x` com dataset `v2.0.0` levanta erro identificando as duas versões; carregar com MAJOR compatível funciona. |
| **Evidência esperada** | `tests/unit/test_registry_compatibilidade.py`; `artifacts/models/*/model_card.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-10 |

### RF-26 — Expor a predição como ferramenta do agente ReAct *(derivado)*

| Campo | Conteúdo |
|---|---|
| **Descrição** | Acrescentar a décima `StructuredTool`, `predizer_risco_gestacional`, com `args_schema` Pydantic completo, para que o agente da aba de consulta livre possa acionar o modelo. A tool devolve o mesmo payload do workflow, incluindo avisos. |
| **Tipo** | Integração |
| **Prioridade** | Desejável |
| **Justificativa** | `ARQUITETURA_ALVO.md` §2, camada 8. É a evidência mais direta de que o ML foi integrado ao sistema existente e não ficou num script paralelo. Declarar `args_schema` desde o início evita repetir o problema de `buscar_protocolo` (`lib/tools.py:301-306`, LAC-05). |
| **Dependências** | RF-01, RF-06, RF-14 |
| **Critério de aceite** | `build_langchain_tools` devolve 10 tools, todas com `args_schema`; a nova tool produz payload válido para entrada válida e mensagem de campos faltantes para entrada incompleta. |
| **Evidência esperada** | `tests/unit/test_tool_predicao.py`; `tests/regression/test_tools_existentes_intactas.py` |
| **Status** | **Não iniciado** |
| **Responsável** | `LLMIntegrationAgent` |
| **Risco associado** | RIS-08 |

---

## 6. Consolidação

| Prioridade | Quantidade | IDs |
|---|---|---|
| Obrigatório | 25 | RF-01 a RF-25 |
| Desejável | 1 | RF-26 |
| Futuro | 0 | — |
| **Total** | **26** | **RF-01 … RF-26** |

| Responsável | Requisitos |
|---|---|
| `DataEngineeringAgent` | RF-01, RF-02, RF-03, RF-24 |
| `MachineLearningAgent` | RF-05, RF-06, RF-07, RF-08, RF-09 |
| `ExplainabilityAgent` | RF-10 |
| `RAGAgent` | RF-11 |
| `LangGraphAgent` | RF-04 (com `SecurityAndComplianceAgent`), RF-12, RF-21, RF-22 |
| `LLMIntegrationAgent` | RF-13, RF-23, RF-26 |
| `SecurityAndComplianceAgent` | RF-04, RF-14, RF-15 |
| `DemoAndPresentationAgent` | RF-16, RF-17 |
| `MLOpsAndDeploymentAgent` | RF-18, RF-19, RF-22 (corresponsável), RF-25 |
| `TestingAndValidationAgent` | RF-20 |

**Status consolidado: 26 de 26 requisitos em `Não iniciado`.**

Os critérios de aceite em formato Dado/Quando/Então estão em
`docs/requisitos/CRITERIOS_DE_ACEITE.md`; o vínculo com arquitetura, módulo, teste e evidência está
em `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md`.
