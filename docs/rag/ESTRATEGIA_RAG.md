# Estratégia de RAG

**Agente responsável:** `RAGAgent`
**Status:** Descrição do que **existe** (marcado `[COD]`) + especificação do que será **acrescentado**
(marcado `[PROJ]`). Nada do que está marcado `[PROJ]` foi implementado.
**Fontes de verdade lidas:** `06_indexar_protocolos.ipynb` · `lib/workflows/common.py:63-96` ·
`lib/tools.py:215-237` · `lib/agent.py` SYSTEM_PROMPT

---

> ### Banner de estado
> Os artefatos do RAG (`files/chroma/`, `fontes_saude_mulher_v2.json`) **não estão no repositório**
> — são gitignored e vivem no Google Drive do autor (`00_INVENTARIO_PROJETO.md` §5). As contagens
> "1392 chunks" e "39 PDFs" são afirmações de documentação (`[DOC]`), não verificadas por execução
> nesta fase. Nenhuma métrica de recuperação foi medida; ver `AVALIACAO_RECUPERACAO.md`.

---

## 1. O corpus

| Atributo | Valor | Origem |
|---|---|---|
| Documentos fonte | 39 PDFs de protocolos de saúde da mulher | `[DOC]` `01_extrair_protocolos.ipynb`, saída "Protocolos processados: 39" |
| Intermediário | `files/fontes_saude_mulher_v2.json` — lista de `{filename, content, category, sensitive, name}` | `[COD]` `06_indexar_protocolos.ipynb` célula 3 |
| Chunks indexados | ~1392 | `[DOC]` README; **não verificado nesta fase** |
| Categorias | 5 | `[COD]` metadados |

### 1.1 As cinco categorias

| `category` | `sensitive` | Conteúdo |
|---|---|---|
| `ginecologia_obstetricia` | `false` | Pré-natal, emergências obstétricas, condutas ginecológicas |
| `cancer_mama_colo` | `false` | Rastreamento e conduta em câncer de mama e colo uterino |
| `planejamento_familiar` | `false` | Contracepção, planejamento reprodutivo |
| `violencia_domestica` | **`true`** | Acolhimento, notificação, profilaxias pós-violência sexual |
| `saude_mental` | **`true`** | Saúde mental na gestação e puerpério, ideação suicida |

A flag `sensitive` é gravada por chunk e é o que conecta o RAG à regra 3 do
`ValidadorDeterministico`: resposta ancorada em categoria sensível **precisa** citar serviço da
rede (`POLITICA_ANTI_ALUCINACAO.md` §6, `POLITICA_DE_CITACAO.md` §6).

---

## 2. Chunking `[COD]`

Implementado em `06_indexar_protocolos.ipynb`, célula 3. Parâmetros:

| Parâmetro | Valor |
|---|---|
| `CHUNK_SIZE` | 6000 caracteres |
| `CHUNK_OVERLAP` | 400 caracteres |
| Corte preferencial | quebra de parágrafo (`\n\n`) |
| Janela de busca do corte | do início do chunk até `size`, aceitando o corte se cair além de `size // 2` |
| Normalização prévia | `re.sub(r'\n{3,}', '\n\n', text)` |
| Descarte | chunks com ≤ 200 caracteres |

```python
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind('\n\n', start, end)
            if cut > start + size // 2:
                end = cut
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if len(c) > 200]
```

### 2.1 Leitura crítica dos parâmetros

**6000 caracteres é um chunk grande** — aproximadamente 1200–1500 tokens em português. Isso tem
duas consequências opostas e ambas reais:

| Efeito | Sinal |
|---|---|
| Um chunk costuma conter um fluxo clínico inteiro (critério + conduta + dose), em vez de um fragmento | Positivo: reduz o risco de o LLM ver o critério sem a conduta |
| A granularidade da recuperação é grossa: `k=4` traz ~24 000 caracteres, dos quais o prompt usa 2500 | Negativo: a maior parte do que é recuperado é descartada pelo truncamento |

O segundo efeito é o mais importante e está subdocumentado no projeto. Os workflows truncam o
contexto concatenado em `[:2500]` (`triagem.py:106`, `obstetrico.py:196`, `prevencao.py:158`).
Com chunks de 6000 caracteres, **o truncamento corta dentro do primeiro chunk**: o segundo, o
terceiro e o quarto resultados da busca praticamente nunca chegam ao prompt.

Na prática, hoje, `k=4` é `k≈1` no que o modelo efetivamente lê. O `citar_fontes` cita os quatro,
mas o LLM viu um. Isso é uma inconsistência entre o que a citação afirma e o que fundamentou a
resposta, e está registrado como melhoria prioritária em §8.

**O overlap de 400 (6,7 % do chunk)** é modesto. Com corte preferencial em parágrafo, a perda de
contexto na fronteira é pequena, então é uma escolha defensável.

**O corte em `size // 2`** impede que um parágrafo muito próximo do início produza chunk minúsculo.
Boa salvaguarda, herdada de `02_gerar_dataset_sft.ipynb`.

---

## 3. Embeddings `[COD]`

| Atributo | Valor |
|---|---|
| Modelo | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Dimensão | 384 |
| Normalização | `encode_kwargs={'normalize_embeddings': True}` |
| Dispositivo na indexação | `cuda` (notebook 06); `cpu` viável |
| Licença | aberto, sem token |

Vetores normalizados + Chroma com distância padrão implicam que a ordenação é equivalente a
similaridade de cosseno — o que importa para qualquer interpretação de score na avaliação.

### 3.1 Limitação: janela de 512 tokens contra chunk de 6000 caracteres

`paraphrase-multilingual-MiniLM-L12-v2` tem comprimento máximo de sequência de **512 tokens**. Um
chunk de 6000 caracteres em português tem ~1200–1500 tokens.

**Consequência:** o `sentence-transformers` trunca a entrada. O embedding de cada chunk representa
aproximadamente o **primeiro terço** do seu texto. Os outros dois terços estão armazenados e serão
devolvidos como `page_content`, mas **não influenciaram o vetor** que decide se o chunk é
recuperado.

Isto é um achado de leitura de código, não uma suposição: `CHUNK_SIZE = 6000` está na célula 2 do
notebook 06, e o limite de 512 tokens é propriedade do modelo declarado na mesma célula.

Implicações concretas:

1. Uma conduta que aparece no final de um chunk é **praticamente irrecuperável** por busca
   semântica sobre seu próprio conteúdo. Ela só chega ao prompt se o início do chunk casar com a
   consulta.
2. O `recall@k` real é menor do que a estrutura do corpus sugeriria.
3. Chunks menores (1000–1500 caracteres) alinhariam chunk e janela do encoder, mas exigiriam
   reindexação completa e mudariam a contagem de 1392 — ver §8.

Esta limitação **não estava documentada** em nenhum arquivo do repositório antes deste. Ela é,
provavelmente, o fator isolado mais relevante para a qualidade da recuperação.

---

## 4. Vector store e retriever `[COD]`

| Atributo | Valor |
|---|---|
| Store | Chroma persistente |
| Collection | `protocolos_saude_mulher` |
| Persist dir | `{DRIVE_BASE}/files/chroma` |
| Construção | `Chroma.from_documents(...)` no notebook 06 |
| Retriever | `vectorstore.as_retriever(search_kwargs={'k': 4})` |
| Metadados por chunk | `doc_id`, `chunk_id`, `category`, `sensitive`, `name` |

Detalhamento do esquema de metadados em `METADADOS_DAS_FONTES.md`.

---

## 5. Recuperação: `common.rag_search` `[COD]`

```python
def rag_search(retriever, query, categoria=None, k=4) -> list[dict]:
    docs = retriever.invoke(query)
    out = []
    for d in docs[:k * 2]:
        meta = d.metadata or {}
        if categoria and meta.get('category') != categoria:
            continue
        out.append({'trecho': d.page_content,
                    'doc_id': meta.get('doc_id', '?'),
                    'category': meta.get('category', '?'),
                    'chunk_id': meta.get('chunk_id', '?')})
        if len(out) >= k:
            break
    return out
```

Contrato completo em `CONTRATOS_DE_COMPONENTES.md` §6.

### 5.1 A falha do filtro por categoria em pós-processamento

Esta é a fraqueza mais concreta do RAG atual e merece ser nomeada sem eufemismo.

**O que acontece.** O retriever é construído uma vez, com `search_kwargs={'k': 4}` fixo. Ele
devolve **4 documentos**. `rag_search` então fatia `docs[:k*2]` — que, com `k=4`, é `docs[:8]`,
mas a lista tem 4 elementos. O fatiamento não traz nada a mais: **`k*2` é ilusório**. Em seguida,
filtra por categoria e devolve até `k` itens.

Portanto, quando `categoria` é passada, o resultado é: *"dos 4 vizinhos mais próximos globais,
quantos por acaso pertencem à categoria pedida?"*

**Consequências, em ordem de gravidade:**

| # | Consequência | Quando ocorre |
|---|---|---|
| 1 | Devolve **menos de `k`** resultados | Sempre que menos de `k` dos 4 vizinhos globais são da categoria |
| 2 | Devolve **zero** resultados, com protocolo relevante existindo no índice | Quando nenhum dos 4 vizinhos é da categoria |
| 3 | O parâmetro `k` de `rag_search` é **inoperante para aumentar** | O retriever já fixou 4; pedir `k=6` não traz 6 |
| 4 | A intenção de "pegar mais e filtrar" **não se realiza** | `docs[:k*2]` sobre uma lista de 4 |

A consequência 2 é a grave: **o sistema dirá "os protocolos disponíveis não cobrem este cenário"
quando eles cobrem** — só não estavam entre os 4 vizinhos globais. Isso é um falso negativo de
recuperação que se apresenta ao usuário como ausência de cobertura documental.

O efeito é pior justamente nas categorias **raras**. As duas sensíveis (`violencia_domestica`,
`saude_mental`) são plausivelmente as menores do corpus; consultas com filtro nessas categorias
são as mais propensas a devolver vazio.

**Onde isso já morde hoje:**

| Chamada | Categoria | Risco |
|---|---|---|
| `triagem.py:96` | `ginecologia_obstetricia`, `k=3` | Baixo — categoria dominante |
| `obstetrico.py:190-194` | `ginecologia_obstetricia`, `k=3` | Baixo |
| `prevencao.py:153-157` | `cancer_mama_colo`, `k=3` | **Médio** — categoria menor; vazio é plausível |
| `triagem.py:158-160` | sem filtro, `k=2` | Nenhum — sem filtro não há descarte |

**A correção `[PROJ]`.** Chroma suporta filtro nativo por metadado:

```python
retriever.invoke(query, filter={'category': categoria})
# ou, na construção:
vectorstore.as_retriever(search_kwargs={'k': k, 'filter': {'category': categoria}})
```

Filtrar no store garante `k` resultados **dentro** da categoria, em vez de `k` globais dos quais
alguns sobram. O comentário em `tools.py:220-222` justifica o pós-processamento por
"o retriever em si não suporta filtro dinâmico em todas as versões do langchain" — razão legítima
quando foi escrita, e verificável hoje: a correção deve **detectar** o suporte e cair no
comportamento atual quando ausente, preservando a ADR-001.

Escopo: ver §8, item R-01.

### 5.2 `citar_fontes` dedupa por `doc_id` `[COD]`

```python
unicas: dict[str, dict] = {}
for f in fontes:
    key = f.get('doc_id', '?')
    if key not in unicas:
        unicas[key] = f
```

Quatro chunks do mesmo PDF viram **uma** linha de citação. Correto para não poluir a resposta, mas
com um efeito colateral: o `chunk_id` do primeiro chunk é o que sobrevive, e os demais se perdem —
a rastreabilidade cai de chunk para documento. Ver `METADADOS_DAS_FONTES.md` §5.

### 5.3 Divergência entre `rag_search` e `buscar_protocolo` `[COD]`

Duas implementações quase idênticas, com três diferenças:

| | `common.rag_search` | `tools.buscar_protocolo` |
|---|---|---|
| Default de metadado ausente | `'?'` | `None` |
| Ordem dos parâmetros | `(retriever, query, categoria, k)` | `(query, retriever, k, categoria)` |
| Usada por | workflows | tool do agente ReAct |

Um consumidor que aceite as duas origens precisa tolerar `None` **e** `'?'`
(`CONTRATOS_DE_COMPONENTES.md` §6). Já registrado; o novo workflow consome apenas `rag_search`.

### 5.4 `buscar_protocolo` é a única tool sem `args_schema` `[COD]`

`lib/tools.py:301-306`. As outras oito passam `args_schema=...`; esta não. O LangChain infere a
assinatura do lambda `lambda query, categoria=None: ...`, sem descrição de campo e sem tipagem
declarada.

Num modelo de 3B, isso é risco concreto de tool calling instável: o modelo precisa adivinhar que
`categoria` aceita exatamente uma das cinco strings. Sem `args_schema`, nada informa quais são.

**Correção `[PROJ]`, aditiva e de baixo risco:**

```python
class BuscarProtocoloInput(BaseModel):
    query: str = Field(..., description='Pergunta clínica em linguagem natural')
    categoria: Literal['ginecologia_obstetricia', 'cancer_mama_colo',
                       'planejamento_familiar', 'violencia_domestica',
                       'saude_mental'] | None = Field(
        None, description='Restringe a busca a uma categoria de protocolo')
```

Escopo: §8, item R-02.

---

## 6. Integração do RAG no workflow de ML `[PROJ]`

O nó `recuperar_protocolos_rag` de `lib/workflows/risco_ml.py` executa **depois** da predição e da
explicabilidade, e **antes** da síntese (`ARQUITETURA_ALVO.md` §4). A ordem importa: a consulta é
construída a partir do resultado do modelo.

### 6.1 Construção da consulta

A consulta não é a descrição livre do caso. Ela é montada a partir de dois insumos estruturados:

1. **o rótulo predito** (`prediction`), que define o tipo de conduta buscada;
2. **as features de maior contribuição** (`top_features`), traduzidas para vocabulário clínico por
   um dicionário fixo — não por LLM.

```python
# lib/workflows/risco_ml.py  — PROJETADO

TERMO_CLINICO = {
    'has_cronica':           'hipertensão arterial crônica na gestação',
    'diabetes_previo':       'diabetes mellitus prévio na gestação',
    'pre_eclampsia_previa':  'pré-eclâmpsia prévia recorrência profilaxia',
    'gemelaridade':          'gestação gemelar conduta pré-natal',
    'cardiopatia':           'cardiopatia materna gestação',
    'nefropatia':            'doença renal crônica gestação',
    'tev_previo':            'tromboembolismo prévio tromboprofilaxia gestação',
    'idade':                 'idade materna avançada pré-natal',
    'imc_pre_gestacional':   'obesidade na gestação conduta',
    'pas_mmhg':              'hipertensão na gestação conduta',
    'pad_mmhg':              'hipertensão na gestação conduta',
    'hemoglobina_g_dl':      'anemia na gestação conduta',
    'glicemia_jejum_mg_dl':  'diabetes gestacional rastreamento conduta',
    'proteinuria_fita':      'proteinúria pré-eclâmpsia critério diagnóstico',
    'infeccao_sexual_ativa': 'sífilis HIV hepatite na gestação conduta',
    'tabagismo':             'tabagismo na gestação orientação',
    # features sem termo mapeado não entram na consulta
}

def _montar_consulta(predicao, top_features, n=3) -> str:
    base = ('pré-natal de alto risco conduta acompanhamento'
            if predicao == 'alto_risco'
            else 'pré-natal de risco habitual rotina acompanhamento')
    termos = [TERMO_CLINICO[f['feature']]
              for f in top_features[:n]
              if f['feature'] in TERMO_CLINICO]
    return ' '.join([base, *termos])
```

**Por que o dicionário é fixo e não gerado por LLM.** Uma tradução gerada seria não-determinística
e variaria entre execuções, tornando a recuperação irreprodutível e a avaliação de §
`AVALIACAO_RECUPERACAO.md` sem sentido. O custo é manutenção manual de 16 entradas; o ganho é que
a mesma predição sempre busca os mesmos protocolos.

**Features sem termo mapeado são omitidas**, não traduzidas por fallback genérico. Melhor uma
consulta mais curta do que uma consulta poluída por `escolaridade_anos`.

### 6.2 Categoria e o problema do filtro

A consulta natural seria filtrar por `ginecologia_obstetricia`. Dado §5.1, isso pode devolver
menos de `k` ou zero. A política do nó novo:

| Passo | Ação |
|---|---|
| 1 | Busca **com** filtro `ginecologia_obstetricia` |
| 2 | Se devolver 0 resultados: repete **sem** filtro e marca `fontes_sem_filtro=True` no estado |
| 3 | Se ainda devolver 0: `retrieved_sources = []`, e a resposta declara a ausência de cobertura |
| 4 | Se `fontes_sem_filtro`, a citação registra a categoria real de cada fonte, que pode não ser obstétrica |

O passo 2 é uma degradação **declarada**, não silenciosa. Sem ele, a falha de §5.1 se converteria
em "protocolos não cobrem este cenário" para casos cobertos.

### 6.3 Falha do RAG não derruba a predição

Exigência de `CONTRATOS_DE_COMPONENTES.md` §6:

```python
def _recuperar_protocolos_rag(retriever):
    def node(state):
        try:
            fontes = common.rag_search(retriever, _montar_consulta(...),
                                       categoria='ginecologia_obstetricia', k=4)
            if not fontes:
                fontes = common.rag_search(retriever, _montar_consulta(...), k=4)
                sem_filtro = bool(fontes)
            else:
                sem_filtro = False
            falha = None
        except Exception as e:
            fontes, sem_filtro, falha = [], False, f'{type(e).__name__}: {e}'
        return {'fontes': fontes, 'fontes_sem_filtro': sem_filtro,
                'falha_rag': falha,
                'raciocinio': state.get('raciocinio', []) + [...]}
    return node
```

O resultado de ML é válido sem protocolo. Uma exceção do Chroma degrada a citação, não a predição.
Ver `docs/langgraph/TRATAMENTO_DE_ERROS.md` §4.

---

## 7. Onde o RAG entra em cada caminho de execução

| Caminho | RAG roda? | Consulta construída a partir de |
|---|---|---|
| `normal` | Sim | `prediction` + `top_features` |
| `bypass_regra` | Sim | `regras_disparadas` (termos dos sinais de alarme) |
| `degradado` | Sim | rótulo da regra determinística |
| `incompleto` | **Não** | — |

**Decisão do ciclo 1 (T-04):** o caminho `incompleto` **não** chama RAG. Fonte de verdade:
`docs/langgraph/WORKFLOW_ML.md` §8. Motivo: sem features obrigatórias não há estratificação a
ancorar; o profissional precisa completar dados, não receber protocolo genérico que pode ser
lido como conduta. Orientação de pré-natal genérica fica registrada como extensão futura
(`dados_incompletos → recuperar_protocolos_rag`), não como escopo desta fase.

---

## 8. Melhorias — escopo declarado

### 8.1 Dentro do escopo desta fase

| ID | Melhoria | Justificativa | Risco |
|---|---|---|---|
| **R-01** | Filtro nativo de categoria no Chroma, com detecção de suporte e fallback ao pós-processamento | Corrige a falha de §5.1, que produz falso negativo de cobertura | Baixo — aditivo, comportamento atual preservado no fallback |
| **R-02** | `args_schema` em `buscar_protocolo` | Única tool sem schema; instabilidade de tool calling em 3B | Muito baixo — aditivo |
| **R-03** | Truncamento proporcional por fonte em vez de `[:2500]` no concatenado | Hoje o 2º ao 4º chunk nunca chegam ao prompt (§2.1) | Baixo — muda só o prompt do workflow novo |
| **R-04** | Registrar no estado quantas fontes foram recuperadas, quantas sobreviveram ao filtro e se houve fallback sem filtro | Torna a falha de §5.1 observável em vez de invisível | Nenhum |
| **R-05** | Conjunto de avaliação de recuperação e cálculo de recall@k / MRR | Hoje não existe nenhuma medida de qualidade do RAG | Nenhum — só medição |
| **R-06** | Reindexação local reprodutível para o perfil `demo-cpu` | Chroma é gitignored; sem isso o Docker não tem RAG | Médio — depende do JSON de fontes, que também não está no repo |

### 8.2 Fora do escopo, com motivo

| Melhoria | Por que fica de fora |
|---|---|
| Rechunking para 1000–1500 caracteres, alinhado à janela de 512 tokens | Provavelmente o de maior impacto (§3.1), mas invalida o índice de 1392 chunks e todos os números de documentação da Fase 3. Precisa de reindexação completa e de nova avaliação. **Registrado como recomendação principal para a fase seguinte** |
| Troca do encoder para `intfloat/multilingual-e5-base` | Já cogitado em `ARQUITETURA.md`. Melhor qualidade em PT, mas 768d e mais lento; exige reindexação e reavaliação |
| Busca híbrida (BM25 + denso) com *reranking* | Ganho real, custo alto: nova dependência, novo índice, e o reranker cruzado não roda bem em CPU no perfil `demo-cpu` |
| Expansão de consulta por LLM | Introduziria não-determinismo na recuperação e tornaria a avaliação irreprodutível |
| Extração de número de página e ano de publicação nos metadados | Depende de reprocessar os 39 PDFs, que não estão no repositório. Registrado como lacuna em `METADADOS_DAS_FONTES.md` §6 |
| `MultiQueryRetriever` / HyDE | Mesma objeção de não-determinismo, mais latência com um 3B |

---

## 9. Resumo dos achados sobre o RAG existente

Cinco achados de leitura de código, em ordem de gravidade:

1. **A janela de 512 tokens do encoder contra chunks de 6000 caracteres** faz o embedding
   representar cerca de um terço de cada chunk. Não documentado em nenhum lugar antes deste
   arquivo. (§3.1)
2. **O filtro por categoria em pós-processamento** pode devolver zero resultados com protocolo
   relevante indexado, e `k*2` não traz candidatos extras porque o retriever já fixou `k=4`. (§5.1)
3. **O truncamento em `[:2500]` do contexto concatenado** faz o 2º ao 4º chunk nunca chegarem ao
   prompt, enquanto `citar_fontes` os cita como consultados. (§2.1)
4. **`buscar_protocolo` sem `args_schema`** — a única das nove tools nessa condição. (§5.4)
5. **Duas implementações divergentes** da mesma recuperação, com defaults e ordem de parâmetros
   diferentes. (§5.3)

Os achados 1 e 3 juntos produzem um efeito que vale enunciar: **o sistema cita quatro fontes,
enquanto o LLM leu aproximadamente o primeiro terço de uma delas.**

---

## 10. Estado atual

| Item | Estado |
|---|---|
| Índice Chroma | `[AUS]` no repositório; `[VAL]` no Drive |
| `files/fontes_saude_mulher_v2.json` | `[AUS]` no repositório |
| Contagem de 1392 chunks / 39 PDFs | `[DOC]`, não verificada nesta fase |
| `rag_search` | `[COD]` — existe e funciona |
| Filtro nativo no Chroma (R-01) | **Não implementado** |
| `args_schema` em `buscar_protocolo` (R-02) | **Não implementado** |
| Nó `recuperar_protocolos_rag` | **Não implementado** |
| Avaliação de recuperação | **Nunca executada** |
