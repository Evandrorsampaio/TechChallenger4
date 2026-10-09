# 01 — Estado Atual do Sistema

**Agente responsável:** `ProjectDiscoveryAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Commit base:** `a8b26cd` (branch `main`)
**Escopo:** descreve **o que o sistema faz hoje**, ponta a ponta, confirmado por leitura de código.
Nada aqui é plano. O plano está em `docs/arquitetura/ARQUITETURA_ALVO.md`.

## Legenda de origem

| Símbolo | Significado |
|---|---|
| `[COD]` | Confirmado por leitura de código (`.py` / `.ipynb`) |
| `[CFG]` | Confirmado por configuração (`.gitignore`, variável de ambiente, célula de setup) |
| `[DOC]` | Afirmado em documentação (`README.md`, relatórios) |
| `[INF]` | Inferido do conjunto de evidências, sem confirmação direta |
| `[AUS]` | Ausente do repositório |
| `[VAL]` | Necessita validação externa (execução ou artefato fora do repositório) |

---

## 1. Resumo em uma frase

`[COD]` O sistema é uma **aplicação de notebook** que carrega um Llama 3.2 3B Instruct fine-tunado
por QLoRA, o expõe como `ChatModel` do LangChain e o usa de duas formas — como **agente ReAct com
9 ferramentas** sobre um SQLite de 50 pacientes sintéticas e um índice Chroma de protocolos, e como
**motor de decisão dentro de 4 workflows LangGraph** de estado tipado — tudo renderizado numa
**UI Gradio de 5 abas**.

`[COD]` Não há camada de configuração, tratamento de erro, teste automatizado, modelo de ML
supervisionado, nem ponto de entrada executável fora do Google Colab.

---

## 2. Pré-requisitos reais de execução

`[COD]` `[CFG]` O sistema **só executa no Google Colab com GPU e Google Drive montado**. Não é uma
escolha de conveniência: é uma dependência estrutural de três pontos.

| Dependência | Evidência | Consequência |
|---|---|---|
| Caminho do banco fixado no Drive | `lib/db.py:12` — `DEFAULT_DB_PATH = '/content/drive/MyDrive/AssistenteHospitalar/files/hospital.db'` | Fora do Colab, `connect()` cria um diretório inexistente e abre um banco vazio, a menos que `HOSPITAL_DB_PATH` seja exportado |
| Caminho do adapter LoRA fixado no Drive | `lib/llm.py:51` — default de `DRIVE_BASE` = `/content/drive/MyDrive/AssistenteHospitalar` | Sem o Drive, `_latest_adapter_dir` devolve `None` e o sistema roda **sem** o fine-tuning, silenciosamente (`lib/llm.py:74` imprime o aviso, mas não falha) |
| GPU obrigatória | `lib/llm.py:55-61` — `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)`, `device_map='auto'` | `bitsandbytes` em 4-bit exige CUDA. Em CPU, o carregamento falha |
| Índice vetorial e banco não versionados | `.gitignore` exclui `files/`, `*.db`, `**/chroma/` `[CFG]` | Clonar o repositório não é suficiente para executar; é preciso regenerar (notebooks 05 e 06) ou ter o Drive do autor |

`[COD]` **Não existe `main.py`, CLI ou serviço.** Os únicos pontos de entrada são notebooks
(`08_app_gradio.ipynb`, `09_demo_workflows.ipynb`), a função `lib.ui.build_ui(agent, conn, workflows)`
— que exige que o chamador já tenha construído LLM, conexão e retriever — e o `__main__` de
`referencias/validador_resposta_llm.py`, que é puro stdlib.

`[COD]` **Não existe `requirements.txt`.** As dependências vivem em células `!pip install -q` dos
notebooks, sem pin de versão exceto no notebook 03.

---

## 3. Interface Gradio — o que cada aba dispara

`[COD]` `lib/ui.py:287-598`, função `build_ui(agent, conn, default_usuario='sessao_demo', workflows=None)`.
Se `workflows` não for passado, as abas de workflow permanecem visíveis mas devolvem
`'⚠️ Workflow não disponível.'` (`lib/ui.py:380, 388, 402, 413`).

### 3.1 Sidebar (comum a todas as abas)

| Controle | Handler | Efeito confirmado |
|---|---|---|
| `Profissional logado` (textbox) | `on_usuario_change` (`ui.py:317`) | Chama `tools_mod.set_usuario_atual()`, que grava a variável de módulo `_USUARIO_ATUAL` usada em toda linha de `log_acesso` (`tools.py:24-39`) |
| `Paciente` (dropdown) | `_lista_pacientes` (`ui.py:28`) + `on_paciente_change` (`ui.py:321`) | Popula opções com `SELECT paciente_id, nome, data_nascimento FROM pacientes`. Ao mudar, renderiza o painel de alertas |
| Painel de alertas | `_alertas_paciente` (`ui.py:39`) | Dispara três leituras: `tools.consultar_prontuario`, `tools.exames_atrasados` (regra determinística) e `SELECT COUNT(*) FROM registros_violencia` |

`[COD]` O painel de alertas exibe a contagem de registros de violência **sem passar pelo caminho
auditado**: a query é feita direto em `ui.py:63-66`, enquanto `tools.consultar_violencia` exige
motivo e grava em `log_acesso`. A contagem não revela conteúdo, mas revela existência.

### 3.2 As 5 abas

| # | Aba | Entrada | O que dispara | Renderizador |
|---|---|---|---|---|
| 1 | 💬 Consulta livre | textbox + histórico | `run_consulta(agent, ...)` → agente ReAct (`agent.py:72-119`) | chat + bloco `<details>` com as tool calls |
| 2 | 🩺 Triagem Ginecológica | queixa (texto livre) | `wf_triagem.invoke({'queixa', 'paciente_id'})` | `_render_triagem` (`ui.py:115`) |
| 3 | 🛡️ Detecção de Violência | **duas sub-abas** (ver abaixo) | workflow LangGraph **ou** matriz determinística | `_render_violencia_wf` (`ui.py:148`) / markdown inline |
| 4 | 🤰 Atendimento Obstétrico | descrição + IG opcional | `wf_obstetrico.invoke({'descricao_caso', 'paciente_id', 'ig_semanas'?})` | `_render_obstetrico` (`ui.py:197`) |
| 5 | 📅 Prevenção e Rastreamento | apenas a paciente da sidebar | `wf_prevencao.invoke({'paciente_id'})` | `_render_prevencao` (`ui.py:241`) |

Detalhes por aba, todos `[COD]`:

- **Aba 1** prefixa a pergunta com `[Contexto: paciente_id=N]` quando há paciente selecionada
  (`agent.py:86-87`), mantém o histórico numa closure (`ui.py:313`, `historico_estado`) e limita a
  execução com `recursion_limit=12` (`agent.py:74, 94`).
- **Aba 3** tem `gr.Tabs()` aninhado. A sub-aba *Workflow completo* inclui o checkbox
  **`Confirmação clínica (autoriza registro SINAN no DB)`** (`ui.py:524-527`) — **este é o único
  gate humano formal do sistema inteiro**; sem ele, o nó `documentar_seguro` não escreve no banco.
  A sub-aba *Checklist heurístico* monta 12 checkboxes a partir de `alertas.SINAIS_VIOLENCIA` e
  chama `tools.avaliar_padrao_violencia` **sem LLM** (`ui.py:357-372`).
- **Aba 4** aceita IG por campo numérico; se vazio, o valor é extraído da descrição pelo LLM.
- **Aba 5** é a única que **exige** paciente selecionada; sem ela devolve texto de instrução.

`[INF]` **Risco de compatibilidade na Aba 1.** `on_chat` devolve histórico no formato
`{'role': ..., 'content': ...}` (`ui.py:345-348`), mas `gr.Chatbot` é instanciado sem
`type='messages'` (`ui.py:470`). Em versões do Gradio cujo default ainda é `tuples`, isso produz
aviso de depreciação ou renderização incorreta. Não foi possível confirmar por execução, porque
não há versão de Gradio pinada em lugar algum `[AUS]`.

---

## 4. O agente ReAct e as 9 ferramentas

`[COD]` `lib/agent.py:65-69` — `build_agent` delega a `langgraph.prebuilt.create_react_agent`,
passando modelo, lista de tools e o `SYSTEM_PROMPT` (`agent.py:25-51`), que instrui linguagem
técnica PT-BR, proíbe a frase "procure um profissional de saúde" (o usuário **é** o profissional) e
prescreve qual tool usar em cada situação.

`[COD]` `lib/tools.py:242-307` — `build_langchain_tools(conn, retriever)` devolve 9
`StructuredTool`, com `conn` e `retriever` capturados em closure:

| # | Tool | `args_schema` | Efeito | Auditoria LGPD |
|---|---|---|---|---|
| 1 | `consultar_prontuario` | `ConsultarProntuarioInput` | leitura (`pacientes` + `prontuario_gineco`) | não |
| 2 | `historico_exames` | `HistoricoExamesInput` | leitura (`exames`) | não |
| 3 | `exames_atrasados` | `ConsultarProntuarioInput` | leitura + regra determinística | não |
| 4 | `consultar_medicamento` | `ConsultarMedicamentoInput` | leitura (`medicamentos`, LIKE) | não |
| 5 | `calendario_menstrual` | `ConsultarProntuarioInput` | leitura + cálculo de média de ciclos | não |
| 6 | `registrar_violencia` | `RegistroViolenciaInput` | **INSERT** em `registros_violencia` | **sim** (`tools.py:168`) |
| 7 | `consultar_violencia` | `ConsultarViolenciaInput` | leitura | **sim**, exige motivo ≥ 5 caracteres (`tools.py:188-190`) |
| 8 | `avaliar_padrao_violencia` | `AvaliarPadraoViolenciaInput` | função pura | não |
| 9 | `buscar_protocolo` | **ausente** (`tools.py:301-306`) | leitura RAG | não |

`[COD]` A tool 9 é a única sem `args_schema` declarado, ficando dependente de inferência de
assinatura pelo LangChain sobre um `lambda`. Em um modelo de 3B, isso é o item mais frágil do tool
calling. `[INF]`

`[COD]` `run_consulta` (`agent.py:72-119`) percorre as mensagens do estado final para reconstruir os
pares chamada/resultado de ferramenta, e devolve `{'resposta', 'tool_calls', 'mensagens'}`.

---

## 5. Os 4 workflows LangGraph, nó a nó

`[COD]` Todos em `lib/workflows/`, todos com estado `TypedDict(total=False)`, todos compilados por
`build_*_workflow(chat_model, conn, retriever)`.

### 5.1 Triagem Ginecológica — `triagem.py` (7 nós, 1 aresta condicional)

| Ordem | Nó | Natureza | O que faz |
|---|---|---|---|
| 1 | `parse_sintomas` | LLM | Extrai lista de sintomas da queixa em JSON (`triagem.py:74-90`) |
| 2 | `analisar_risco` | RAG + LLM | `rag_search(..., categoria='ginecologia_obstetricia', k=3)`, depois pede diferenciais (`triagem.py:93-120`) |
| 3 | `classificar_urgencia` | **Regra → LLM** | Casa a queixa em minúsculas contra `SINAIS_EMERGENCIA` (14 termos, `triagem.py:38-45`). Se houver match, classifica `emergencia` **sem consultar o LLM**; caso contrário, o LLM classifica com default `agendado` (`triagem.py:123-152`) |
| 4 | `sugerir_exames` | RAG + LLM | Nova busca (`k=2`), acumula fontes (`triagem.py:155-175`) |
| 5 | `orientacoes_iniciais` | LLM | Texto livre, até 4 linhas (`triagem.py:178-194`) |
| 6 | `agendamento` | Determinístico | Mapeia urgência → especialidade + prazo; usa `'mama'` nos diferenciais para rotear a Mastologia (`triagem.py:197-217`) |
| 7 | `compilar_resposta` | Determinístico | Monta `resposta_estruturada` + `estimar_confianca(n_fontes, n_decisoes_llm=4, ...)` |

`[COD]` **Aresta condicional:** `_rota_urgencia` (`triagem.py:243-245`) — se `urgencia == 'emergencia'`,
o fluxo **pula** `sugerir_exames` e `orientacoes_iniciais` e vai direto a `agendamento`. É o único
comportamento de desvio real entre os quatro fluxos, junto com o de violência.

### 5.2 Detecção de Violência — `violencia.py` (7 nós, 1 aresta condicional)

| Ordem | Nó | Natureza | O que faz |
|---|---|---|---|
| 1 | `extrair_sinais` | LLM | Mapeia a descrição livre para as 12 chaves canônicas de `alertas.SINAIS_VIOLENCIA`; filtra chaves inválidas (`violencia.py:71-88`) |
| 2 | `avaliar_risco` | **Determinístico** | `alertas.avaliar_padrao_violencia` → score, nível, conduta, encaminhamentos (`violencia.py:91-102`) |
| 3 | `protocolo_seguranca` | Determinístico | Só executa se `nivel == 'alta_suspeita'` (`violencia.py:105-119`) |
| 4 | `acionar_equipe` | Determinístico | Compõe a equipe por nível; acrescenta CAPS/psiquiatria se `ideacao_suicida` (`violencia.py:122-138`) |
| 5 | `documentar_seguro` | Determinístico + escrita | **Só grava** se `nivel == 'alta_suspeita'` **E** `confirmacao_clinica` **E** houver `paciente_id`. Chama `tools.registrar_violencia`, que grava em `log_acesso` antes do INSERT (`violencia.py:141-200`) |
| 6 | `definir_seguimento` | Determinístico | Prazo de retorno por nível (`violencia.py:203-229`) |
| 7 | `compilar_resposta` | Determinístico | `estimar_confianca(n_fontes=0, ...)` — este fluxo **não usa RAG** (`violencia.py:232-253`) |

`[COD]` **Aresta condicional:** `_rota_nivel` (`violencia.py:258-262`).

`[COD]` **Defeito confirmado:** `_protocolo_seguranca` (`violencia.py:105-119`) monta uma lista
`medidas` com 6 condutas de segurança (`violencia.py:107-113`) e **não a inclui no dicionário de
retorno** (`violencia.py:115-119`). Só a flag booleana `protocolo_seguranca_ativado` chega ao estado
e à interface. Perda silenciosa de conteúdo clínico.

### 5.3 Atendimento Obstétrico — `obstetrico.py` (7 nós, **grafo linear**)

| Ordem | Nó | Natureza | O que faz |
|---|---|---|---|
| 1 | `coletar_dados_gestante` | LLM | Extrai IG, paridade, antecedentes, sintomas em JSON (`obstetrico.py:96-121`) |
| 2 | `avaliar_risco_gestacional` | **LLM** | Classifica `habitual` vs `alto_risco` passando `CRITERIOS_ALTO_RISCO` (15 itens) como texto no prompt; **default em caso de falha de parse é `'habitual'`** (`obstetrico.py:124-144`) |
| 3 | `detectar_alertas_urgencia` | Determinístico | Casamento de substrings da descrição contra 10 sinais de `SINAIS_ALARME_OBST` (`obstetrico.py:147-182`) |
| 4 | `orientacoes_especificas` | RAG + LLM | `rag_search(..., categoria='ginecologia_obstetricia', k=3)` + texto em bullets (`obstetrico.py:185-217`) |
| 5 | `agendar_exames` | Determinístico | Rotina de pré-natal por trimestre de IG; acrescenta item genérico se `alto_risco` (`obstetrico.py:219-273`) |
| 6 | `definir_acompanhamento` | Determinístico | Periodicidade: emergência → 0 dias; alto risco → 14/7/3; habitual → 30/15/7 (`obstetrico.py:276-317`) |
| 7 | `compilar_resposta` | Determinístico | `estimar_confianca(..., n_decisoes_llm=2, ...)` |

`[COD]` **Divergência documentação↔código:** o docstring do arquivo (`obstetrico.py:1-27`) desenha
um ramo condicional `emergência? → alerta_emerg`, mas `build_obstetrico_workflow`
(`obstetrico.py:344-366`) monta o grafo **exclusivamente com `add_edge`** — sem
`add_conditional_edges` e sem nó `alerta_emerg`. A emergência é apenas um campo booleano que os nós
seguintes consultam; ela **não altera o caminho de execução**.

`[COD]` Este é o nó identificado como ponto de inserção do ML supervisionado — ver
`docs/ml/DEFINICAO_DO_PROBLEMA.md` §1 e ADR-002.

### 5.4 Prevenção e Rastreamento — `prevencao.py` (6 nós, **grafo linear**)

| Ordem | Nó | Natureza | O que faz |
|---|---|---|---|
| 1 | `carregar_historico` | Leitura | `consultar_prontuario` + `historico_exames`; se faltar `paciente_id`, grava `{'erro': ...}` no perfil e segue (`prevencao.py:61-76`) |
| 2 | `identificar_exames_devidos` | Determinístico | `alertas.exames_atrasados` + projeção de vencimento em ≤ 90 dias para mamografia (50–69a) e papanicolau (25–64a) (`prevencao.py:79-140`) |
| 3 | `orientacoes_preventivas` | RAG + LLM | `rag_search(..., categoria='cancer_mama_colo', k=3)`; se não há exames devidos, devolve texto fixo sem chamar o LLM (`prevencao.py:143-177`) |
| 4 | `agendar_automaticamente` | Determinístico | Data proposta por prioridade (14/45/90 dias) + especialidade por tipo de exame (`prevencao.py:180-210`) |
| 5 | `gerar_lembretes` | LLM + fallback | Pede mensagens ao LLM; se vierem menos que o número de agendamentos, completa com template fixo (`prevencao.py:213-250`) |
| 6 | `compilar_resposta` | Determinístico | `estimar_confianca(..., n_decisoes_llm=2, ...)` |

`[COD]` O grafo é montado apenas com `add_edge` (`prevencao.py:287-293`).

### 5.5 Quadro consolidado

| Workflow | Nós | Aresta condicional | Decisões por LLM | `try/except` | Human-in-the-loop |
|---|---|---|---|---|---|
| `triagem` | 7 | **sim** (`_rota_urgencia`) | 4 | **não** | não |
| `violencia` | 7 | **sim** (`_rota_nivel`) | 1 | **não** | checkbox `confirmacao_clinica` |
| `obstetrico` | 7 | **não** | 3 | **não** | não |
| `prevencao` | 6 | **não** | 2 | **não** | não |

`[COD]` **Nenhum dos quatro workflows tem tratamento de erro.** Não há `try`/`except`, nó de
fallback, retry ou checkpointer em `lib/workflows/`. Qualquer exceção em `chat_model.invoke` ou em
`retriever.invoke` propaga até o handler do Gradio.

---

## 6. O caminho RAG

`[COD]` O RAG é acessado por **dois wrappers equivalentes e duplicados**:

| Função | Arquivo | Usada por |
|---|---|---|
| `rag_search(retriever, query, categoria=None, k=4)` | `lib/workflows/common.py:63-80` | `triagem`, `obstetrico`, `prevencao` |
| `buscar_protocolo(query, retriever, k=4, categoria=None)` | `lib/tools.py:215-237` | tool 9 do agente ReAct |

`[COD]` Ambas seguem o mesmo algoritmo: `retriever.invoke(query)`, fatia `docs[:k*2]`, **filtra
categoria em pós-processamento** (porque nem toda versão do LangChain suporta filtro dinâmico) e
corta em `k`. Devolvem dicionários com `trecho`, `doc_id`, `category`, `chunk_id`.

`[COD]` **O retriever não é construído dentro de `lib/`.** Ele é injetado pelos notebooks (06 indexa,
08 e 09 instanciam) e chega a `build_langchain_tools` e a `build_*_workflow` como parâmetro. Não há,
no pacote, nenhuma referência a ChromaDB, embeddings ou caminho de índice — o acoplamento é apenas
com o contrato `.invoke(query) -> List[Document]`.

`[CFG]` Categorias usadas nas chamadas: `'ginecologia_obstetricia'` e `'cancer_mama_colo'`. Se o
índice não tiver `metadata['category']` com exatamente esses valores, o filtro descarta tudo e o
prompt recebe `'(sem contexto)'` — degradação silenciosa, sem aviso ao usuário. `[INF]`

`[COD]` `common.citar_fontes` (`common.py:83-95`) deduplica por `doc_id`; `ui._render_trace_e_fontes`
(`ui.py:89-112`) renderiza trace e fontes num bloco `<details>` colapsável.

---

## 7. Carregamento do LLM

`[COD]` `lib/llm.py`:

1. `load_finetuned(adapter_dir=None, base_model_id='meta-llama/Llama-3.2-3B-Instruct', use_4bit=True)`
   — se `adapter_dir` for `None`, resolve `DRIVE_BASE` (default Colab, `llm.py:51`) e procura a run
   mais recente em `files/finetune/` pelo glob `llama32-3b-saude-mulher_*`, exigindo o
   subdiretório `adapter_final` (`llm.py:24-32`).
2. Quantização 4-bit NF4 com `bnb_4bit_compute_dtype=torch.bfloat16` e double quant (`llm.py:55-61`).
3. `AutoTokenizer` com `pad_token = eos_token` quando ausente (`llm.py:63-65`).
4. Se houver adapter, aplica `PeftModel.from_pretrained`; **senão, segue com o modelo base e apenas
   imprime um aviso** (`llm.py:69-74`). Não há exceção, flag de estado, nem indicação na UI de que
   o fine-tuning não foi carregado. `[COD]`
5. `build_chat_model` embrulha em `pipeline('text-generation')` → `HuggingFacePipeline` →
   `ChatHuggingFace` (`llm.py:112-134`), que é o objeto com `bind_tools` consumido pelo agente e
   pelos workflows.

`[COD]` Os defaults de geração — `max_new_tokens=256`, `repetition_penalty=1.2`,
`no_repeat_ngram_size=4`, `do_sample=False` — estão documentados **no próprio código** como
mitigação de defeitos observados na avaliação da run `0217`: loops degenerativos e verbosidade
(`llm.py:84-89`). A mitigação está no código; a medição que a motivou não está no repositório
(ver §9).

---

## 8. As regras determinísticas que já existem

`[COD]` O sistema já opera com uma camada determinística relevante, o que importa porque a
arquitetura alvo (ADR-006) determina que a regra **precede e pode anular** o ML.

| Regra | Onde | Critério |
|---|---|---|
| Papanicolau em atraso | `alertas.py:46-68` | 25–64 anos; atraso se nunca realizado ou > 3,5 anos; prioridade `alta` se > 5 anos |
| Mamografia em atraso | `alertas.py:71-93` | 50–69 anos; atraso se nunca realizada ou > 2,5 anos; prioridade `alta` se > 4 anos |
| Matriz de violência | `alertas.py:126-170` | 12 sinais; peso 2 para `lesoes_inexplicadas`, `lesoes_multiplas_fases`, `ideacao_suicida`; score ≥ 4 → `alta_suspeita`, ≥ 2 → `atencao` |
| Próximo ciclo menstrual | `alertas.py:173-195` | Média dos últimos 6 intervalos; exige ≥ 2 ciclos registrados |
| Sinais de emergência na triagem | `triagem.py:38-45, 125-136` | 14 termos; match literal em minúsculas **antes** de consultar o LLM |
| Sinais de alarme obstétrico | `obstetrico.py:36-47, 147-182` | 10 sinais por substring; `contracoes_regulares` só alarma se IG < 37 |
| Rotina de exames por IG | `obstetrico.py:219-273` | 1º/2º/3º trimestre + rastreio de EGB a partir de 35 semanas |
| Periodicidade de consultas | `obstetrico.py:276-317` | 0 / 14-7-3 / 30-15-7 dias conforme emergência, alto risco e IG |
| Agendamento preventivo | `prevencao.py:180-210` | 14 / 45 / 90 dias conforme prioridade |

`[COD]` **Data congelada replicada em quatro pontos, um deles divergente:**

| Local | Valor |
|---|---|
| `lib/alertas.py:16` | `date(2026, 5, 22)` |
| `lib/mock_data.py:20` | `date(2026, 5, 22)` |
| `lib/tools.py:100` | `date(2026, 5, 22)` — literal inline, sem constante nomeada |
| `lib/workflows/prevencao.py:34` | **`date(2026, 5, 23)`** — um dia à frente |

O congelamento torna o comportamento determinístico e testável, o que é desejável. A **replicação
com divergência** não: `prevencao.py` calcula vencimentos e datas propostas contra uma data
diferente da usada por `alertas.exames_atrasados`, que é exatamente a função de onde ele consome os
atrasos.

---

## 9. Estado de execução dos notebooks e os números do README

`[COD]` Verificado por inspeção de `execution_count` e `outputs` no JSON dos 10 notebooks.

| Notebook | Executado | Outputs com resultados reais salvos |
|---|---|---|
| 01 `extrair_protocolos` | parcial | **sim** — inventário de PDFs, "Protocolos processados: 39" |
| 02 `gerar_dataset_sft` | parcial (`execution_count` 34–47) | **não** — todos `outputs: []` |
| 03 `treinar_qlora` | não | não |
| 04 `avaliar_modelo` | não | **não** — nenhuma métrica ROUGE persistida |
| 05, 06, 07, 10 | não | não |
| 08, 09 | não | apenas erro de kernel local (`ipykernel` ausente) |

### 9.1 Afirmações apenas documentais

`[DOC]` O `README.md` reporta os seguintes números:

| Número | Onde no README | Status de evidência |
|---|---|---|
| 6414 pares Q&A sintéticos | linha 5 | `[VAL]` |
| 5134 exemplos SFT (`sft_train.jsonl`) | linhas 73, 172 | `[VAL]` |
| 1392 chunks indexados no Chroma | linhas 6, 65, 176, 197 | `[VAL]` |
| ROUGE-L 0,101 → 0,095 (−5,9 %) | linha 246 | `[VAL]` |
| ~60 % das respostas do modelo FT com loops repetitivos | linha 247 | `[VAL]` |
| Respostas 18,6 % mais longas que o modelo base | linha 249 | `[VAL]` |

`[COD]` **Nenhum desses números tem evidência dentro do repositório.** As saídas dos notebooks 02 e
04 foram limpas, e os artefatos que os sustentariam (`sft_train.jsonl`, `eval_report.json`,
`files/chroma/`) são excluídos pelo `.gitignore` `[CFG]`.

> **Isto não significa que os números sejam falsos.** Significa que são **não verificáveis a partir
> do repositório**: dependem de artefatos que vivem no Google Drive do autor. Qualquer documento da
> nova fase que os reutilize deve marcá-los como *"resultado da Fase 3, evidência externa ao
> repositório, pendente de validação"* — nunca como métrica obtida nesta fase.

`[VAL]` Validação externa possível: reexecutar os notebooks 02, 04 e 06 no Colab com o Drive do
autor e anexar as saídas, ou anexar `eval_report.json` e o manifesto do índice Chroma como
evidência. Enquanto isso não ocorrer, o status permanece **Pendente**.

---

## 10. O que o sistema **não** faz hoje

`[AUS]` Consolidado aqui apenas para fechar a fotografia; o detalhamento com severidade e requisito
bloqueado está em `docs/03_LACUNAS_E_RISCOS.md`.

- Nenhum modelo de Machine Learning supervisionado. Busca por `sklearn`, `train_test_split`,
  `RandomForest`, `LogisticRegression`, `XGBoost`, `GridSearchCV` em `*.py` e `*.ipynb` retorna zero
  ocorrências.
- Nenhum dataset tabular rotulado. `hospital.db` não tem variável alvo, sinal vital, resultado
  laboratorial numérico nem comorbidade estruturada (`lib/db.py:31-103`).
- Nenhuma explicabilidade de modelo (SHAP, importância de variáveis, contribuição por feature).
- Nenhum teste automatizado, `Dockerfile`, `requirements.txt`, `scripts/` ou `pyproject.toml`.
- Nenhuma camada de configuração (`lib/config.py`), `.env.example` ou logging estruturado.
- Nenhuma auditoria de predição — `log_acesso` cobre apenas acesso a `registros_violencia`.
- Nenhuma integração do validador anti-alucinação: `referencias/validador_resposta_llm.py:217-242`
  mantém `_esboco_integracao_NAO_USE`, que levanta `NotImplementedError` deliberadamente.

---

## 11. Próximo documento

`docs/02_MAPA_DE_COMPONENTES.md` — inventário módulo a módulo de `lib/`, com responsabilidades,
funções públicas, acoplamento e grafo de dependências.
