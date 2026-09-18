# 00 — Inventário do Projeto

**Agente responsável:** `ProjectDiscoveryAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Data do levantamento:** 2026-09-18
**Commit base:** `a8b26cd` (branch `main`)

## Legenda de origem da informação

Toda afirmação neste documento é classificada por origem:

| Símbolo | Classificação | Significado |
|---|---|---|
| `[COD]` | Confirmada por código | Lida diretamente no fonte `.py` / `.ipynb` |
| `[CFG]` | Confirmada por configuração | Lida em `.gitignore`, env vars, células de setup |
| `[DOC]` | Confirmada por documentação | Afirmada em `README.md` / `ARQUITETURA.md` / relatórios |
| `[INF]` | Inferida | Deduzida do conjunto de evidências, sem confirmação direta |
| `[AUS]` | Ausente | Mencionada em documentação mas **não existe** no repositório |
| `[VAL]` | Necessita validação | Depende de execução ou de artefato externo ao repositório |

> **Aviso metodológico:** a documentação existente descreve artefatos (`hospital.db`, `files/chroma/`,
> `sft_train.jsonl`, adapter LoRA) que **não estão versionados** no repositório — eles vivem no Google
> Drive do autor. Neste inventário, esses itens são marcados `[AUS]` no repositório e `[VAL]` quanto
> à sua existência real.

---

## 1. Árvore completa de arquivos versionados

```
TechChallenger4/
├── .gitignore                                  [COD]
├── README.md                                   [COD]
├── ARQUITETURA.md                              [COD]
├── RELATORIO_TECNICO.md                        [COD]
├── RELATORIO_TECNICO_DETALHADO.md              [COD]
├── ROTEIRO_VIDEO.md                            [COD]
│
├── 01_extrair_protocolos.ipynb                 [COD]
├── 02_gerar_dataset_sft.ipynb                  [COD]
├── 03_treinar_qlora.ipynb                      [COD]
├── 04_avaliar_modelo.ipynb                     [COD]
├── 05_gerar_dados_mock.ipynb                   [COD]
├── 06_indexar_protocolos.ipynb                 [COD]
├── 07_testar_tools_alertas.ipynb               [COD]
├── 08_app_gradio.ipynb                         [COD]
├── 09_demo_workflows.ipynb                     [COD]
├── 10_relatorio_utilizacao.ipynb               [COD]
│
├── lib/
│   ├── __init__.py                             [COD]
│   ├── db.py                                   [COD]  SQLite: 7 tabelas + bootstrap
│   ├── mock_data.py                            [COD]  Faker pt_BR, 50 pacientes, seed=42
│   ├── alertas.py                              [COD]  Regras determinísticas (exames, violência)
│   ├── tools.py                                [COD]  9 StructuredTools LangChain
│   ├── llm.py                                  [COD]  load_finetuned + build_chat_model
│   ├── agent.py                                [COD]  create_react_agent + SYSTEM_PROMPT
│   ├── ui.py                                   [COD]  Gradio Blocks, 5 tabs
│   ├── workflows/
│   │   ├── __init__.py                         [COD]
│   │   ├── common.py                           [COD]  llm_json, llm_text, rag_search, estimar_confianca
│   │   ├── triagem.py                          [COD]  StateGraph, 7 nodes, 1 edge condicional
│   │   ├── violencia.py                        [COD]  StateGraph, matriz SINAN
│   │   ├── obstetrico.py                       [COD]  StateGraph, 7 nodes
│   │   └── prevencao.py                        [COD]  StateGraph, 6 nodes
│   └── templates/                              [COD]  6 templates clínicos .md + README
│
└── referencias/
    └── validador_resposta_llm.py               [COD]  Validador regex + validador LLM (NÃO integrado)
```

**Total versionado:** 6 documentos Markdown na raiz, 10 notebooks, 14 módulos Python, 7 templates clínicos.

**Nenhum dos seguintes existe no repositório:** `requirements.txt`, `Dockerfile`, `.dockerignore`,
`docker-compose.yml`, `pyproject.toml`, `setup.py`, `tests/`, `scripts/`, `artifacts/`, `.env.example`,
CI/CD (`.github/workflows/`), `Makefile`. Todos `[AUS]`.

---

## 2. Tecnologias identificadas

| Camada | Tecnologia | Versão declarada | Origem | Onde |
|---|---|---|---|---|
| LLM base | `meta-llama/Llama-3.2-3B-Instruct` | — | `[COD]` | `lib/llm.py:22` |
| LLM gerador de dataset | `meta-llama/Llama-3.1-8B-Instruct` | — | `[COD]` | `02_gerar_dataset_sft.ipynb` |
| Fine-tuning | QLoRA (4-bit NF4 + bfloat16) | `bitsandbytes>=0.45.0` | `[CFG]` | `03_treinar_qlora.ipynb` |
| Treino | TRL `SFTTrainer` + PEFT | `trl>=0.12,<0.14`, `peft>=0.13,<0.15` | `[CFG]` | `03_treinar_qlora.ipynb` |
| Transformers | HuggingFace | `>=4.46,<4.50` | `[CFG]` | `03_treinar_qlora.ipynb` |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` | 384d, normalizado | `[COD]` | `06_indexar_protocolos.ipynb` |
| Vector store | ChromaDB (persistente) | não pinada | `[CFG]` | `06_indexar_protocolos.ipynb` |
| Orquestração | LangChain + LangGraph | não pinada | `[CFG]` | `08`, `09` |
| Base estruturada | SQLite (stdlib) | — | `[COD]` | `lib/db.py` |
| Dados sintéticos | Faker `pt_BR` | não pinada | `[COD]` | `lib/mock_data.py` |
| Validação de schema | Pydantic | não pinada | `[COD]` | `lib/tools.py:13` |
| UI | Gradio Blocks | não pinada; código usa formato `messages` do Gradio 5/6 | `[COD]` | `lib/ui.py:345` |
| Relatórios | pandas + matplotlib | não pinada | `[CFG]` | `10_relatorio_utilizacao.ipynb` |
| PDF | PyMuPDF + pikepdf | não pinada | `[CFG]` | `01_extrair_protocolos.ipynb` |
| Avaliação de texto | `rouge_score` | não pinada | `[CFG]` | `04_avaliar_modelo.ipynb` |
| Runtime alvo | Google Colab Pro (A100/L4) | — | `[DOC]` | `README.md` |

### Machine Learning supervisionado tradicional

**`[AUS]` — Não existe.** Busca exaustiva por `sklearn`, `scikit-learn`, `train_test_split`,
`RandomForest`, `LogisticRegression`, `XGBoost`, `GridSearchCV`, `cross_val`, `fit_transform`
em todo o repositório (`*.py`, `*.ipynb`) retornou **zero ocorrências**. Esta é a lacuna central
que a nova fase precisa preencher.

---

## 3. Pontos de entrada

| # | Ponto de entrada | Tipo | Executável localmente? | Origem |
|---|---|---|---|---|
| 1 | `08_app_gradio.ipynb` | Notebook → app Gradio | **Não** — exige Colab + Drive + GPU | `[COD]` |
| 2 | `09_demo_workflows.ipynb` | Notebook → demo dos 4 workflows | **Não** — mesma dependência | `[COD]` |
| 3 | `lib.ui.build_ui(agent, conn, workflows)` | Função → `gr.Blocks` | Sim, se as dependências forem injetadas | `[COD]` |
| 4 | `10_relatorio_utilizacao.ipynb` | Notebook → relatório gerencial | **Sim** — tem branch não-Colab via `HOSPITAL_DB_PATH` | `[COD]` |
| 5 | `referencias/validador_resposta_llm.py` | `__main__` com 6 asserts | **Sim** — puro stdlib + regex | `[COD]` |

**Não existe CLI, nem `main.py`, nem entrypoint de serviço.** `[AUS]`

---

## 4. Modelos identificados

| Modelo | Tipo | Local | Status |
|---|---|---|---|
| Llama 3.2 3B Instruct | LLM base | HuggingFace Hub (gated) | `[VAL]` — exige `HF_TOKEN` com aprovação Meta |
| Adapter LoRA `llama32-3b-saude-mulher_20260524_0217` | Adapter PEFT | Google Drive | `[AUS]` no repo / `[VAL]` externamente |
| `paraphrase-multilingual-MiniLM-L12-v2` | Embedding | HuggingFace Hub (aberto) | `[VAL]` — baixado em runtime |
| **Modelo de ML supervisionado** | — | — | **`[AUS]`** |

Nota: `.gitignore` exclui `**/adapter_final/`, `**/finetune/`, `*.safetensors`, `*.bin` — a exclusão
do adapter é deliberada `[CFG]`.

---

## 5. Datasets identificados

| Dataset | Formato | Conteúdo | Versionado? | Adequado a ML supervisionado tabular? |
|---|---|---|---|---|
| `fontes_saude_mulher_v2.json` | JSON | 39 PDFs de protocolos extraídos | Não (`files/` ignorado) `[CFG]` | Não — texto bruto |
| `sft_train/val/test.jsonl` | JSONL | `{messages:[system,user,assistant], category, sensitive, source_doc}` | Não (`*.jsonl` ignorado) `[CFG]` | **Não** — pares de chat; `category`/`sensitive` são metadados, não features |
| `hospital.db` | SQLite | 50 pacientes sintéticos, 7 tabelas | Não (`*.db` ignorado) `[CFG]` | **Não** — sem variável alvo, n=50, sem sinais vitais/laboratório |
| `files/chroma/` | Chroma | ~1392 chunks `[DOC]` | Não (`**/chroma/` ignorado) `[CFG]` | Não — índice vetorial |

### Conclusão crítica sobre dados

**`[COD]` Não existe nenhum dataset tabular rotulado no projeto.** O schema de `hospital.db`
(`lib/db.py:31-103`) contém apenas dados cadastrais, prontuário ginecológico descritivo, exames com
resultado em texto livre, ciclos menstruais, registros de violência e bula de medicamentos.
**Não há:** sinais vitais, pressão arterial, IMC, resultados laboratoriais numéricos, comorbidades
estruturadas, desfechos clínicos, nem qualquer coluna que sirva como variável alvo.

Consequência: o `DataEngineeringAgent` precisará **declarar a ausência e propor um dataset sintético
controlado**, conforme previsto na seção 5.4 do prompt mestre. Ver `docs/dados/CONTRATO_DE_DADOS.md`.

---

## 6. Workflows LangGraph

Todos `[COD]`, confirmados por leitura de `lib/workflows/`.

| Workflow | Arquivo | Nodes | Estado tipado | Edge condicional | Decisões por LLM | Decisões determinísticas |
|---|---|---|---|---|---|---|
| Triagem Ginecológica | `triagem.py` | 7 | `TriagemState` (TypedDict) | 1 (`_rota_urgencia`) | 4 | agendamento, matching de `SINAIS_EMERGENCIA` |
| Detecção de Violência | `violencia.py` | 7 | `ViolenciaState` | sim | extração de sinais | matriz de pontuação `alertas.avaliar_padrao_violencia` |
| Obstétrico | `obstetrico.py` | 7 | `ObstetricoState` | **nenhum** (grafo linear, apesar do docstring desenhar um) | 3 | alarmes por keyword, agenda de exames por IG, periodicidade |
| Prevenção | `prevencao.py` | 6 | `PrevencaoState` | **nenhum** (grafo linear — `prevencao.py:287-293` usa só `add_edge`) | orientações | `alertas.exames_atrasados` |

Apenas **dois** dos quatro workflows têm aresta condicional: `triagem.py` (`_rota_urgencia`) e
`violencia.py:284-286` (`_rota_nivel`). `[COD]`

### Achados relevantes para a nova fase

1. **`obstetrico.py:344-366`** — o docstring no topo do arquivo desenha um ramo condicional
   (`emergência? → alerta_emerg`), mas `build_obstetrico_workflow` monta um grafo **estritamente
   linear** com `add_edge`. Divergência entre documentação inline e código. `[COD]`
2. **`obstetrico.py:124-144` (`_avaliar_risco_gestacional`)** — a classificação `habitual` vs
   `alto_risco` é feita **pelo LLM**, passando `CRITERIOS_ALTO_RISCO` como texto no prompt.
   **Este é o ponto de inserção natural para um modelo de ML supervisionado.** `[COD]`
3. **`triagem.py:123-152` (`_classificar_urgencia`)** — regra determinística primeiro
   (`SINAIS_EMERGENCIA`), LLM como fallback. Bom padrão, já existente, a ser replicado pelo ML.
4. **Nenhum workflow tem tratamento de erro explícito** (`try/except`, nó de fallback, retry).
   Falha de `chat_model.invoke` propaga para o Gradio. `[COD]`
5. **Nenhum workflow tem human-in-the-loop formal** (`interrupt`, checkpointer). O único gate
   humano é o checkbox `confirmacao_clinica` no fluxo de violência. `[COD]`
6. **Defeito em `violencia.py:105-119` (`_protocolo_seguranca`)** — o nó monta uma lista `medidas`
   com 6 itens de conduta e **não a inclui no dicionário de retorno**. As medidas de segurança
   nunca chegam ao estado nem à interface; apenas a flag booleana
   `protocolo_seguranca_ativado` é propagada. Perda silenciosa de conteúdo clínico. `[COD]`
7. **`lib/agent.py:54` declara `max_iterations: int = 6` e nunca o utiliza.** O limite efetivo é
   `recursion_limit=12`, aplicado em `run_consulta` (`agent.py:74`). Parâmetro morto que sugere um
   controle inexistente. `[COD]`

---

## 7. Ferramentas LangChain

`[COD]` — `lib/tools.py:242-307`, `build_langchain_tools(conn, retriever)` devolve **9**
`StructuredTool`:

| # | Tool | `args_schema` | Efeito colateral | Audita LGPD |
|---|---|---|---|---|
| 1 | `consultar_prontuario` | `ConsultarProntuarioInput` | leitura | não |
| 2 | `historico_exames` | `HistoricoExamesInput` | leitura | não |
| 3 | `exames_atrasados` | `ConsultarProntuarioInput` | leitura + regra | não |
| 4 | `consultar_medicamento` | `ConsultarMedicamentoInput` | leitura | não |
| 5 | `calendario_menstrual` | `ConsultarProntuarioInput` | leitura + cálculo | não |
| 6 | `registrar_violencia` | `RegistroViolenciaInput` | **INSERT** | **sim** |
| 7 | `consultar_violencia` | `ConsultarViolenciaInput` | leitura | **sim** (motivo ≥5 chars) |
| 8 | `avaliar_padrao_violencia` | `AvaliarPadraoViolenciaInput` | puro | não |
| 9 | `buscar_protocolo` | **nenhum** (`args_schema` omitido) | leitura RAG | não |

**Achado:** a tool 9 é a única sem `args_schema` (`tools.py:301-306`), o que a deixa dependente de
inferência de assinatura pelo LangChain. Risco de instabilidade de tool calling num modelo 3B. `[COD]`

### 7.1 Achado crítico no RAG — descompasso entre tamanho de chunk e janela do encoder

`[COD]` `06_indexar_protocolos.ipynb` define `CHUNK_SIZE, CHUNK_OVERLAP = 6000, 400` (em
**caracteres**) e indexa com `paraphrase-multilingual-MiniLM-L12-v2` sem sobrescrever
`max_seq_length`.

Esse modelo é distribuído com `max_seq_length` de **128 tokens** na configuração
sentence-transformers. Em português, 128 tokens correspondem grosseiramente a 500–700 caracteres.
Ou seja: **o vetor de cada chunk representa aproximadamente os primeiros 10 % do texto do chunk;
os outros 90 % são truncados antes da codificação e ficam praticamente irrecuperáveis por busca
semântica.** O texto completo continua sendo devolvido no `page_content` — o que mascara o
problema, porque o trecho recuperado parece correto, mas a *escolha* daquele trecho foi feita
olhando apenas o começo dele.

Este é provavelmente o fator isolado mais relevante para a qualidade do RAG no projeto e não estava
documentado em lugar nenhum. Classificação: `[COD]` quanto ao descompasso.

**T-03 (2026-09-18):** `sentence_bert_config.json` oficial do Hub
(`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) declara `"max_seq_length": 128`.
Carga local `SentenceTransformer(..., local_files_only=True)` falhou com `OSError` (pesos
`pytorch_model.bin` / `model.safetensors` ausentes neste ambiente). **Sem rechunking.** O valor
operacional permanece 128 tokens; a divergência com a menção a 512 tokens em `ESTRATEGIA_RAG.md` §3.1
é documentação da Fase 3, não medição.

Dois efeitos colaterais relacionados, também `[COD]`:

- **`k*2` é ilusório.** `common.rag_search` faz `docs[:k * 2]` para "pegar mais e filtrar por
  categoria", mas o retriever é construído com `search_kwargs={'k': 4}` fixo — a lista tem 4
  elementos e o fatiamento em 8 não traz nada a mais. O filtro por categoria em pós-processamento
  pode portanto devolver **zero** resultados mesmo havendo protocolo indexado na categoria.
- **Truncamento em `[:2500]`.** Os workflows concatenam os trechos e cortam em 2500 caracteres
  antes de enviar ao LLM. Com chunks de 6000 caracteres, o corte cai dentro do primeiro trecho —
  mas `citar_fontes` lista as quatro fontes como "consultadas". O sistema cita fontes que o LLM
  não leu.

---

## 8. Regras determinísticas (`lib/alertas.py`)

`[COD]`

| Regra | Função | Critério |
|---|---|---|
| Papanicolau em atraso | `exames_atrasados` | 25–64a; atraso se >3,5 anos desde o último, ou nunca realizado |
| Mamografia em atraso | `exames_atrasados` | 50–69a; atraso se >2,5 anos, ou nunca realizada |
| Padrão de violência | `avaliar_padrao_violencia` | 12 sinais; pesos 2 para `lesoes_inexplicadas`, `lesoes_multiplas_fases`, `ideacao_suicida`; score ≥4 = `alta_suspeita`, ≥2 = `atencao` |
| Próximo ciclo menstrual | `proximo_periodo_menstrual` | média dos últimos 6 intervalos; exige ≥2 ciclos |

**Achado — data congelada replicada e divergente.** A constante "hoje" aparece em **quatro** lugares,
e um deles **diverge**: `[COD]`

| Local | Valor |
|---|---|
| `lib/alertas.py:16` | `date(2026, 5, 22)` |
| `lib/mock_data.py:20` | `date(2026, 5, 22)` |
| `lib/tools.py:100` | `date(2026, 5, 22)` — inline, sem constante nomeada |
| `lib/workflows/prevencao.py:34` | **`date(2026, 5, 23)`** — um dia à frente |

O congelamento em si é defensável (torna o comportamento determinístico e testável), mas a
replicação em quatro pontos com um valor divergente é um defeito: `prevencao.py` calcula
vencimento de exames e datas propostas de agendamento (`linhas 107, 125, 185-191`) contra uma data
diferente da usada por `alertas.exames_atrasados`, que é a função da qual ele consome os atrasos.

---

## 9. Dependências

**`[AUS]` — não existe `requirements.txt`.** O conjunto abaixo foi reconstruído a partir das células
`!pip install` dos 10 notebooks `[CFG]`:

| Pacote | Restrição declarada | Notebooks |
|---|---|---|
| `transformers` | `>=4.46,<4.50` (só em 03) | 02, 03, 04, 08, 09 |
| `peft` | `>=0.13,<0.15` (só em 03) | 02, 03, 04, 08, 09 |
| `trl` | `>=0.12,<0.14` | 03 |
| `accelerate` | `>=1.1,<2.0` | 02, 03, 04, 08, 09 |
| `bitsandbytes` | `>=0.45.0` | 02, 03, 04, 08, 09 |
| `triton` | `>=3.0` | 03 |
| `datasets` | — | 03, 04 |
| `langchain`, `langchain-community`, `langchain-huggingface` | — | 06, 07, 08, 09 |
| `langgraph` | — | 08, 09 |
| `chromadb`, `sentence-transformers` | — | 06, 07, 08, 09 |
| `gradio` | — | 08 |
| `faker` | — | 05, 07 |
| `pydantic` | — | 07 |
| `pandas`, `matplotlib` | — | 10 |
| `pymupdf`, `pikepdf` | — | 01 |
| `rouge_score` | — | 04 |
| `python-dotenv` | — | 02, 03, 04, 08, 09 |
| `torch` | implícito | — |

Apenas o notebook 03 usa versões pinadas. Todos os demais usam `pip install -q` sem restrição —
**reprodutibilidade não garantida** `[COD]`.

---

## 10. Variáveis de ambiente

`[CFG]` — todas descobertas por leitura de código.

| Variável | Usada em | Default | Obrigatória |
|---|---|---|---|
| `HF_TOKEN` | 02, 03, 04, 08, 09 (via `.env` no Drive) | nenhum | Sim, para o LLM |
| `HOSPITAL_DB_PATH` | `lib/db.py:16`, notebooks 05–10 | `/content/drive/MyDrive/AssistenteHospitalar/files/hospital.db` | Não (mas o default só funciona no Colab) |
| `DRIVE_BASE` | `lib/llm.py:56`, notebooks 08, 09 | `/content/drive/MyDrive/AssistenteHospitalar` | Não |

**`[AUS]`** — não existe `.env.example`. Não existe camada de configuração central
(`lib/config.py`); os defaults Colab estão espalhados por `db.py`, `llm.py` e células de notebook.

---

## 11. Estado de execução dos notebooks

`[COD]` — verificado por inspeção de `execution_count` e `outputs` no JSON dos notebooks.

| Notebook | Executado | Outputs salvos com resultados reais |
|---|---|---|
| 01 | parcial | **sim** — inventário de PDFs, "Protocolos processados: 39" |
| 02 | parcial (`execution_count` 34–47) | **não** — todos `outputs: []` |
| 03 | não | não |
| 04 | não | **não** — nenhuma métrica ROUGE persistida no repositório |
| 05, 06, 07, 10 | não | não |
| 08, 09 | não | apenas erro de kernel local (`ipykernel` ausente) |

### Consequência para rastreabilidade

Os números citados no `README.md` — **6414 pares Q&A, 5134 exemplos SFT, 1392 chunks,
ROUGE-L 0.101→0.095 (−5,9%), ~60% de respostas com loop, +18,6% de comprimento** — **não têm
evidência dentro do repositório**. São `[DOC]` sem respaldo `[COD]`, porque as saídas dos
notebooks foram limpas e `eval_report.json` é gitignored.

Isso **não significa que sejam falsos** — significa que são `[VAL]`: dependem de artefatos no Drive
do autor. Qualquer relatório da nova fase que reutilizar esses números deve marcá-los como
"resultado da Fase 3, evidência externa ao repositório".

---

## 12. Artefatos ausentes (consolidado)

| Artefato | Status | Impacto na nova fase |
|---|---|---|
| `requirements.txt` | `[AUS]` | **Bloqueante** para Docker e execução local |
| `Dockerfile`, `.dockerignore` | `[AUS]` | **Bloqueante** — requisito explícito |
| `tests/` (qualquer teste automatizado) | `[AUS]` | **Bloqueante** — requisito explícito |
| `scripts/` (train, evaluate, predict, demo) | `[AUS]` | **Bloqueante** — requisito explícito |
| Dataset tabular rotulado | `[AUS]` | **Bloqueante** para ML supervisionado |
| Qualquer código scikit-learn | `[AUS]` | **Bloqueante** — núcleo da nova fase |
| Explicabilidade (SHAP / feature importance) | `[AUS]` | **Bloqueante** — requisito explícito |
| `artifacts/models`, `artifacts/metrics` | `[AUS]` | Necessário para versionamento |
| Camada de configuração (`lib/config.py`) | `[AUS]` | Necessário para sair do Colab |
| `.env.example` | `[AUS]` | Necessário para onboarding |
| Persistência de auditoria de predições | `[AUS]` | `log_acesso` só cobre violência |
| Integração do `ValidadorDeterministico` | `[AUS]` | Existe em `referencias/`, deliberadamente **não integrado** (`_esboco_integracao_NAO_USE`, `validador_resposta_llm.py:218-242`) |
| CI/CD | `[AUS]` | Desejável, não obrigatório |
| `hospital.db`, `files/chroma/`, adapter LoRA | `[AUS]` no repo, `[VAL]` no Drive | Precisam ser regeneráveis localmente |

---

## 13. Ambiente local verificado

`[COD]` — executado em 2026-09-18 na máquina do desenvolvedor.

| Item | Valor |
|---|---|
| SO | Windows 10.0.26200 |
| Shell | PowerShell |
| Python | 3.13.13 (e `py` 3.13.7) |
| Docker | 29.3.1 |
| Git | repositório em `main`, limpo |

**Implicação:** há Docker e Python locais, então o requisito "Dockerfile testado de verdade" é
executável nesta máquina — **desde que a imagem não exija GPU/CUDA**. Ver
`docs/arquitetura/DECISOES_ARQUITETURAIS.md` (ADR-005).

---

## 14. Próximo documento

`docs/01_ESTADO_ATUAL.md` — descrição funcional do que o sistema faz hoje, ponta a ponta.
