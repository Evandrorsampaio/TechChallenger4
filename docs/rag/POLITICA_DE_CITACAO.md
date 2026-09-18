# Política de Citação de Fontes

**Agente responsável:** `RAGAgent`
**Status:** Especificação. A citação **existe parcialmente** hoje (`common.citar_fontes`,
`lib/agent.py` SYSTEM_PROMPT) e é `[COD]`; a obrigatoriedade verificada é `[PROJ]` e não está
implementada.
**Vinculado a:** `ESTRATEGIA_RAG.md` · `METADADOS_DAS_FONTES.md` ·
`docs/llm/POLITICA_ANTI_ALUCINACAO.md` · ADR-007

---

> ### Banner de estado
> A regra "nada sem suporte documental" é um **princípio arquitetural declarado**
> (`ARQUITETURA_ALVO.md` §8), não um controle implementado. Hoje ela é pedida no prompt e
> parcialmente verificada pela regra 4 do `ValidadorDeterministico` — que emite **aviso**, não
> bloqueio. Nenhuma taxa de conformidade foi medida.

---

## 1. O princípio

> **O sistema não emite orientação dependente de protocolo sem suporte documental recuperado.**

"Dependente de protocolo" é a qualificação que faz a regra ser aplicável em vez de utópica. Nem
toda frase precisa de citação — dizer "a gestante tem 32 anos" não precisa. O que precisa é
enunciado em §2.

A regra deriva de `ARQUITETURA_ALVO.md` §8 ("Nada sem suporte documental: fontes RAG anexadas ao
payload; resposta cita `doc_id`") e da regra de uso de tools de `lib/agent.py`
("`buscar_protocolo` — SEMPRE que a pergunta envolver conduta clínica, posologia, fluxo, critério
diagnóstico ou encaminhamento. Cite trecho e fonte (`doc_id`) ao final da resposta").

---

## 2. Quando a citação é OBRIGATÓRIA

Citação obrigatória significa: **a afirmação não pode ser entregue sem um `doc_id` associado.** Se
não há fonte, a afirmação é removida do texto — não entregue sem fonte.

| # | Tipo de afirmação | Exemplo | Por quê |
|---|---|---|---|
| **C-1** | **Conduta clínica** | "Encaminhar ao pré-natal de alto risco" | É a saída acionável do sistema. Sem protocolo, é opinião de um modelo de 3B |
| **C-2** | **Posologia ou dose** | "AAS 100 mg/dia a partir de 12 semanas" | Erro de dose tem consequência direta. Já é regra 2 do `ValidadorDeterministico` |
| **C-3** | **Fluxo assistencial** | "Encaminhar ao PS obstétrico antes de nova aferição" | Define para onde a paciente vai |
| **C-4** | **Critério diagnóstico ou de classificação** | "PA ≥ 140/90 após 20 semanas com proteinúria" | Critério errado gera classificação errada em cascata |
| **C-5** | **Periodicidade de acompanhamento ou exame** | "Retorno em 7 dias", "TOTG entre 24 e 28 semanas" | É prescrição de seguimento |
| **C-6** | **Indicação ou contraindicação** | "Contraindicado em gestante com nefropatia" | Idem C-2 |
| **C-7** | **Encaminhamento à rede em caso sensível** | "Notificação SINAN compulsória" | Já é regra 3 do `ValidadorDeterministico` |

### 2.1 O caso especial de C-5 e o conteúdo determinístico do projeto

`obstetrico.py:219-273` (`_agendar_exames`) e `:276-317` (`_definir_acompanhamento`) já produzem
periodicidades e rotinas de exame — **em código, sem RAG**. "Próxima consulta em 7 dias",
"TOTG 75 g entre 24 e 28 semanas" e "cultura de Streptococcus B entre 35 e 37 semanas" estão
escritos como literais Python.

Isso é C-5 sem citação. A política **não** trata isso como violação, e a distinção é importante:

| Origem da afirmação | Citação exigida | Forma da atribuição |
|---|---|---|
| Texto gerado por LLM | **Sim**, `doc_id` do RAG | `Fonte: <doc_id>, <categoria>` |
| Regra determinística codificada em `lib/` | Não `doc_id`, mas **sim atribuição** | `Fonte: rotina de pré-natal MS (regra do sistema)` |

O motivo: uma regra codificada é auditável lendo o fonte, é estável entre execuções e não foi
inventada por um modelo. O risco que a citação mitiga — invenção — não existe ali. O que se exige é
que a **origem** seja distinguível, para que o profissional saiba se está lendo protocolo
recuperado ou regra do sistema.

**Consequência prática:** a resposta pode ter dois tipos de rodapé de origem, e eles não se
confundem. Isso é uma extensão do que existe hoje, onde toda origem se apresenta igual.

---

## 3. Quando a citação é OPCIONAL

| Situação | Exemplo |
|---|---|
| Reprodução de dado de entrada | "IG de 32 semanas", "IMC 31" |
| Reprodução de saída do modelo | "probabilidade 0,75, acima do limiar 0,31" |
| Explicação do próprio funcionamento do sistema | "o limiar foi escolhido para priorizar sensibilidade" |
| Avisos obrigatórios | `safety_notice`, `aviso_dados_sinteticos` |
| Declaração de ausência de cobertura | a frase de §5 |
| Linguagem de ligação e organização do texto | títulos de seção, conectivos |

**Nota sobre a segunda linha.** A saída do modelo não é citável por protocolo porque não veio de
protocolo. Ela tem sua própria forma de rastreabilidade: `model_name`, `model_version`,
`dataset_version` e a linha em `predicoes_ml`. Citar um protocolo ao lado de uma probabilidade
sugeriria que o protocolo endossa aquele número, o que seria falso.

---

## 4. Formato da citação

### 4.1 Forma normativa

```
Fonte: <doc_id>, <categoria>
```

Exemplo:

```
Fonte: manual_prenatal_ms_2022.pdf, ginecologia_obstetricia
```

### 4.2 Forma por afirmação, dentro do corpo

Quando a conduta é um bullet, a fonte vem ao final do próprio bullet, para que a ligação entre
afirmação e origem seja inequívoca:

```markdown
- Iniciar profilaxia de pré-eclâmpsia com AAS a partir de 12 semanas. Fonte: `febrasgo_hipertensao_2023.pdf`
```

Amarrar a fonte ao bullet, e não só à lista, é o que permite que uma resposta com quatro condutas e
duas fontes deixe claro **qual conduta veio de qual documento**.

### 4.3 Bloco consolidado ao final

Mantido como está hoje em `common.citar_fontes`, que produz:

```markdown
**Fontes consultadas:**
- `manual_prenatal_ms_2022.pdf` (ginecologia_obstetricia)
- `febrasgo_hipertensao_2023.pdf` (ginecologia_obstetricia)
```

Deduplicado por `doc_id` (`common.py:87-91`). Esse comportamento é preservado.

### 4.4 O que a citação NÃO inclui, e deveria

Ver `METADADOS_DAS_FONTES.md` §6. Em resumo: **não há número de página, ano de publicação, órgão
emissor nem versão do protocolo**, porque esses campos não existem nos metadados indexados. A
citação atual identifica *o arquivo*, não *o lugar no documento* nem *a edição*.

Para protocolo clínico, isso é uma limitação relevante e precisa aparecer na própria interface, não
só nesta documentação.

---

## 5. Quando o RAG não devolve nada

### 5.1 A frase canônica

O sistema deve dizer, literalmente:

> Os protocolos disponíveis não cobrem este cenário.

Essa string **já existe** em `lib/agent.py`, SYSTEM_PROMPT, regra 4 de comportamento:

```
- Quando o protocolo não responder claramente a uma dúvida, diga isso explicitamente:
  "Os protocolos disponíveis não cobrem este cenário".
```

Ela é reusada sem reescrita nos prompts novos (`PROMPTS_DE_EXPLICACAO.md`, seção
`### Conduta sugerida` de todas as variantes). Uma única forma de dizer "não sei" — se houvesse
duas, a equipe teria que aprender a distingui-las, e a diferença acabaria sendo interpretada como
significativa quando não é.

### 5.2 O que NÃO fazer quando não há fonte

| Tentação | Por que é recusada |
|---|---|
| Responder com conhecimento paramétrico do LLM | É exatamente a alucinação que o RAG existe para evitar. Um Llama 3B fine-tunado em dados sintéticos não é fonte clínica |
| Omitir a seção de conduta e não dizer nada | Silêncio é ambíguo: o leitor não sabe se não há conduta ou se o sistema falhou |
| Emitir conduta "genérica e segura" sem fonte | Conduta genérica ainda é conduta. E "seguro" é julgamento clínico que o sistema não tem competência para fazer |
| Marcar como erro do sistema | Não é erro. Ausência de cobertura documental é resultado legítimo |

### 5.3 Distinguir "não cobriu" de "não buscou" de "falhou"

Três situações diferentes que produziriam a mesma tela se não fossem separadas:

| Situação | `retrieved_sources` | O que o texto diz |
|---|---|---|
| Buscou, índice respondeu, nada relevante | `[]`, `falha_rag = None` | "Os protocolos disponíveis não cobrem este cenário." |
| Buscou com filtro, veio vazio, refez sem filtro e achou | preenchido, `fontes_sem_filtro = True` | Cita normalmente, **mais** nota de que a busca foi ampliada para fora da categoria |
| Chroma falhou | `[]`, `falha_rag` preenchido | "Não foi possível consultar a base de protocolos nesta execução. A estratificação abaixo não tem suporte documental anexado." |

A terceira linha é uma exigência de `TRATAMENTO_DE_ERROS.md`: falha é explícita ao usuário, nunca
silenciosa. Hoje ela seria indistinguível da primeira — o que faria o sistema afirmar que os
protocolos não cobrem o cenário quando na verdade ele não conseguiu consultá-los. Essa é uma
afirmação falsa gerada por tratamento de erro ausente.

---

## 6. Categorias sensíveis: citação **e** rede

Quando alguma fonte recuperada tem `category ∈ {violencia_domestica, saude_mental}`, a citação do
`doc_id` **não é suficiente**. A resposta precisa, adicionalmente, nomear ao menos um serviço da
rede de proteção:

`SINAN` · `Ligue 180` · `CVV 188` · `CAPS` · `SAMU 192` · `Delegacia da Mulher` ·
`Centro de Referência`

Esta é a regra 3 do `ValidadorDeterministico` (`referencias/validador_resposta_llm.py`,
`CATEGORIAS_SENSITIVE` × `SERVICOS_REDE`), e é **bloqueante**: a ausência descarta a resposta.

A razão de ser mais rigorosa aqui é assimetria de consequência. Numa resposta sobre rastreamento de
colo uterino, a falta de citação produz uma orientação sem lastro. Numa resposta sobre violência
doméstica, a falta de encaminhamento à rede produz uma paciente que sai do serviço sem saber para
onde ir.

---

## 7. Verificação da política

### 7.1 O que é verificado hoje `[COD]`

| Regra | Onde | Bloqueia? |
|---|---|---|
| Menção a fonte ou a sociedade médica no texto | `ValidadorDeterministico` regra 4 | **Não** — aviso |
| Serviço da rede em categoria sensível | `ValidadorDeterministico` regra 3 | Sim — mas o validador **não está integrado** |
| Posologia sem referência a protocolo | `ValidadorDeterministico` regra 2 | Sim — idem |

O detalhe que anula as duas últimas linhas: o validador vive em `referencias/` e não é chamado por
nenhum workflow. `_esboco_integracao_NAO_USE` levanta `NotImplementedError`
(`validador_resposta_llm.py:218-242`). Na prática, **nada da política de citação é verificado hoje**.

### 7.2 O que passa a ser verificado `[PROJ]`

| # | Verificação | Classe | Camada |
|---|---|---|---|
| V-1 | `retrieved_sources` não vazio ⟹ o texto contém ao menos um `doc_id` recuperado | violação | nova |
| V-2 | Todo `Fonte: X` do texto corresponde a um `doc_id` de `retrieved_sources` | **violação** | nova — ver §7.3 |
| V-3 | `retrieved_sources` vazio ⟹ o texto contém a frase canônica de §5.1 | violação | nova |
| V-4 | Categoria sensível ⟹ ao menos um serviço da rede | violação | regra 3 promovida |
| V-5 | Posologia ⟹ referência a protocolo ou disclaimer | violação | regra 2 promovida |
| V-6 | Ausência total de menção a fonte | aviso | regra 4 promovida |

### 7.3 V-2 é a verificação que falta na política anti-alucinação

Citar `Fonte: protocolo_ms_prenatal.pdf` quando esse `doc_id` não está em `retrieved_sources` é
alucinação de **procedência**: o número pode estar certo, o rótulo pode estar certo, e ainda assim
o texto atribui a afirmação a um documento que não foi consultado.

`POLITICA_ANTI_ALUCINACAO.md` verifica números (camada 2) e rótulo (camada 3), mas **não verifica
procedência**. Essa lacuna está registrada em `CASOS_DE_TESTE_LLM.md` §4.1 (caso LLM-36) e V-2 é a
regra que a fecha. Implementação:

```python
def verificar_procedencia(texto, retrieved_sources) -> list[str]:
    """Devolve doc_ids citados no texto que não foram recuperados."""
    recuperados = {f['doc_id'] for f in retrieved_sources}
    citados = set(re.findall(r'Fonte:\s*`?([^\s,`]+)', texto))
    return sorted(citados - recuperados)
```

Custo: uma regex. Ganho: impede que o sistema invente a autoridade em que se apoia.

---

## 8. Como a citação chega à interface

| Etapa | Responsável | Estado |
|---|---|---|
| Recuperação com metadados | `common.rag_search` | `[COD]` |
| Anexação ao payload (`retrieved_sources`) | `llm_contract.montar_payload` | `[PROJ]` |
| Citação por afirmação no texto | prompt + verificação V-1/V-2 | `[PROJ]` |
| Bloco consolidado | `common.citar_fontes` | `[COD]` |
| Renderização na UI | `lib/ui.py::_render_trace_e_fontes` | `[COD]` |
| Persistência da citação | **nenhuma** | ver §8.1 |

### 8.1 A citação não é persistida

`predicoes_ml` (`ARQUITETURA_ALVO.md` §5.3) registra modelo, versão, hash de features, predição,
método de explicação, `top_features`, `regras_disparadas` e modo. **Não registra quais documentos
foram citados.**

Isso significa que, dada uma linha de auditoria, é possível reconstruir qual modelo decidiu, mas
não em que protocolo a orientação se apoiou. Para uma auditoria clínica retrospectiva, é uma lacuna
real.

A decisão de **não** acrescentar a coluna nesta fase é deliberada: alterar o DDL publicado exigiria
ADR, e o caso de uso (auditoria clínica retrospectiva) está explicitamente fora do escopo acadêmico
declarado em `CONTRATOS_DE_COMPONENTES.md` §8. Fica registrada como limitação, não como
esquecimento — e como candidata natural a `predicoes_ml.fontes_citadas TEXT` numa fase seguinte.

---

## 9. Resumo operacional

| Pergunta | Resposta |
|---|---|
| Conduta sem fonte pode ser entregue? | **Não.** Ou tem `doc_id`, ou tem atribuição a regra do sistema, ou é removida |
| Número do modelo precisa de fonte de protocolo? | Não. Ele tem a própria rastreabilidade |
| E se o RAG não achar nada? | Frase canônica de §5.1, literal |
| E se o RAG falhar? | Mensagem distinta de §5.3, declarando a falha |
| E se a busca precisou sair da categoria? | Cita normalmente, com nota de que a busca foi ampliada |
| Categoria sensível muda alguma coisa? | Sim: exige serviço da rede, além do `doc_id`, e é bloqueante |
| Citar `doc_id` que não foi recuperado? | Violação V-2 — descarte |
| A citação inclui página e ano? | **Não.** Limitação declarada em `METADADOS_DAS_FONTES.md` §6 |

---

## 10. Estado atual

| Item | Estado |
|---|---|
| Frase canônica de cobertura ausente | `[COD]` — existe em `lib/agent.py` |
| `citar_fontes` | `[COD]` — funciona, dedupa por `doc_id` |
| `ValidadorDeterministico` integrado a algum workflow | **Não** |
| V-1, V-2, V-3 implementadas | **Não** |
| Distinção entre "não cobriu" e "falhou" | **Não existe** — hoje seriam a mesma tela |
| Citação persistida em auditoria | **Não** — limitação declarada em §8.1 |
| Taxa de conformidade medida | **Nunca** |
