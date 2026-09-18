# Avaliação da Recuperação (RAG)

**Agente responsável:** `RAGAgent`
**Status:** Plano de avaliação + **TEMPLATE VAZIO**
**Vinculado a:** `ESTRATEGIA_RAG.md` · `METADADOS_DAS_FONTES.md`

---

> ## ⚠️ BANNER OBRIGATÓRIO
>
> **Nenhuma avaliação de recuperação foi executada neste projeto — nem nesta fase, nem na anterior.**
>
> Não existe conjunto de avaliação, não existe script de avaliação, não existe recall@k medido.
> Todas as células de resultado deste documento contêm `—` e **só podem ser preenchidas** pela
> saída de `scripts/avaliar_rag.py`, gravada em `artifacts/metrics/rag_eval.json`.
>
> O único teste de recuperação que existe no repositório é o *smoke test* da célula 5 do
> `06_indexar_protocolos.ipynb`: cinco consultas cujo resultado é **impresso para leitura humana**,
> sem gabarito e sem métrica. Ele prova que o índice responde; não mede se responde bem. E o
> notebook está sem outputs salvos (`00_INVENTARIO_PROJETO.md` §11), então nem isso está
> evidenciado no repositório.

---

## 1. O que será medido, e por quê

A camada de RAG é a única fonte de suporte documental do sistema. A `POLITICA_DE_CITACAO.md`
determina que nenhuma conduta clínica seja emitida sem lastro em protocolo recuperado. Segue que
**a qualidade da recuperação é o teto da qualidade clínica da resposta**: se o chunk certo não é
recuperado, nenhum prompt, nenhuma verificação e nenhum modelo de linguagem consertam isso.

Mede-se, portanto, uma pergunta só, em quatro formas: *dada uma pergunta clínica, o documento que a
responde aparece entre os `k` primeiros?*

### 1.1 Hipóteses específicas a testar

A avaliação não é genérica. Ela existe para testar três achados de `ESTRATEGIA_RAG.md` §9:

| ID | Hipótese | Métrica que a decide |
|---|---|---|
| **H-1** | O filtro por categoria em pós-processamento devolve menos de `k` resultados com frequência não desprezível, e zero em parte dos casos | Distribuição do número de resultados devolvidos, com e sem filtro |
| **H-2** | A janela de 512 tokens do encoder degrada a recuperação de conteúdo que está no fim do chunk | Recall@k comparando consultas ancoradas no início vs. no fim do chunk-alvo |
| **H-3** | Categorias raras têm hit rate pior que categorias dominantes | Hit rate por categoria |

Uma avaliação que não testasse hipótese nenhuma produziria um número bonito e inútil. Estas três
têm consequência direta: H-1 decide a prioridade de R-01, H-2 decide se o rechunking sai do
"fora de escopo", H-3 decide se as categorias sensíveis precisam de tratamento especial.

---

## 2. Métricas

| Métrica | Definição | Interpretação neste contexto | Valor de `k` |
|---|---|---|---|
| **Recall@k** | Fração das consultas em que ao menos um documento relevante aparece nos `k` primeiros | Métrica primária. É a que decide se a conduta terá lastro | 1, 3, 4, 10 |
| **Precision@k** | Fração dos `k` devolvidos que são relevantes | Secundária. Com `[:2500]` no prompt, ruído no 3º lugar custa pouco — mas no 1º custa muito | 1, 3, 4 |
| **MRR** | Média de `1/posição do primeiro relevante` | Captura o que precision@k não captura: **estar em primeiro importa**, porque o truncamento faz o 1º chunk dominar o prompt (`ESTRATEGIA_RAG.md` §2.1) | — |
| **Hit rate por categoria** | Recall@4 estratificado por `category` do documento esperado | Decide H-3 e a política das categorias sensíveis | 4 |
| **Taxa de retorno vazio** | Fração das consultas com filtro que devolvem `[]` | Decide H-1. **Não é métrica de IR padrão; é métrica deste defeito** | 4 |
| **Cardinalidade devolvida** | Distribuição de `len(resultado)` sob filtro | Complementa H-1: quantifica "menos de k" | 4 |

### 2.1 Por que MRR e não nDCG

nDCG exigiria relevância graduada (muito relevante / parcialmente relevante / irrelevante), o que
exigiria julgamento clínico que não temos competência para fazer em escala. MRR opera sobre
relevância binária, que é o que o gabarito de §3 consegue sustentar honestamente.

### 2.2 Por que `k=1` e `k=10` também, se o sistema usa `k=4`

`k=1` mede o que efetivamente chega ao prompt hoje, dado o truncamento. `k=10` mede se o documento
certo está "por perto" — a diferença entre recall@4 e recall@10 separa dois problemas distintos:
*o encoder não encontra o documento* (ambos baixos) versus *o encoder encontra mas ranqueia mal*
(recall@10 alto, recall@4 baixo). As correções são diferentes.

---

## 3. Conjunto de avaliação

### 3.1 Forma

```jsonl
{"id": "Q-001",
 "pergunta": "Quais critérios para repetir citologia em paciente com LSIL?",
 "categoria_esperada": "cancer_mama_colo",
 "doc_ids_relevantes": ["inca_diretrizes_colo_2016.pdf"],
 "chunk_ids_relevantes": ["inca_diretrizes_colo_2016.pdf::7"],
 "origem": "smoke_test_nb06",
 "posicao_no_chunk": "inicio",
 "usada_em": ["H-1", "H-2"]}
```

| Campo | Papel |
|---|---|
| `doc_ids_relevantes` | Gabarito no nível de documento. É o nível em que o recall é reportado |
| `chunk_ids_relevantes` | Gabarito no nível de chunk, quando identificável. Permite medir MRR mais fino |
| `posicao_no_chunk` | `inicio` \| `meio` \| `fim`. **Campo desenhado para H-2** |
| `origem` | Rastreia de onde a pergunta veio; ver §3.2 |

### 3.2 Como o conjunto será construído

Quatro fontes, em ordem decrescente de confiabilidade e crescente de volume:

| # | Fonte | Quantas | Confiabilidade do gabarito | Observação |
|---|---|---|---|---|
| 1 | As 5 consultas do smoke test do notebook 06 | 5 | Alta — foram escritas por quem conhece o corpus | Ponto de partida; cobrem 4 das 5 categorias |
| 2 | As 8 consultas já embutidas nos workflows (`triagem.py:96,159`, `obstetrico.py:192`, `prevencao.py:155`) e as consultas montadas por `_montar_consulta` (`ESTRATEGIA_RAG.md` §6.1) | ~8 | Alta | **São as consultas que o sistema realmente faz.** Avaliar outra coisa mediria outro sistema |
| 3 | Perguntas derivadas dos títulos de seção dos 39 PDFs | ~40 | Média | Gabarito por construção: a pergunta vem do documento, logo o documento é relevante |
| 4 | Perguntas geradas a partir de chunks sorteados, com `posicao_no_chunk` controlada | ~30 | Média | **Desenhadas especificamente para H-2**: metade ancorada nos primeiros 1500 caracteres do chunk, metade nos últimos 1500 |

**Alvo: 60 a 80 consultas**, com no mínimo 8 por categoria, para que o hit rate por categoria tenha
algum sentido. Com 5 categorias e 60 consultas, o intervalo de confiança por categoria ainda será
largo, e isso será reportado, não escondido.

### 3.3 Limitação declarada do gabarito

A fonte 3 tem um viés que precisa estar registrado: uma pergunta derivada do título de uma seção
usa o vocabulário exato do documento. Isso **superestima** o recall, porque a busca semântica tem
sobreposição lexical máxima. As fontes 1 e 2 não têm esse viés — são perguntas em linguagem de
consulta clínica real.

Consequência metodológica: **as métricas serão reportadas separadamente por origem**, e a leitura
principal será a das fontes 1 e 2, que refletem o uso real. Um recall@4 global alto puxado pela
fonte 3 seria autoengano.

### 3.4 Bloqueio atual

O conjunto **não pode ser construído hoje**. `fontes_saude_mulher_v2.json` e `files/chroma/` não
estão no repositório (`00_INVENTARIO_PROJETO.md` §5), e sem eles não há `doc_id` real, não há
títulos de seção e não há chunk para sortear. Construir o conjunto exige, primeiro, resolver a
melhoria R-06 de `ESTRATEGIA_RAG.md` (reindexação local reprodutível).

Isso é uma dependência dura e está registrada como tal. O plano existe; a execução está bloqueada.

---

## 4. Protocolo de execução

| Item | Definição |
|---|---|
| Script | `scripts/avaliar_rag.py` *(não existe)* |
| Entrada | `tests/fixtures/rag_eval_set.jsonl` *(não existe)* |
| Saída | `artifacts/metrics/rag_eval.json` + preenchimento deste documento |
| Retriever | O mesmo `vectorstore.as_retriever(search_kwargs={'k': K})`, com `K` variável por corrida |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2`, normalizado — idêntico à indexação |
| Determinismo | Busca vetorial é determinística para índice fixo. Duas corridas devem dar resultado idêntico; o script verifica isso |
| Perfil | `demo-cpu` — não precisa de GPU |

### 4.1 Braços da comparação

Cada consulta é executada em quatro configurações, para isolar o efeito de cada mecanismo:

| Braço | Filtro de categoria | `k` do retriever | Pós-processamento |
|---|---|---|---|
| **A — baseline atual** | pós-processado | 4 | `rag_search` como está |
| **B — sem filtro** | nenhum | 4 | `rag_search` sem `categoria` |
| **C — filtro nativo (R-01)** | no Chroma | 4 | nenhum |
| **D — teto de recall** | nenhum | 10 | nenhum |

A comparação A × C decide H-1 quantitativamente. A comparação A × D separa "não encontra" de
"ranqueia mal". A comparação B × C mede quanto o filtro custa ou ganha.

---

## 5. Templates de resultado — **VAZIOS**

> Preencher exclusivamente a partir de `artifacts/metrics/rag_eval.json`. Nenhuma célula pode ser
> estimada, inferida ou preenchida por analogia.

### 5.1 Caracterização do conjunto de avaliação

| Item | Valor |
|---|---|
| Consultas totais | — |
| Consultas da origem 1 (smoke test) | — |
| Consultas da origem 2 (workflows) | — |
| Consultas da origem 3 (títulos) | — |
| Consultas da origem 4 (posição no chunk) | — |
| Categorias cobertas | — |
| Consultas por categoria (mín / máx) | — / — |
| Chunks indexados no momento da avaliação | — |
| Documentos indexados | — |
| Data da execução | — |
| Commit | — |

### 5.2 Métricas globais por braço

| Métrica | A — baseline | B — sem filtro | C — filtro nativo | D — k=10 |
|---|---|---|---|---|
| Recall@1 | — | — | — | — |
| Recall@3 | — | — | — | — |
| Recall@4 | — | — | — | — |
| Recall@10 | — | — | — | — |
| Precision@1 | — | — | — | — |
| Precision@3 | — | — | — | — |
| Precision@4 | — | — | — | — |
| MRR | — | — | — | — |
| Taxa de retorno vazio | — | — | — | — |
| Média de resultados devolvidos | — | — | — | — |

### 5.3 Métricas por origem da consulta (controle do viés de §3.3)

| Origem | n | Recall@4 (A) | Recall@4 (C) | MRR (A) |
|---|---|---|---|---|
| 1 — smoke test | — | — | — | — |
| 2 — consultas dos workflows | — | — | — | — |
| 3 — títulos de seção | — | — | — | — |
| 4 — posição no chunk | — | — | — | — |

### 5.4 Hit rate por categoria (hipótese H-3)

| Categoria | `sensitive` | n de consultas | Chunks no índice | Hit rate @4 (A) | Hit rate @4 (C) | Retorno vazio (A) |
|---|---|---|---|---|---|---|
| `ginecologia_obstetricia` | não | — | — | — | — | — |
| `cancer_mama_colo` | não | — | — | — | — | — |
| `planejamento_familiar` | não | — | — | — | — | — |
| `violencia_domestica` | **sim** | — | — | — | — | — |
| `saude_mental` | **sim** | — | — | — | — | — |

### 5.5 Cardinalidade devolvida sob filtro (hipótese H-1)

| Resultados devolvidos | Braço A (ocorrências) | % |
|---|---|---|
| 0 | — | — |
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |
| 4 | — | — |

**Conclusão sobre H-1:** —

### 5.6 Efeito da posição no chunk (hipótese H-2)

| `posicao_no_chunk` | n | Recall@4 | MRR |
|---|---|---|---|
| `inicio` | — | — | — |
| `meio` | — | — | — |
| `fim` | — | — | — |

**Conclusão sobre H-2:** —

> Se o recall de `fim` for substancialmente menor que o de `inicio`, a hipótese de truncamento do
> encoder está confirmada e o rechunking deixa de ser melhoria opcional para virar correção de
> defeito. Essa é a decisão que este subquadro existe para tomar.

### 5.7 Análise de erros

Preencher com as consultas de pior desempenho, uma linha por caso investigado.

| ID da consulta | Recall@4 | Documento esperado | Documentos devolvidos | Diagnóstico |
|---|---|---|---|---|
| — | — | — | — | — |

### 5.8 Conclusões e decisões

| Hipótese | Confirmada? | Decisão decorrente |
|---|---|---|
| H-1 — filtro pós-processado degrada | — | — |
| H-2 — janela de 512 tokens degrada | — | — |
| H-3 — categorias raras têm hit rate pior | — | — |

---

## 6. O que esta avaliação não mede

Limites declarados:

| Não medido | Por quê |
|---|---|
| Se o trecho recuperado **responde** à pergunta | Exigiria julgamento clínico por especialista. O gabarito é de *documento relevante*, não de *resposta contida* |
| Se a resposta final do sistema está correta | É avaliação de geração, não de recuperação. Ver `CASOS_DE_TESTE_LLM.md` |
| Qualidade dos 39 PDFs como fonte | Não avaliamos a atualidade nem a autoridade dos protocolos. Ver `METADADOS_DAS_FONTES.md` §6 |
| Desempenho com corpus maior | 39 documentos é um corpus pequeno; nada aqui extrapola para escala |
| Latência da recuperação | Fora de escopo desta avaliação; ver `ESTRATEGIA_DE_ESCALABILIDADE.md` |

---

## 7. Critérios de aceite do componente de avaliação

| ID | Critério | Evidência |
|---|---|---|
| RAG-AC-01 | Conjunto de avaliação existe, versionado, com ≥ 60 consultas e ≥ 8 por categoria | `tests/fixtures/rag_eval_set.jsonl` no git |
| RAG-AC-02 | Script executa e grava JSON | `artifacts/metrics/rag_eval.json` |
| RAG-AC-03 | Os quatro braços são executados sobre o mesmo conjunto e o mesmo índice | Campo `indice_hash` idêntico nos quatro |
| RAG-AC-04 | As três hipóteses recebem conclusão explícita, inclusive "não confirmada" | §5.8 preenchida |
| RAG-AC-05 | Métricas reportadas por origem, não só globalmente | §5.3 preenchida |
| RAG-AC-06 | Nenhum número neste documento sem origem em `rag_eval.json` | Revisão manual antes da entrega |

---

## 8. Estado atual

| Item | Estado |
|---|---|
| Conjunto de avaliação | **Não existe** |
| `scripts/avaliar_rag.py` | **Não existe** |
| `artifacts/metrics/rag_eval.json` | **Não existe** |
| Índice Chroma acessível localmente | **Não** — bloqueio de §3.4 |
| Alguma métrica de recuperação medida em qualquer fase | **Nenhuma** |
