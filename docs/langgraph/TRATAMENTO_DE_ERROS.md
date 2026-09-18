# Tratamento de Erros

**Agente responsável:** `LangGraphAgent`
**Status:** Especificação. **Nenhum tratamento de erro existe hoje em nenhum dos quatro workflows.**
**Vinculado a:** `WORKFLOW_ML.md` · `ESTADOS_E_TRANSICOES.md` · `ARQUITETURA_ALVO.md` §4 e §8 ·
`CONTRATOS_DE_COMPONENTES.md`

---

> ### Banner de estado
> A lacuna é confirmada por leitura de código, não inferida: busca por `try`, `except`, `raise`,
> `retry` e `timeout` em `lib/workflows/*.py` retorna **zero ocorrências de tratamento de erro**.
> Registrado em `00_INVENTARIO_PROJETO.md` §6, achado 4. Nada do que este documento especifica está
> implementado.

---

## 1. O estado atual, com precisão

### 1.1 Não há `try/except` em nenhum workflow

Qualquer exceção levantada dentro de um nó sobe pelo `StateGraph`, sai de `wf.invoke(...)` em
`lib/ui.py` e chega ao Gradio, que exibe um traceback. Os pontos que podem estourar:

| Origem | Onde | Exceção plausível |
|---|---|---|
| `chat_model.invoke` | 10 nós LLM nos quatro workflows | OOM de GPU, timeout, erro de tokenização |
| `retriever.invoke` | `common.rag_search`, 5 chamadas | Chroma não carregado, diretório de persistência ausente |
| `conn.execute` | `prevencao.py:100,118`, `violencia.py:188` | banco somente leitura, arquivo ausente |
| Acesso direto a chave | `state["descricao_caso"]`, `state["queixa"]` | `KeyError` se o invocador omitir |
| `date.fromisoformat` | `prevencao.py:107,125` | `ValueError` com data malformada |
| Indexação | `alertas_mod.SINAIS_VIOLENCIA[s]` em `violencia.py:240` | `KeyError` se o estado tiver chave inválida |

A última linha tem uma proteção parcial: `_extrair_sinais` filtra contra `SINAIS_KEYS`
(`violencia.py:83`). É a única validação de saída de LLM em todo o código — e é boa.

### 1.2 Há falhas silenciosas, que são piores

Ausência de tratamento produz traceback, que ao menos é visível. Falha silenciosa produz resposta
de aparência normal. O código tem três:

| # | Local | Comportamento | Consequência |
|---|---|---|---|
| **FS-1** | `common.llm_json:49` | Parse falhou → devolve `default` | Ver §3. **A mais grave** |
| **FS-2** | `prevencao.py:64-68` | Sem `paciente_id` → `perfil = {'erro': ...}` e o fluxo segue | Nós seguintes leem `perfil.get('idade', 0)` → `0`; nenhuma faixa etária casa; resposta vazia de aparência normal |
| **FS-3** | `violencia.py:105-119` | `medidas` construída e não devolvida | Seis condutas clínicas descartadas a cada execução |

FS-3 não é erro de execução, mas é perda silenciosa de conteúdo clínico — mesma família.

### 1.3 Degradação graciosa existe em um lugar só

`prevencao.py:236-243`, `_gerar_lembretes`: se o LLM devolver menos lembretes do que há
agendamentos, o nó completa a lista por template e **declara** no `raciocinio`. É o único fallback
explícito do código atual, e é o padrão que este documento generaliza.

---

## 2. Taxonomia de erros

Sete classes. A coluna "política" é desenvolvida em §4.

| ID | Classe | Exemplo | Detectável onde | Política | `modo` resultante |
|---|---|---|---|---|---|
| **E1** | **Validação** | `pas_mmhg = 300`; `pad >= pas`; `partos + abortos > gestacoes` | `validar_dados` | **fail-fast declarado** | `incompleto` |
| **E2** | **Dados incompletos** | `imc_pre_gestacional` ausente | `validar_dados` | **fail-fast + HIL** | `incompleto` |
| **E3** | **Modelo indisponível** | artefato ausente, corrompido, MAJOR incompatível | `executar_modelo_ml` | **degradar** | `degradado` |
| **E4** | **Falha de RAG** | Chroma não carrega; exceção em `retriever.invoke` | `recuperar_protocolos_rag` | **degradar** (parcial) | inalterado |
| **E5** | **Falha de LLM** | exceção na geração, timeout, texto reprovado | `sintetizar_com_llm`, `validar_resposta_llm` | **degradar** para resposta estruturada | inalterado |
| **E6** | **Falha de auditoria** | `INSERT` falha | `auditar` | **declarar, não abortar** | inalterado + flag |
| **E7** | **Falha de persistência (outras)** | leitura de `hospital.db` falha | qualquer nó com `conn` | **retry limitado, depois degradar** | conforme o caso |

### 2.1 Por que E1 e E2 são classes distintas

Ambas barram a predição e ambas auditam como `incompleto`, mas exigem ações opostas do humano:

- **E1** — o dado está lá e está errado. Ação: corrigir. A resposta mostra valor recebido × faixa
  aceita.
- **E2** — o dado não está lá. Ação: coletar. A resposta lista os campos e como obtê-los.

Fundi-las produziria uma mensagem que serve mal aos dois casos. São nós distintos
(`erro_validacao` e `dados_incompletos`) por essa razão.

### 2.2 Por que E4 e E5 não mudam o `modo`

`modo` audita a **decisão clínica**, não a qualidade da apresentação. Falha de RAG ou de LLM não
altera a predição: os números são os mesmos, com ou sem protocolo citado, com ou sem texto gerado.
Marcar `degradado` nesses casos confundiria "o modelo não rodou" com "o texto não foi aprovado" —
duas coisas com significados clínicos opostos.

O que muda é o conteúdo da resposta e o conteúdo do rastro, que é onde a informação pertence.

---

## 3. A correção da falha silenciosa de `common.llm_json`

### 3.1 O defeito

```python
# lib/workflows/common.py:21-49  [COD]
def llm_json(chat_model, user_prompt, system_prompt=None, default=None):
    ...
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    for pattern in (r'\{.*\}', r'\[.*\]'):
        m = re.search(pattern, cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                continue
    return default if default is not None else {}     # ← falha silenciosa
```

O chamador recebe um dicionário. **Não tem como distinguir** "o LLM respondeu isso" de "o LLM
falhou e isto é o default". A função devolve o mesmo tipo nos dois casos, sem sinal algum.

### 3.2 Onde isso morde

| Chamador | `default` | Consequência da falha de parse |
|---|---|---|
| `obstetrico.py:135-136` | `{'classificacao': 'habitual', 'fatores': []}` | **Falso negativo clínico.** Gestante classificada como risco habitual porque o parser falhou |
| `triagem.py:145-146` | `{'urgencia': 'agendado', ...}` | Urgência rebaixada silenciosamente |
| `triagem.py:85` | `{'sintomas': []}` | Nenhum sintoma extraído; a query do RAG vira a queixa crua |
| `triagem.py:109` | `{'diferenciais': []}` | Diferenciais vazios |
| `violencia.py:82` | `{'sinais': []}` | `score = 0`, `nivel = 'sem_alerta'`. **Falso negativo em violência** |
| `obstetrico.py:107` | `{}` | Dados da gestante vazios |
| `prevencao.py:232` | `{'lembretes': []}` | Único caso com fallback explícito a jusante |

Duas dessas linhas são falso negativo em domínio clínico sensível. A de `obstetrico.py` é
literalmente a justificativa da ADR-002 e do projeto de ML inteiro
(`DEFINICAO_DO_PROBLEMA.md` §1):

> "o `default` em caso de falha de parse é `'habitual'` — ou seja, **a falha silenciosa do LLM
> produz um falso negativo**, que é o pior erro possível neste domínio."

A de `violencia.py` é do mesmo tipo e **não está registrada em nenhum documento anterior**: se o
LLM não produzir JSON parseável, `sinais_identificados` fica vazio,
`alertas.avaliar_padrao_violencia([])` devolve score 0, e o fluxo segue por `sem_alerta` até o fim,
com aparência de avaliação normal. O `raciocinio` registra "Sinais identificados pelo LLM: nenhum"
— indistinguível de um caso legitimamente sem sinais.

### 3.3 A correção proposta

Um sentinela explícito, mais uma flag no estado.

```python
# lib/workflows/common.py  — PROJETADO, aditivo

class FalhaParseLLM:
    """Sentinela devolvido quando nenhuma estratégia de parse funcionou.

    Falsy de propósito: `if not out:` continua funcionando nos chamadores
    que já testam o resultado. Mas `isinstance(out, FalhaParseLLM)`
    distingue "falhou" de "veio vazio".
    """
    __slots__ = ('texto_bruto', 'motivo')

    def __init__(self, texto_bruto: str, motivo: str):
        self.texto_bruto = texto_bruto[:500]
        self.motivo = motivo

    def __bool__(self) -> bool:
        return False

    def get(self, chave, padrao=None):
        """Compatível com o uso atual `out.get('campo', default)`."""
        return padrao


def llm_json(chat_model, user_prompt, system_prompt=None, default=None,
             sinalizar_falha: bool = False):
    """...

    sinalizar_falha=False (padrão): comportamento ATUAL, inalterado.
    sinalizar_falha=True: devolve FalhaParseLLM em vez do default.
    """
    ...
    if sinalizar_falha:
        return FalhaParseLLM(texto_bruto=text, motivo='json_nao_parseavel')
    return default if default is not None else {}
```

**O parâmetro tem default `False`.** Sem isso, a mudança alteraria o comportamento dos quatro
workflows existentes, violando a ADR-001. Com ele, `risco_ml.py` e o nó novo do obstétrico pedem o
comportamento honesto; os demais seguem idênticos.

### 3.4 Uso no chamador

```python
out = common.llm_json(chat_model, prompt, sistema, sinalizar_falha=True)

if isinstance(out, common.FalhaParseLLM):
    return {
        'falha_parse': True,
        'falhas': state.get('falhas', []) + [{
            'classe': 'E5',
            'no': 'extrair_dados',
            'motivo': out.motivo,
            'amostra': out.texto_bruto[:200],
        }],
        'raciocinio': state.get('raciocinio', []) + [
            'FALHA: a saída do LLM não pôde ser interpretada. '
            'Nenhum valor foi assumido — o campo permanece indefinido.'
        ],
    }
```

Três propriedades:

1. **Nenhum valor clínico é assumido.** Nem `habitual`, nem `agendado`, nem `[]`. O campo fica
   indefinido, e o caminho de dados incompletos trata disso.
2. **A falha entra em `falhas`**, com classe, nó e amostra do texto bruto — depurável.
3. **A falha entra no `raciocinio`**, que a UI já renderiza. O profissional vê.

### 3.5 Registro em `risco_ml`

`sintetizar_com_llm` **não usa** `llm_json` — a saída do LLM é texto, não JSON, exatamente para
evitar este caminho (`CONTRATO_ENTRADA_SAIDA_LLM.md` §5.1). O uso previsto de `llm_json` no fluxo
novo é nenhum. A correção existe para o nó opcional do obstétrico e para uso futuro.

---

## 4. Política por classe

### 4.1 E1 — Validação: **fail-fast declarado**

| Item | Definição |
|---|---|
| Ação | Interrompe antes de qualquer inferência |
| Retry | **Não.** O dado não muda sozinho |
| Degradação | **Não.** Predizer com dado fora do domínio seria pior que não predizer |
| Usuário vê | Uma linha por campo: nome, valor recebido, faixa aceita |
| Estado | `erros_validacao` preenchido, `features=None`, `modo='incompleto'` |
| Auditoria | `modo='incompleto'`, `probabilidade=NULL`, `threshold=NULL` |

### 4.2 E2 — Dados incompletos: **fail-fast + human-in-the-loop**

| Item | Definição |
|---|---|
| Ação | Interrompe. **Nunca imputa campo obrigatório** (`CONTRATOS_DE_COMPONENTES.md` §1, invariante iv) |
| Retry | Não automático. O retry é o humano completando os dados |
| Usuário vê | Lista de campos faltantes com nome clínico e como obter |
| Estado | `campos_faltantes`, `requer_intervencao_humana=True`, `intervencao` |
| Auditoria | `modo='incompleto'` |

**Não é caminho raro.** Ver `WORKFLOW_ML.md` §5.3: 6 das 11 features obrigatórias faltam para toda
paciente de `hospital.db`.

### 4.3 E3 — Modelo indisponível: **degradar e declarar**

| Item | Definição |
|---|---|
| Ação | Cai para a regra determinística `CRITERIOS_ALTO_RISCO` |
| Retry | **Não.** Artefato ausente ou MAJOR incompatível não melhora com nova tentativa |
| Usuário vê | Declaração de modo degradado na **primeira** seção, não em rodapé |
| Estado | `modo='degradado'`, `falha_modelo`, `regras_disparadas` (critérios atendidos) |
| Auditoria | `modo='degradado'`, `probabilidade=NULL` |

### 4.4 E4 — Falha de RAG: **degradar parcialmente**

| Item | Definição |
|---|---|
| Ação | `fontes=[]`; a predição segue |
| Retry | **1 tentativa**, imediata. Falhas transitórias de I/O são plausíveis |
| Usuário vê | "Não foi possível consultar a base de protocolos nesta execução. A estratificação abaixo não tem suporte documental anexado." |
| Estado | `falha_rag` preenchido |
| Auditoria | `modo` **inalterado** |

**Essa mensagem precisa ser distinta de "os protocolos não cobrem este cenário".** Hoje as duas
situações seriam indistinguíveis, e o sistema afirmaria falsamente que os protocolos não cobrem o
caso quando na verdade não conseguiu consultá-los (`docs/rag/POLITICA_DE_CITACAO.md` §5.3).

### 4.5 E5 — Falha de LLM: **degradar para resposta estruturada**

| Item | Definição |
|---|---|
| Ação | `usar_resposta_estruturada` |
| Retry | **Não.** Regeneração custa 5–10 s e produz texto igualmente não verificado (ADR-010) |
| Usuário vê | Faixa de `POLITICA_ANTI_ALUCINACAO.md` §7.3 + resposta estruturada completa |
| Estado | `falha_llm` ou `verificacao.aprovada == False`; `texto_descartado=True` |
| Auditoria | `modo` **inalterado** |

Exceção de geração e reprovação na verificação entram pela **mesma porta**. Uma só saída
(`usar_resposta_estruturada`), um só caminho a testar.

### 4.6 E6 — Falha de auditoria: **declarar, nunca abortar**

| Item | Definição |
|---|---|
| Ação | Registra erro crítico no log estruturado; a execução continua |
| Retry | **1 tentativa.** `sqlite3.OperationalError` por lock é transitório e comum |
| Usuário vê | "⚠️ Esta predição **não foi registrada** na trilha de auditoria. Documente manualmente." |
| Estado | `auditoria_falhou=True`, `auditoria_id=None` |
| Log | Nível `CRITICAL` com `correlation_id` |

Duas decisões nesta linha:

**Por que não abortar.** A predição já ocorreu e é clinicamente válida. Recusar a entrega porque o
banco falhou puniria o profissional por um problema de infraestrutura.

**Por que é crítico mesmo assim.** "Toda predição é auditável" é princípio de
`ARQUITETURA_ALVO.md` §8. Uma predição entregue sem rastro é violação, e precisa ser **visível** —
ao usuário e ao log. É exatamente o que `CONTRATOS_DE_COMPONENTES.md` §8 exige: "não pode ser
silenciada […] marca a resposta como não auditada".

### 4.7 E7 — Falha de persistência: **retry limitado, depois degradar**

| Item | Definição |
|---|---|
| Ação | Retry, depois segue sem o dado |
| Retry | **2 tentativas**, 100 ms e 300 ms |
| Usuário vê | Nome do dado indisponível, não traceback |
| Estado | `falhas` recebe entrada `E7` |

---

## 5. Contrato do modo degradado

### 5.1 Definição

> **Modo degradado** é o estado em que o sistema entrega um resultado produzido por um caminho
> **inferior ao projetado**, e **declara isso** ao usuário, na primeira informação da resposta.

### 5.2 Obrigações

| # | Obrigação |
|---|---|
| D-1 | A degradação é declarada **antes** do resultado, nunca depois |
| D-2 | A **origem** do resultado é nomeada ("regra determinística MS/FEBRASGO", não "o sistema") |
| D-3 | Nenhum número de modelo é apresentado. Não há probabilidade nem limiar no modo degradado |
| D-4 | A auditoria registra `modo='degradado'` com `probabilidade=NULL` |
| D-5 | Os dois avisos obrigatórios continuam presentes |
| D-6 | A degradação **nunca** é presumida como aceitável: o log registra `ERROR`, não `INFO` |

### 5.3 Níveis

| Nível | Gatilho | O que ainda funciona | O que se perde |
|---|---|---|---|
| **N0 — normal** | — | tudo | — |
| **N1 — sem texto** | E5 | predição, explicabilidade, RAG, auditoria | narrativa; resposta estruturada no lugar |
| **N2 — sem protocolo** | E4 | predição, explicabilidade, texto, auditoria | citação documental |
| **N3 — sem modelo** | E3 | regra determinística, RAG, texto, auditoria | probabilidade, limiar, explicabilidade |
| **N4 — sem predição** | E1, E2 | validação, HIL, auditoria | toda a estratificação |
| **N5 — sem rastro** | E6 | tudo o mais | auditabilidade — **o mais grave** |

N5 é o único nível em que a perda não é visível no conteúdo da resposta, e por isso é o que mais
precisa de declaração explícita.

Níveis se acumulam: N2+N3 é possível (Chroma e modelo fora). A resposta declara os dois.

### 5.4 A regra que organiza tudo

> **Falha é explícita ao usuário. Nunca silenciosa.**

`ARQUITETURA_ALVO.md` §8, linha "Falha é explícita". Operacionalmente:

| Proibido | Obrigatório |
|---|---|
| Devolver valor default clínico em falha de parse | Sentinela + flag + declaração (§3) |
| Tratar exceção e seguir sem registrar | `falhas` + `raciocinio` + log |
| Resposta vazia sem explicação | Declarar o que faltou e por quê |
| Apresentar resultado de regra como se fosse de modelo | Nomear a origem (D-2) |
| Entregar sem auditar e não avisar | Aviso explícito (§4.6) |
| Dizer "protocolos não cobrem" quando o RAG falhou | Mensagem distinta (§4.4) |

---

## 6. Política de retry

### 6.1 Onde há retry

| Classe | Tentativas | Espera | Justificativa |
|---|---|---|---|
| E4 — RAG | 1 extra | imediata | I/O de arquivo local pode falhar transitoriamente |
| E6 — auditoria | 1 extra | 200 ms | Lock de SQLite é transitório e comum |
| E7 — persistência | 2 extras | 100 ms, 300 ms | idem |

### 6.2 Onde **não** há retry

| Classe | Por quê |
|---|---|
| E1 — validação | O dado não muda entre tentativas |
| E2 — dados incompletos | O campo não aparece sozinho |
| E3 — modelo indisponível | Artefato ausente ou incompatível é condição estável |
| E5 — LLM | Custo de 5–10 s; texto novo também não verificado; ADR-010 |

### 6.3 Limites globais

| Limite | Valor | Motivo |
|---|---|---|
| Retries por execução do grafo | 3 no total | Impede acúmulo silencioso de latência |
| Timeout por nó LLM | 60 s | Acima disso a UI está travada para o usuário |
| Timeout por nó RAG | 10 s | Busca local; mais que isso é falha |
| Retry como aresta do grafo | **proibido** | Ciclo exigiria contador no estado e cria risco de laço infinito |

O retry vive **dentro** do nó. O grafo permanece acíclico (`ESTADOS_E_TRANSICOES.md` §7.1, P-4).

---

## 7. Como o erro aparece na auditoria

### 7.1 A coluna `modo`

DDL em `ARQUITETURA_ALVO.md` §5.3: `modo TEXT NOT NULL` ∈
`{'normal','degradado','bypass_regra','incompleto'}`.

| Classe | `modo` | `probabilidade` | `threshold` | `regras_disparadas` |
|---|---|---|---|---|
| sem erro | `normal` | do modelo | do `model_card` | `[]` |
| E1 | `incompleto` | `NULL` | `NULL` | `[]` |
| E2 | `incompleto` | `NULL` | `NULL` | `[]` |
| E3 | `degradado` | `NULL` | `NULL` | critérios atendidos |
| E4 | inalterado | inalterada | inalterado | inalterado |
| E5 | inalterado | inalterada | inalterado | inalterado |
| E6 | — | — | — | — (não há linha) |
| bypass por regra | `bypass_regra` | `NULL` | `NULL` | sinais de alarme |

### 7.2 Três limitações da coluna `modo`, ditas abertamente

**L-1. `modo` não distingue E1 de E2.** Erro de domínio e dado faltante auditam ambos como
`incompleto`. São situações diferentes com ações diferentes. Resolver exigiria um quinto valor no
domínio, o que altera o DDL publicado. Registrado em `WORKFLOW_ML.md` §8; requer ADR.

**L-2. `modo` não registra E4 nem E5.** Falha de RAG e descarte de texto não aparecem em
`predicoes_ml`. Ficam no log estruturado e no `raciocinio`, que **não são persistidos**. Consulta
retrospectiva à tabela não responde "quantas respostas foram descartadas". O agregado fica em
`artifacts/metrics/verificacao_llm.json`, produzido por execução de script — não por consulta ao
banco.

**L-3. E6 não tem como ser registrado na própria tabela.** Se o `INSERT` falhou, não há linha. O
registro vai para o log estruturado, com `correlation_id`. Consequência: **o número real de
execuções é o do log, não o da tabela**, e reconciliar os dois é a única forma de detectar E6 a
posteriori.

Nenhuma das três é corrigida nesta fase. Todas são consequência de preservar o DDL publicado, o que
é a escolha conservadora — e o custo está dito.

### 7.3 O log estruturado

`lib/observabilidade.py` (não existe). Cada falha gera:

```json
{
  "timestamp": "...",
  "correlation_id": "...",
  "nivel": "ERROR",
  "evento": "falha_no_workflow",
  "workflow": "risco_ml",
  "no": "recuperar_protocolos_rag",
  "classe_erro": "E4",
  "excecao": "ChromaError",
  "mensagem": "...",
  "modo_resultante": "normal",
  "retries": 1,
  "auditoria_id": 142
}
```

`correlation_id` é o que amarra log, rastro e linha de auditoria. Sem ele, L-3 seria
irreconciliável.

---

## 8. Erros nos quatro workflows existentes

O escopo desta fase **não** inclui adicionar tratamento a `triagem.py`, `violencia.py`,
`obstetrico.py` nem `prevencao.py` — ADR-001 os classifica como "não tocar".

Registro do que ficaria a fazer, por prioridade:

| Prioridade | Workflow | Correção | Impacto |
|---|---|---|---|
| **1** | `violencia.py:82` | `sinalizar_falha=True` em `_extrair_sinais` | Falha de parse produz `sem_alerta` indistinguível de caso sem sinais. **Falso negativo em violência doméstica** |
| **2** | `obstetrico.py:135` | `sinalizar_falha=True` em `_avaliar_risco_gestacional` | Falso negativo de alto risco. **Mitigado** pelo nó de ML da ADR-012, que sobrescreve a classificação quando a flag está ligada |
| **3** | `prevencao.py:64-68` | Nó de erro em vez de `perfil={'erro':...}` | Resposta vazia com aparência normal |
| **4** | `violencia.py:105-119` | Devolver `medidas` | Perda de seis condutas clínicas |
| **5** | todos | `try/except` em torno de `chat_model.invoke` | Traceback no Gradio |

A prioridade 1 é a mais séria das cinco e **não estava registrada em nenhum documento anterior**
desta entrega. A prioridade 2 é a que a ADR-002 usa como justificativa do projeto de ML.

---

## 9. Testes de erro exigidos

| ID | Cenário | Verifica | Arquivo planejado |
|---|---|---|---|
| ERR-01 | `pas_mmhg=300` | E1; `modo='incompleto'`; erro nomeia campo e faixa | `tests/unit/test_erros_validacao.py` |
| ERR-02 | `pad >= pas` | E1; invariante cruzado | idem |
| ERR-03 | 6 obrigatórias ausentes | E2; `campos_faltantes` com os 6; HIL acionado | idem |
| ERR-04 | Artefato de modelo ausente | E3; `modo='degradado'`; declaração na 1ª seção | `tests/integration/test_modo_degradado.py` |
| ERR-05 | `model_card` com MAJOR incompatível | E3; não carrega, degrada | idem |
| ERR-06 | Chroma levanta exceção | E4; predição preservada; mensagem distinta de "não cobrem" | `tests/integration/test_falha_rag.py` |
| ERR-07 | `chat_model.invoke` levanta | E5; resposta estruturada; sem crash | `tests/integration/test_falha_llm.py` |
| ERR-08 | Banco somente leitura | E6; `auditoria_falhou=True`; aviso ao usuário; log CRITICAL | `tests/integration/test_falha_auditoria.py` |
| ERR-09 | `llm_json` com `sinalizar_falha=True` e saída não-JSON | Devolve `FalhaParseLLM`; nenhum default clínico | `tests/unit/test_llm_json.py` |
| ERR-10 | `llm_json` com `sinalizar_falha=False` | Comportamento **idêntico ao atual** | idem — **teste de regressão da ADR-001** |
| ERR-11 | E3 + E4 simultâneos | N2+N3; ambas as degradações declaradas | `tests/integration/test_degradacao_composta.py` |
| ERR-12 | Timeout no nó LLM | Respeitado; degrada para estruturada | `tests/integration/test_falha_llm.py` |
| ERR-13 | Todos os caminhos de erro auditam | Uma linha em `predicoes_ml` por execução, em qualquer modo | `tests/integration/test_auditoria_sempre.py` |

ERR-10 é o teste que protege a ADR-001: sem ele, a correção de §3 poderia alterar silenciosamente o
comportamento dos quatro workflows existentes.

---

## 10. Estado atual

| Item | Estado |
|---|---|
| `try/except` em qualquer workflow | **Zero** |
| Retry em qualquer lugar | **Zero** |
| Timeout em qualquer lugar | **Zero** |
| `FalhaParseLLM` e `sinalizar_falha` | **Não existem** |
| Nós de erro (`erro_validacao`, `modo_degradado`) | **Não existem** |
| `lib/observabilidade.py` | **Não existe** |
| Tabela `predicoes_ml` | **Não existe** |
| `correlation_id` em qualquer lugar | **Não existe** |
| Testes ERR-01 a ERR-13 | **Nenhum** |
| Falhas silenciosas FS-1, FS-2, FS-3 | **Presentes no código** |
