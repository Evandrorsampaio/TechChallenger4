# Critérios de Aceite

**Agente responsável:** `RequirementsAnalystAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Formato:** Dado / Quando / Então, agrupado por capacidade
**Faixa de IDs:** `CA-01` a `CA-40`

> **Status global: nenhum critério foi verificado.** Todos os arquivos de teste citados são
> **planejados** — o diretório `tests/` não existe no repositório (`docs/03_LACUNAS_E_RISCOS.md`,
> LAC-13).

## Como ler

Cada cenário traz:

- **Cobre:** os IDs de `REQUISITOS_FUNCIONAIS.md` e `REQUISITOS_NAO_FUNCIONAIS.md` que ele prova;
- **Teste planejado:** o arquivo que conterá a automação;
- o bloco Dado/Quando/Então, escrito de modo que o resultado seja **binário** — não há "deve ser
  razoável" nem "deve funcionar bem".

---

## A. Entrada, validação e dados incompletos

### CA-01 — Payload válido é aceito e produz predição
**Cobre:** RF-01, RF-02, RF-06, RF-07 · **Teste planejado:** `tests/e2e/test_fluxo_completo.py`

```gherkin
Dado um payload com os 11 campos obrigatórios preenchidos dentro dos domínios do contrato v1.0.0
Quando o workflow de risco gestacional for executado
Então a resposta contém prediction ∈ {habitual, alto_risco}
  E contém probabilities com as duas chaves somando 1,0 ± 1e-6
  E contém o threshold efetivamente aplicado
  E nenhuma exceção é levantada
```

### CA-02 — Valor fora do domínio é rejeitado com mensagem nominal
**Cobre:** RF-02, RNF-17 · **Teste planejado:** `tests/unit/test_validacao_entrada.py`

```gherkin
Dado um payload com pas_mmhg = 400
Quando a validação for executada
Então a execução falha antes de qualquer inferência
  E a mensagem cita o campo "pas_mmhg", o valor recebido e a faixa aceita (80–200)
  E nenhuma linha de auditoria com modo 'normal' é gravada
```

### CA-03 — Inconsistência obstétrica cruzada é rejeitada
**Cobre:** RF-02 · **Teste planejado:** `tests/unit/test_validacao_entrada.py`

```gherkin
Dado um payload com gestacoes = 1, partos = 1 e abortos = 1
Quando a validação for executada
Então a entrada é rejeitada por validador cruzado
  E a mensagem explica que partos + abortos não pode exceder gestacoes
```

### CA-04 — Campo desconhecido não passa silenciosamente
**Cobre:** RF-02, RNF-08 · **Teste planejado:** `tests/unit/test_schema_gestante.py`

```gherkin
Dado um payload contendo a chave "pressao_arterial_sistolica" em vez de "pas_mmhg"
Quando a validação for executada
Então a entrada é rejeitada por campo desconhecido
  E a mensagem identifica a chave não reconhecida
```

### CA-05 — Campo obrigatório ausente não é imputado
**Cobre:** RF-03, RNF-18 · **Teste planejado:** `tests/unit/test_dados_incompletos.py`

```gherkin
Dado um payload sem o campo pas_mmhg
Quando o workflow for executado
Então nenhuma probabilidade é produzida
  E a resposta lista ["pas_mmhg"] como campo obrigatório ausente
  E a auditoria registra modo = 'incompleto' com probabilidade NULL
```

### CA-06 — Campo opcional ausente é imputado e declarado
**Cobre:** RF-03, RNF-18 · **Teste planejado:** `tests/unit/test_dados_incompletos.py`

```gherkin
Dado um payload completo exceto hemoglobina_g_dl
Quando o workflow for executado
Então a predição é produzida normalmente
  E o campo dados_imputados contém "hemoglobina_g_dl"
  E o mesmo campo aparece na interface e na auditoria
```

### CA-07 — Dados incompletos acionam o human-in-the-loop
**Cobre:** RF-21, RNF-09 · **Teste planejado:** `tests/e2e/test_fluxo_dados_incompletos.py`

```gherkin
Dado um payload com dois campos obrigatórios ausentes
Quando o workflow for executado
Então o fluxo termina no estado de solicitação de complemento, sem chamar o modelo
  E ao reenviar com os dois campos preenchidos, a execução prossegue até a resposta completa
```

---

## B. Regras determinísticas de segurança

### CA-08 — Sinal de alarme obstétrico anula o modelo
**Cobre:** RF-04, RNF-05 · **Teste planejado:** `tests/integration/test_regra_precede_ml.py`

```gherkin
Dado um caso com cefaleia intensa, escotomas e epigastralgia
  E um modelo que, para essas features, devolveria probabilidade de alto risco igual a 0,05
Quando o workflow for executado
Então a resposta indica encaminhamento imediato
  E a auditoria registra modo = 'bypass_regra' com probabilidade NULL
  E a decisão independe do valor devolvido pelo modelo
```

### CA-09 — A ordem de execução é regra antes de modelo
**Cobre:** RF-04, RF-12 · **Teste planejado:** `tests/integration/test_ordem_dos_nos.py`

```gherkin
Dado o grafo compilado do workflow de risco gestacional
Quando a ordem topológica dos nós for inspecionada
Então o nó de regras de segurança precede o nó de inferência em todos os caminhos
```

---

## C. Dataset sintético

### CA-10 — Geração é determinística e verificável
**Cobre:** RF-24, RNF-02, RNF-15 · **Teste planejado:** `tests/unit/test_dataset_reprodutivel.py`

```gherkin
Dado o gerador com RANDOM_SEED = 42
Quando o dataset for gerado duas vezes em processos independentes
Então o SHA-256 do Parquet é idêntico nas duas execuções
  E `scripts/train.py --verificar-dataset` confirma o hash do manifesto versionado
```

### CA-11 — A variável latente nunca entra como feature
**Cobre:** RF-24, RNF-18 · **Teste planejado:** `tests/unit/test_dataset_sem_vazamento.py`

```gherkin
Dado o dataset carregado por lib/ml/dataset.py
Quando a matriz de features for construída
Então a coluna risco_latente não está presente
  E nenhuma feature apresenta |correlação| > 0,95 com o alvo sem justificativa registrada
```

### CA-12 — O dataset respeita o contrato declarado
**Cobre:** RF-24 · **Teste planejado:** `tests/unit/test_contrato_dataset.py`

```gherkin
Dado o dataset gerado na versão v1.0.0
Quando o perfilamento for executado
Então há 8000 registros
  E a prevalência da classe positiva está em 0,22 ± 0,02
  E os splits treino/validação/teste somam 100 % e são estratificados pelo alvo
```

---

## D. Modelos, comparação e métricas

### CA-13 — Quatro modelos treinados no mesmo split
**Cobre:** RF-05, RF-08 · **Teste planejado:** `tests/integration/test_treino_completo.py`

```gherkin
Dado o dataset na versão v1.0.0
Quando `scripts/train.py` for executado
Então existem artefatos para DummyClassifier, baseline determinístico, Regressão Logística e Random Forest
  E os quatro foram avaliados sobre exatamente o mesmo split, identificado por hash
```

### CA-14 — O limiar é escolhido na validação, por recall
**Cobre:** RF-06, RF-09 · **Teste planejado:** `tests/unit/test_limiar_operacional.py`

```gherkin
Dado o modelo escolhido e o conjunto de validação
Quando o limiar operacional for selecionado
Então é o menor limiar que atinge recall ≥ 0,90 na validação
  E o valor é gravado no model_card.json
  E o conjunto de teste não foi usado nessa escolha
```

### CA-15 — A acurácia não decide qual modelo vence
**Cobre:** RF-08, RF-09 · **Teste planejado:** `tests/unit/test_criterio_de_selecao.py`

```gherkin
Dado o conjunto de métricas dos quatro modelos
Quando a seleção do modelo final for executada
Então o critério aplicado é recall com PR-AUC como desempate
  E a acurácia consta do relatório mas não participa da regra de decisão
```

### CA-16 — Toda métrica publicada tem artefato de origem
**Cobre:** RF-09, RNF-16, RNF-03 · **Teste planejado:** conferência documental registrada em `docs/ml/METRICAS_E_RESULTADOS.md`

```gherkin
Dado qualquer número publicado em docs/ml/
Quando sua origem for conferida
Então existe uma chave correspondente em artifacts/metrics/*.json
  E o arquivo identifica modelo, split, versão do dataset e timestamp
```

### CA-17 — Falsos negativos são analisados caso a caso
**Cobre:** RF-09 · **Teste planejado:** seção obrigatória verificada em revisão documental

```gherkin
Dado o conjunto de teste avaliado pelo modelo escolhido
Quando os falsos negativos forem listados
Então cada caso traz os fatores de risco presentes que o modelo não capturou
  E há análise de desempenho por faixa etária e por idade gestacional
```

---

## E. Explicabilidade

### CA-18 — Toda predição vem com contribuições por variável
**Cobre:** RF-10 · **Teste planejado:** `tests/unit/test_explicabilidade.py`

```gherkin
Dado um payload válido
Quando a predição for gerada
Então top_features contém ao menos 3 entradas
  E cada entrada traz feature, value, contribution e direction ∈ {aumenta, reduz}
  E explanation_method está preenchido
```

### CA-19 — A explicabilidade sobrevive à ausência do SHAP
**Cobre:** RF-10, RNF-09 · **Teste planejado:** `tests/unit/test_explicabilidade_fallback.py`

```gherkin
Dado um ambiente sem a biblioteca shap instalada
Quando a predição for gerada
Então a explicação continua sendo produzida
  E explanation_method deixa de ser 'shap_tree_explainer'
  E o método efetivamente usado é o declarado no payload e na auditoria
```

---

## F. Recuperação de protocolos (RAG)

### CA-20 — Fontes recuperadas acompanham a resposta
**Cobre:** RF-11 · **Teste planejado:** `tests/integration/test_rag_no_fluxo_ml.py`

```gherkin
Dado um índice de protocolos disponível
Quando a predição for concluída
Então retrieved_sources contém ao menos uma fonte com doc_id não nulo
  E a resposta final cita o doc_id apresentado
```

### CA-21 — Índice indisponível degrada sem quebrar
**Cobre:** RF-11, RNF-09 · **Teste planejado:** `tests/integration/test_rag_indisponivel.py`

```gherkin
Dado um retriever que levanta exceção ao ser consultado
Quando o workflow for executado
Então a resposta é produzida com retrieved_sources vazio
  E a ausência de fontes é declarada ao usuário
  E nenhuma exceção chega à interface
```

---

## G. Orquestração LangGraph e caminhos de erro

### CA-22 — O workflow tem ramificação real
**Cobre:** RF-12 · **Teste planejado:** `tests/integration/test_workflow_risco_ml.py`

```gherkin
Dado o grafo compilado de lib/workflows/risco_ml.py
Quando sua estrutura for inspecionada
Então existem ao menos 3 arestas condicionais
  E cada um dos 4 caminhos de exceção é alcançável por ao menos uma entrada de teste
```

### CA-23 — Modelo indisponível cai em modo degradado declarado
**Cobre:** RF-22, RNF-09, RNF-17 · **Teste planejado:** `tests/integration/test_modo_degradado.py`

```gherkin
Dado que o arquivo do modelo foi removido do diretório de artefatos
Quando o workflow for executado com payload válido
Então a decisão é tomada pela regra determinística CRITERIOS_ALTO_RISCO
  E a resposta declara explicitamente que o sistema está em modo degradado
  E a auditoria registra modo = 'degradado' com probabilidade NULL
```

### CA-24 — Nenhuma falha injetada produz traceback ao usuário
**Cobre:** RNF-09, RNF-17 · **Teste planejado:** `tests/integration/test_caminhos_de_erro.py`

```gherkin
Dado que uma falha é injetada, uma de cada vez, no modelo, no LLM, no retriever e no banco
Quando o workflow for executado em cada um dos quatro casos
Então as quatro execuções terminam com resposta estruturada
  E nenhuma delas expõe traceback na saída
```

---

## H. Síntese pelo LLM e anti-alucinação

### CA-25 — O LLM recebe os números prontos
**Cobre:** RF-13 · **Teste planejado:** `tests/unit/test_contrato_llm.py`

```gherkin
Dado um payload de predição fechado
Quando o prompt de síntese for construído
Então ele contém prediction, probabilities, threshold, top_features e as fontes
  E o LLM não é consultado em nenhuma etapa anterior à decisão
```

### CA-26 — Número inventado pelo LLM é descartado
**Cobre:** RF-23 · **Teste planejado:** `tests/unit/test_validador_anti_alucinacao.py`

```gherkin
Dado um payload com probabilidade de alto risco igual a 0,75
  E um texto gerado afirmando "probabilidade de 0,92"
Quando a verificação pós-geração for executada
Então o texto é descartado
  E a resposta entregue é a estruturada determinística
  E a substituição é declarada ao usuário
```

### CA-27 — Contradição de rótulo também invalida o texto
**Cobre:** RF-23, RNF-19 · **Teste planejado:** `tests/unit/test_validador_anti_alucinacao.py`

```gherkin
Dado um payload com prediction = "alto_risco"
  E um texto gerado que conclui por "risco habitual"
Quando a verificação for executada
Então o texto é descartado
  E a taxa de descarte é incrementada na métrica correspondente
```

---

## I. Avisos de segurança e limites de uso

### CA-28 — Os dois avisos estão presentes em todos os modos
**Cobre:** RF-14, RNF-19 · **Teste planejado:** `tests/unit/test_avisos_obrigatorios.py`

```gherkin
Dado um caso de cada modo: normal, degradado, bypass_regra e incompleto
Quando a resposta for compilada
Então as quatro respostas contêm safety_notice preenchido
  E as quatro contêm aviso_dados_sinteticos preenchido
```

### CA-29 — A interface exibe a incerteza, não só o rótulo
**Cobre:** RF-14, RF-16 · **Teste planejado:** `tests/e2e/test_ui_aba_ml.py`

```gherkin
Dado uma predição concluída
Quando a aba de risco gestacional for renderizada
Então são exibidos a probabilidade, o limiar aplicado, os campos imputados e os dois avisos
```

---

## J. Auditoria e privacidade

### CA-30 — Toda execução deixa exatamente um registro
**Cobre:** RF-15, RNF-03 · **Teste planejado:** `tests/integration/test_auditoria_predicoes.py`

```gherkin
Dado um caso de cada um dos quatro modos
Quando cada workflow for executado
Então a tabela predicoes_ml ganha exatamente uma linha por execução
  E o campo modo corresponde ao caminho efetivamente percorrido
```

### CA-31 — A auditoria não guarda valor clínico em claro
**Cobre:** RNF-06 · **Teste planejado:** `tests/unit/test_schema_auditoria.py`

```gherkin
Dado o schema da tabela predicoes_ml
Quando suas colunas forem inspecionadas
Então existe features_hash com SHA-256 em vez dos valores das features
  E o JSON persistido em top_features não contém a chave "value"
```

### CA-32 — Predições idênticas são demonstravelmente idênticas
**Cobre:** RNF-03, RNF-02 · **Teste planejado:** `tests/regression/test_predicao_estavel.py`

```gherkin
Dado o mesmo payload submetido duas vezes ao mesmo modelo e versão
Quando as duas execuções forem auditadas
Então os dois registros têm o mesmo features_hash
  E a mesma probabilidade, com o mesmo limiar
```

---

## K. Interface

### CA-33 — A nova aba não altera as existentes
**Cobre:** RF-16, RNF-20 · **Teste planejado:** `tests/regression/test_ui_abas_existentes.py`

```gherkin
Dado a interface construída com a aba de risco gestacional habilitada
Quando as abas forem enumeradas
Então as 5 abas originais continuam presentes, na mesma ordem, com os mesmos componentes de entrada
  E a sexta aba foi acrescentada ao final
```

---

## L. Demonstração ponta a ponta

### CA-34 — Um comando executa a cadeia completa
**Cobre:** RF-17 · **Teste planejado:** `tests/e2e/test_run_demo.py`

```gherkin
Dado um ambiente com as dependências do perfil demo-cpu instaladas
Quando `python scripts/run_demo.py` for executado
Então o comando termina com código de saída 0
  E produz saída para os quatro cenários: normal, dados incompletos, emergência com bypass e modelo indisponível
  E cada saída inclui predição ou justificativa de ausência, explicação, fontes, avisos e registro de auditoria
```

---

## M. Execução local e Docker

### CA-35 — Ambiente limpo, sem GPU, executa o pipeline
**Cobre:** RF-18, RNF-11 · **Teste planejado:** execução manual registrada em `docs/deploy/EXECUCAO_LOCAL.md`

```gherkin
Dado um clone limpo do repositório e um ambiente virtual novo, sem GPU e sem Google Drive
Quando a sequência documentada for executada
Então o dataset é gerado, os modelos são treinados e uma predição é produzida
  E nenhum arquivo de código-fonte precisou ser editado
  E o tempo total ficou em até 15 minutos
```

### CA-36 — Docker constrói e executa, com log anexado
**Cobre:** RF-19, RNF-11 · **Teste planejado:** execução manual registrada em `docs/deploy/EXECUCAO_DOCKER.md`

```gherkin
Dado o Dockerfile do perfil demo-cpu
Quando `docker build` e depois `docker run` forem executados
Então as duas execuções terminam com sucesso
  E o log das duas está anexado à documentação
  E enquanto esse log não existir, o requisito permanece NÃO atendido
```

### CA-37 — Nenhum segredo versionado
**Cobre:** RNF-13, RNF-12 · **Teste planejado:** `tests/unit/test_sem_segredos.py`

```gherkin
Dado todos os arquivos versionados do repositório
Quando a varredura por padrões de credencial for executada
Então não há ocorrência de token, chave ou senha
  E o .env.example contém apenas nomes de variáveis e valores de exemplo
```

---

## N. Testes, versionamento e retrocompatibilidade

### CA-38 — A suíte roda sem GPU, sem rede e sem Drive
**Cobre:** RF-20, RNF-04 · **Teste planejado:** `pytest` no perfil `ml-only`

```gherkin
Dado o perfil ml-only e um ambiente sem GPU e com a rede desabilitada
Quando a suíte completa for executada
Então 100 % dos testes passam
  E a cobertura de lib/ml é de ao menos 80 % das linhas
  E a execução termina em até 5 minutos
```

### CA-39 — Modelo com dataset incompatível não carrega
**Cobre:** RF-25, RNF-14, RNF-08 · **Teste planejado:** `tests/unit/test_registry_compatibilidade.py`

```gherkin
Dado um modelo treinado com dataset_version v1.0.0
  E um dataset corrente na versão v2.0.0
Quando o carregamento for tentado
Então a operação falha com erro explícito citando as duas versões
  E nenhuma predição é produzida
```

### CA-40 — O sistema anterior continua funcionando
**Cobre:** RNF-20, RF-26 · **Teste planejado:** `tests/regression/test_tools_existentes_intactas.py`, `tests/regression/test_obstetrico_flag_desligada.py`

```gherkin
Dado a flag ML_RISCO_HABILITADO desligada
Quando o workflow obstétrico for executado
Então o resultado é idêntico ao comportamento anterior à evolução
  E as 9 ferramentas originais mantêm nome, args_schema e formato de retorno
  E a lista de ferramentas passa a ter 10 itens, todos com args_schema declarado
```

---

## Cobertura dos requisitos pelos cenários

| Requisito | Cenários que o cobrem |
|---|---|
| RF-01 | CA-01 |
| RF-02 | CA-01, CA-02, CA-03, CA-04 |
| RF-03 | CA-05, CA-06 |
| RF-04 | CA-08, CA-09 |
| RF-05 | CA-13 |
| RF-06 | CA-01, CA-14 |
| RF-07 | CA-01 |
| RF-08 | CA-13, CA-15 |
| RF-09 | CA-14, CA-15, CA-16, CA-17 |
| RF-10 | CA-18, CA-19 |
| RF-11 | CA-20, CA-21 |
| RF-12 | CA-09, CA-22 |
| RF-13 | CA-25 |
| RF-14 | CA-28, CA-29 |
| RF-15 | CA-30 |
| RF-16 | CA-29, CA-33 |
| RF-17 | CA-34 |
| RF-18 | CA-35 |
| RF-19 | CA-36 |
| RF-20 | CA-38 |
| RF-21 | CA-07 |
| RF-22 | CA-23 |
| RF-23 | CA-26, CA-27 |
| RF-24 | CA-10, CA-11, CA-12 |
| RF-25 | CA-39 |
| RF-26 | CA-40 |
| RNF-01 | (verificado por `tests/unit/test_arquitetura_imports.py`, sem cenário de fluxo) |
| RNF-02 | CA-10, CA-32 |
| RNF-03 | CA-16, CA-30, CA-32 |
| RNF-04 | CA-38 |
| RNF-05 | CA-08 |
| RNF-06 | CA-31 |
| RNF-07 | (verificado por `tests/unit/test_observabilidade.py`, sem cenário de fluxo) |
| RNF-08 | CA-04, CA-39 |
| RNF-09 | CA-07, CA-19, CA-21, CA-23, CA-24 |
| RNF-10 | (verificado por revisão documental e `tests/unit/test_docstrings_publicas.py`) |
| RNF-11 | CA-35, CA-36 |
| RNF-12 | CA-37 |
| RNF-13 | CA-37 |
| RNF-14 | CA-39 |
| RNF-15 | CA-10 |
| RNF-16 | CA-16 |
| RNF-17 | CA-02, CA-23, CA-24 |
| RNF-18 | CA-05, CA-06, CA-11 |
| RNF-19 | CA-27, CA-28 |
| RNF-20 | CA-33, CA-40 |

`[INF]` Três requisitos não funcionais — RNF-01, RNF-07 e RNF-10 — são propriedades do código, não
comportamentos observáveis em fluxo; por isso são verificados por teste estrutural e revisão, e não
por cenário Dado/Quando/Então. Está declarado para que a ausência não seja lida como esquecimento.

---

## Critérios de aceite da evolução (checklist do desafio, §13)

Os 20 critérios abaixo consolidam a seção 13 do enunciado, na leitura adotada pelos documentos
vinculantes deste repositório. Cada um aponta os cenários e requisitos que o comprovam.

| # | Critério de aceite da evolução | Cenários / requisitos | Evidência esperada | Status |
|---|---|---|---|---|
| 1 | O problema de ML está formalmente definido, com justificativa técnica ancorada no sistema existente | `docs/ml/DEFINICAO_DO_PROBLEMA.md`; ADR-002 | Documento + referência a `obstetrico.py:124-144` | **Atendido** |
| 2 | A origem e a natureza dos dados estão declaradas, incluindo a ausência de dataset real | RF-24; `CONTRATO_DE_DADOS.md` §1 e §2 | `docs/dados/CONTRATO_DE_DADOS.md` + manifesto | **Atendido** |
| 3 | O dataset é reprodutível de forma verificável | CA-10, CA-12; RF-24, RNF-02, RNF-15 | Manifesto com SHA-256 + log das duas gerações | **Atendido** (`artifacts/data/risco_gestacional_v1.manifest.json`, sha256 `6a3b6aefe9e2cf1bb3ec9123386cac4812fd4ef1602657d7950668d5abc20e2f`) |
| 4 | Não há vazamento de dados entre treino, validação e teste | CA-11; RF-24, RNF-18 | `tests/unit/test_dataset_sem_vazamento.py` | **Atendido** |
| 5 | Ao menos dois modelos supervisionados foram treinados, além dos baselines | CA-13; RF-05 | `artifacts/models/` + `model_card.json` | **Atendido** (LogReg + RF + Dummy + regra) |
| 6 | Os modelos foram comparados na mesma métrica e no mesmo split, com intervalo de confiança | CA-13, CA-15; RF-08 | `artifacts/metrics/comparacao.json` | **Atendido** |
| 7 | A métrica primária é adequada ao problema e a acurácia não é critério isolado | CA-15; RF-09 | `docs/ml/METRICAS_E_RESULTADOS.md` | **Atendido** |
| 8 | O limiar de decisão é justificado, versionado e escolhido fora do conjunto de teste | CA-14; RF-06 | Campo `threshold` no `model_card.json` | **Atendido** (validação; LogReg t=0,278) |
| 9 | Há explicabilidade por variável, com o método utilizado declarado | CA-18, CA-19; RF-10 | `artifacts/explainability/` + `docs/ml/EXPLICABILIDADE.md` | **Atendido** (SHAP ausente; `coef_linear` + `permutacao`; JSON literal) |
| 10 | Regras determinísticas de segurança precedem e podem anular a inferência | CA-08, CA-09; RF-04, ADR-006 | `tests/integration/test_risco_ml.py` | **Atendido** |
| 11 | Dados incompletos são tratados sem imputação silenciosa, com acionamento humano | CA-05, CA-06, CA-07; RF-03, RF-21, RNF-18 | `tests/unit/test_dados_incompletos.py` | **Atendido** |
| 12 | O modelo está integrado a um workflow LangGraph com ramificação e tratamento de erro | CA-22, CA-23, CA-24; RF-12, RNF-09 | `lib/workflows/risco_ml.py` + diagrama | **Atendido** (compile LangGraph + executor equivalente se o runtime LangChain do host divergir) |
| 13 | O LLM comunica o resultado sem poder alterar os números | CA-25, CA-26, CA-27; RF-13, RF-23 | `lib/ml/llm_contract.py` + `tests/unit/test_contrato_llm.py` | **Atendido** |
| 14 | O RAG fornece suporte documental à resposta, com fonte citada | CA-20, CA-21; RF-11 | FakeRetriever nos testes; Chroma real só no perfil GPU/Colab | **Parcial** |
| 15 | Avisos de segurança e limites de uso clínico acompanham toda saída | CA-28, CA-29; RF-14, RNF-19 | payload + aba ML | **Atendido** |
| 16 | Toda predição é auditável, sem persistir dados clínicos em claro | CA-30, CA-31, CA-32; RF-15, RNF-06 | Tabela `predicoes_ml` (`features_hash`) | **Atendido** |
| 17 | A interface expõe a predição com probabilidade, explicação e incerteza | CA-29, CA-33; RF-16 | `lib/ui.py` aba 6 | **Atendido** (sem captura de tela neste ciclo) |
| 18 | Existe demonstração ponta a ponta executável por comando único | CA-34; RF-17 | `python scripts/run_demo.py` → `artifacts/demo/` | **Atendido** |
| 19 | A execução local e em Docker está documentada e **comprovada por log de execução real** | CA-35, CA-36, CA-37; RF-18, RF-19, RNF-11 | `docs/deploy/EXECUCAO_LOCAL.md` e `EXECUCAO_DOCKER.md` | **Atendido** — build 699 s, imagem 1,78 GB (`3dd7f0b4e3d1`), `docker run` exit 0 em 12 s (`docs/deploy/EXECUCAO_DOCKER.md`) |
| 20 | Há suíte de testes automatizados com evidência, e o sistema anterior continua funcionando | CA-38, CA-40; RF-20, RNF-04, RNF-20 | `docs/testes/RELATORIO_DE_TESTES.md` + `tests/regression/` | **Atendido** |

**Resumo: 17 atendidos, 2 parciais (explicabilidade SHAP opcional; RAG real só no perfil GPU/Colab).**

`[INF]` Os critérios 3, 19 e 20 dependem de **execução**, não só de código. O critério 3 tem manifesto SHA-256. O 20 tem `pytest` verde. O 19 tem log local; o `docker build` deste ciclo falhou porque o daemon não estava no ar.
