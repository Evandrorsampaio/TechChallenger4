# Contrato de Entrada e Saída do LLM

**Agente responsável:** `LLMIntegrationAgent`
**Status:** Especificação — **nada implementado**. `lib/ml/llm_contract.py` não existe.
**Fronteira coberta:** camadas 4 (ML), 5 (explicabilidade), 6 (regras) e 7 (RAG) → camada 10 (LLM) → camada 9 (workflow)
**Vinculado a:** `ARQUITETURA_ALVO.md` §5.2 · `DECISOES_ARQUITETURAIS.md` ADR-007 · `CONTRATOS_DE_COMPONENTES.md` §4 e §5

---

> ### Banner de estado
> Este documento **especifica** o contrato. Nenhum payload foi montado, nenhuma síntese foi gerada,
> nenhuma verificação foi executada. Não há métrica de aceitação, taxa de descarte ou exemplo de
> saída real neste arquivo — e não deve haver até que `scripts/run_demo.py` produza saída
> verificável. Os exemplos abaixo são **ilustrativos do formato**, com valores inventados
> deliberadamente genéricos para que não possam ser confundidos com resultado.

---

## 1. O problema que este contrato resolve

Hoje, em `lib/workflows/obstetrico.py:124-144`, quem classifica risco gestacional é o LLM. Ele
recebe `CRITERIOS_ALTO_RISCO` como texto no prompt e devolve um rótulo — sem probabilidade, sem
limiar, sem contribuição por variável e, quando o parse falha, com `default='habitual'`
(`common.llm_json`, linha 49), o que converte falha silenciosa em falso negativo.

A inversão proposta é total: **o LLM deixa de decidir e passa a comunicar**. Os números chegam
prontos, produzidos pelas camadas 4 e 5. O papel do LLM é reunir predição, explicação e protocolo
num texto que o profissional consiga ler em dez segundos — e nada além disso.

Este documento fixa exatamente onde está a fronteira entre "comunicar" e "decidir".

---

## 2. Payload de entrada — forma exata

Reproduzido literalmente de `ARQUITETURA_ALVO.md` §5.2. Esta é a forma normativa; qualquer
divergência entre este bloco e o código é defeito do código.

```json
{
  "model_name": "RandomForestClassifier",
  "model_version": "1.0.0",
  "dataset_version": "v1.0.0",
  "prediction": "alto_risco",
  "threshold": 0.31,
  "probabilities": { "habitual": 0.25, "alto_risco": 0.75 },
  "explanation_method": "shap_tree_explainer",
  "explanation_scope": "local",
  "top_features": [
    { "feature": "has_cronica", "value": true, "contribution": 0.31, "direction": "aumenta" }
  ],
  "dados_imputados": ["hemoglobina_g_dl"],
  "retrieved_sources": [{ "doc_id": "...", "category": "...", "trecho": "..." }],
  "regras_disparadas": [],
  "safety_notice": "Resultado de apoio à decisão. Não substitui avaliação profissional.",
  "aviso_dados_sinteticos": "Modelo treinado em dados sintéticos. Sem validação clínica."
}
```

São **13 campos**, todos obrigatórios na montagem. Nenhum é omitido; campos sem conteúdo são
enviados vazios (`[]`), nunca ausentes — a diferença entre "lista vazia" e "chave ausente" é a
diferença entre "não havia protocolo" e "esquecemos de buscar protocolo", e o LLM precisa
conseguir distinguir as duas.

---

## 3. Esquema campo a campo

Legenda da coluna **Mutável pelo LLM**: `🔒` = imutável, o LLM só pode reproduzir o valor;
`✍️` = o LLM pode parafrasear ou reordenar ao redigir.

| # | Campo | Tipo | Semântica | Proveniência | Mutável pelo LLM |
|---|---|---|---|---|---|
| 1 | `model_name` | `string` | Classe do estimador que produziu a predição. Ex.: `"RandomForestClassifier"` | `ResultadoPredicao.modelo_nome`, lido do `model_card.json` | 🔒 |
| 2 | `model_version` | `string` (semver) | Versão do artefato de modelo | `ResultadoPredicao.modelo_versao` | 🔒 |
| 3 | `dataset_version` | `string` | Versão do dataset de treino. Rastreia qual processo gerador está por trás | `ResultadoPredicao.dataset_versao` | 🔒 |
| 4 | `prediction` | `"habitual"` \| `"alto_risco"` | Rótulo operacional. Vale `"alto_risco"` **se e somente se** `probabilities["alto_risco"] >= threshold` | Camada 4 (`lib/ml/predict.py`) | 🔒 |
| 5 | `threshold` | `number` ∈ [0,1] | Limiar operacional versionado. **Não é 0,5** — é o menor limiar que atinge recall ≥ 0,90 na validação (`DEFINICAO_DO_PROBLEMA.md` §5.1) | `model_card.json` | 🔒 |
| 6 | `probabilities` | `object` com as duas classes | Probabilidades preditas. Soma 1,0 ± 1e-6 | Camada 4 | 🔒 |
| 7 | `explanation_method` | `"shap_tree_explainer"` \| `"contribuicao_linear"` \| `"permutacao"` | Método efetivamente executado pela cascata da ADR-008 | Camada 5 (`lib/ml/explain.py`) | 🔒 |
| 8 | `explanation_scope` | `"local"` \| `"global"` | Escopo da explicação. `"global"` significa que ela descreve o **modelo**, não esta gestante | Camada 5 | 🔒 |
| 9 | `top_features` | `array` de `{feature, value, contribution, direction}` | Contribuições ordenadas por \|contribution\| decrescente. Pode ser `[]` | Camada 5 | 🔒 nos quatro subcampos; ✍️ na tradução do nome técnico para linguagem clínica |
| 10 | `dados_imputados` | `array[string]` | Nomes das features **opcionais** preenchidas pelo `SimpleImputer`. Campo obrigatório nunca aparece aqui | Camadas 3/4 | 🔒 |
| 11 | `retrieved_sources` | `array` de `{doc_id, category, trecho}` | Trechos de protocolo recuperados. Pode ser `[]` | Camada 7 (`common.rag_search`) | ✍️ no `trecho` (pode resumir); 🔒 em `doc_id` e `category` |
| 12 | `regras_disparadas` | `array[string]` | Descrições dos sinais de `SINAIS_ALARME_OBST` detectados. Não vazio ⟹ modo ≠ `normal` | Camada 6 (`obstetrico.SINAIS_ALARME_OBST`) | 🔒 |
| 13 | `safety_notice` | `string` constante | `"Resultado de apoio à decisão. Não substitui avaliação profissional."` | Constante do módulo | 🔒 — reproduzido literalmente |
| 14 | `aviso_dados_sinteticos` | `string` constante | `"Modelo treinado em dados sintéticos. Sem validação clínica."` | Constante do módulo | 🔒 — reproduzido literalmente |

> A numeração vai a 14 porque `safety_notice` e `aviso_dados_sinteticos` são contados
> separadamente; o objeto JSON tem 13 chaves de primeiro nível.

### 3.1 Subcampos de `top_features`

| Subcampo | Tipo | Semântica |
|---|---|---|
| `feature` | `string` | Nome **original** da feature (`has_cronica`), nunca o nome pós-`ColumnTransformer` (`binarias__has_cronica`) |
| `value` | `bool` \| `int` \| `float` \| `string` | Valor observado naquela gestante. Necessário para a explicação fazer sentido: "HAS crônica **presente**" é diferente de "HAS crônica **ausente**" |
| `contribution` | `float` com sinal | Magnitude da contribuição no método declarado em `explanation_method` |
| `direction` | `"aumenta"` \| `"reduz"` | Sentido do efeito sobre a probabilidade de alto risco |

### 3.2 `value` entra no payload, mas **não** na auditoria

Regra do `ARQUITETURA_ALVO.md` §5.3, e é preciso ser explícito porque ela cria uma assimetria
deliberada:

| Destino | `feature` | `value` | `contribution` | `direction` |
|---|---|---|---|---|
| Payload do LLM | ✅ | ✅ | ✅ | ✅ |
| Interface Gradio | ✅ | ✅ | ✅ | ✅ |
| Coluna `predicoes_ml.top_features` | ✅ | **❌** | ✅ | ✅ |

O motivo: `predicoes_ml` já protege os dados clínicos guardando apenas `features_hash`. Persistir
`value` em claro na mesma tabela reintroduziria, por uma porta lateral, exatamente o que o hash
existe para evitar. O payload é efêmero (vive o tempo de uma requisição); a linha de auditoria é
permanente. O tratamento é diferente porque o tempo de vida é diferente.

**Consequência operacional a assumir:** a auditoria permite dizer *quais variáveis pesaram*, não
*com que valores*. Para reconstruir o caso é preciso o prontuário. É um custo aceito e declarado.

---

## 4. Campos imutáveis — a fronteira

**Invariante central (ADR-007, `ARQUITETURA_ALVO.md` §5.2):**

> `prediction`, `probabilities`, `threshold` e `contribution` são gerados **exclusivamente** pela
> camada de ML e pela camada de explicabilidade. O LLM os consome como texto e **não pode
> alterá-los**.

Operacionalizando, a fronteira tem três regras:

1. **Nenhum numeral pode aparecer no texto gerado sem estar presente no payload.** Qualquer
   numeral que não corresponda a um valor do payload dentro da tolerância de arredondamento é
   número inventado, e o texto inteiro é descartado. Ver `POLITICA_ANTI_ALUCINACAO.md` §3.2.
2. **O rótulo mencionado no texto deve ser o de `prediction`.** O LLM não pode escrever
   "risco habitual" quando `prediction == "alto_risco"`, nem suavizar ("risco levemente elevado").
3. **O LLM não recalcula nada.** Não converte probabilidade em percentual arredondado por conta
   própria, não compara probabilidade com um limiar diferente do fornecido, não soma
   contribuições. Todas as formas derivadas de que o texto precisa são pré-computadas e entregues
   prontas — ver §5.3.

O que o LLM **pode** fazer, e é o valor que ele agrega:

- traduzir `has_cronica` para "hipertensão arterial crônica prévia";
- ordenar a narrativa clinicamente em vez de por magnitude de contribuição;
- amarrar a contribuição de uma variável ao trecho de protocolo que a endereça;
- escolher o registro adequado ao público (ver `PROMPTS_DE_EXPLICACAO.md`).

---

## 5. Contrato de saída

### 5.1 A saída é texto, não JSON — e isso é decisão, não preguiça

Pedir JSON ao LLM obrigaria a passar por `common.llm_json`, cujo caminho de falha devolve um
`default` silencioso (linha 49). Reintroduzir esse padrão na camada nova seria repetir
exatamente o defeito que a ADR-002 identifica como justificativa do projeto inteiro.

Além disso, a saída do LLM aqui **não alimenta nenhuma decisão de máquina**. Ela é lida por um
humano. Estrutura sintática rígida não compra nada e custa taxa de falha adicional num modelo de
3B com loops repetitivos documentados (`lib/llm.py:84-88`).

Portanto: **a saída é texto em Markdown, com seções obrigatórias nomeadas.** A verificação é
feita sobre o texto, por regex, e a ausência de uma seção obrigatória é tratada como reprovação —
o que é determinístico e não depende de parse.

### 5.2 Estrutura obrigatória

```
### Estratificação
<1 a 2 frases. Contém o rótulo de `prediction` e a probabilidade da classe predita,
 com o limiar. Nenhum número além destes.>

### Fatores que pesaram
<3 a 5 bullets, um por item de `top_features`, com o nome clínico da variável,
 o valor observado e o sentido (aumenta/reduz). Sem números além dos de `contribution`.>

### Conduta sugerida
<2 a 4 bullets, ancorados nos `retrieved_sources`. Cada conduta com sua fonte.
 Se `retrieved_sources` for vazio: a frase exata de §5.4.>

### Fontes
<`Fonte: <doc_id>, <category>` por linha, uma por doc_id distinto.>

### Avisos
<`safety_notice` e `aviso_dados_sinteticos`, literais.
 Mais o aviso de `dados_imputados`, se não vazio.
 Mais o aviso de escopo global, se `explanation_scope == "global"`.>
```

| Seção | Obrigatória | Verificação associada |
|---|---|---|
| `### Estratificação` | Sempre | Coerência de rótulo (regra 2 da anti-alucinação) |
| `### Fatores que pesaram` | Se `top_features` não vazio | Números conferidos contra `contribution` |
| `### Conduta sugerida` | Sempre | Regra 2 do `ValidadorDeterministico` (posologia sem referência) |
| `### Fontes` | Se `retrieved_sources` não vazio | Regra 4 do `ValidadorDeterministico` (aviso, não bloqueio) |
| `### Avisos` | Sempre | Presença literal das duas constantes — **bloqueante** |

### 5.3 Valores derivados são pré-computados, não calculados pelo LLM

Para que a regra "nenhum numeral fora do payload" seja cumprível, o montador do payload
acrescenta um bloco auxiliar **fora do JSON normativo**, injetado apenas no prompt:

| Derivado | Fórmula | Por que é pré-computado |
|---|---|---|
| Probabilidade em percentual | `round(p * 100, 1)` | Se o LLM converter 0,75 em "75%", o verificador precisa aceitar `75` — mais simples entregar `75.0` pronto e exigir literalidade |
| Distância ao limiar | `p - threshold` | Evita que o LLM subtraia errado e produza um número órfão |
| Faixa de probabilidade | `"baixa" \| "intermediária" \| "alta"`, por corte fixo documentado | Entrega granularidade qualitativa sem inventar uma terceira classe (ADR-003) |

Esses derivados entram na **lista de números justificados** do verificador. Eles não fazem parte
do payload de §2 e não são persistidos.

### 5.4 Quando `retrieved_sources` é vazio

A seção `### Conduta sugerida` deve conter, literalmente:

> Os protocolos disponíveis não cobrem este cenário.

Essa string já existe em `lib/agent.py` (SYSTEM_PROMPT, regra 4 de comportamento) e é reusada sem
reescrita para que o sistema tenha **uma** forma de dizer "não sei", e não duas variantes que a
equipe precise aprender a distinguir. Ver `docs/rag/POLITICA_DE_CITACAO.md` §5.

---

## 6. Pré-condições, pós-condições, invariantes

### 6.1 Pré-condições (garantidas por quem chama `sintetizar`)

| # | Pré-condição | Consequência de violação |
|---|---|---|
| PRE-1 | O payload tem as 13 chaves de §2, sem exceção | `ContratoInvalidoError` — falha de programação, estoura em teste |
| PRE-2 | `sum(probabilities.values()) == 1.0 ± 1e-6` | `ContratoInvalidoError` |
| PRE-3 | `prediction == "alto_risco"` ⟺ `probabilities["alto_risco"] >= threshold` | `ContratoInvalidoError`. É a propriedade que torna o texto verificável |
| PRE-4 | O payload é serializável em JSON sem `NaN` e sem `Infinity` | `ContratoInvalidoError` |
| PRE-5 | A predição e a explicabilidade **já ocorreram**. O payload nunca é montado antes | Violação de ADR-007 na raiz |
| PRE-6 | `explanation_scope == "global"` ⟹ o prompt recebe o aviso obrigatório de escopo | Explicação global apresentada como local é mentira estatística (`CONTRATOS_DE_COMPONENTES.md` §3) |
| PRE-7 | `regras_disparadas` não vazio ⟹ o modo não é `normal` e o prompt é o de bypass | O texto descreveria uma predição que não decidiu nada |
| PRE-8 | Nenhum `trecho` de `retrieved_sources` foi truncado antes da montagem | Truncar é responsabilidade do prompt, não do montador (`CONTRATOS_DE_COMPONENTES.md` §6) |

### 6.2 Pós-condições (garantidas por `sintetizar` + `verificar`)

| # | Pós-condição |
|---|---|
| POS-1 | O texto entregue ao usuário contém `safety_notice` e `aviso_dados_sinteticos` literais, sempre, em todos os modos, inclusive quando o texto do LLM foi descartado |
| POS-2 | O texto entregue não contém nenhum numeral ausente da lista de números justificados |
| POS-3 | O rótulo declarado no texto entregue é exatamente `prediction` |
| POS-4 | `verificar(...).aprovada == False` ⟹ o texto do LLM é **descartado por inteiro** e substituído pela resposta estruturada determinística. Nunca há edição parcial do texto gerado |
| POS-5 | O resultado da verificação (aprovada/reprovada, motivos) é gravado no rastro (`raciocinio`) e contabilizado para a taxa de rejeição |
| POS-6 | `dados_imputados` não vazio ⟹ o texto declara quais campos foram imputados |

### 6.3 Invariantes

| # | Invariante | Como é garantido |
|---|---|---|
| INV-1 | O LLM nunca produz um número que chegue ao usuário sem lastro no payload | Verificação pós-geração + descarte total |
| INV-2 | A verificação é **posterior** à geração e **anterior** à entrega | Nó `validar_resposta_llm` entre `sintetizar_com_llm` e `aplicar_avisos_seguranca` |
| INV-3 | A verificação não faz segunda chamada ao modelo | É regex; custo em microssegundos (ADR-010) |
| INV-4 | Rejeição **não é erro** — é o mecanismo funcionando | A UI mostra a resposta estruturada com nota, não uma mensagem de falha |
| INV-5 | A taxa de rejeição é medida e reportada, nunca suprimida nem "ajustada" afrouxando tolerância | `POLITICA_ANTI_ALUCINACAO.md` §6 |
| INV-6 | O payload é somente-leitura: nenhum campo dele é reescrito depois da geração | O payload é `frozen`/imutável no montador |
| INV-7 | `retrieved_sources == []` é estado **legítimo** e deve ser dito no texto, nunca escondido | §5.4 |

---

## 7. Casos de erro

| ID | Situação | Detecção | Tratamento | Modo de auditoria |
|---|---|---|---|---|
| ERR-LLM-01 | Campo obrigatório ausente na montagem | `ContratoInvalidoError` antes da chamada | Estoura. É defeito de programação, não condição de runtime | — (não chega a auditar) |
| ERR-LLM-02 | `chat_model.invoke` levanta exceção | `try/except` no nó | Tratado **como rejeição**: segue por `usar_resposta_estruturada` | `normal` |
| ERR-LLM-03 | Geração vazia ou só espaços | Verificação de comprimento mínimo | Rejeição | `normal` |
| ERR-LLM-04 | Número órfão no texto | Regra 1 da anti-alucinação | Descarte total do texto | `normal` |
| ERR-LLM-05 | Contradição de rótulo | Regra 2 | Descarte total | `normal` |
| ERR-LLM-06 | Seção obrigatória ausente (`### Avisos`) | Regex de seção | Descarte total | `normal` |
| ERR-LLM-07 | Loop repetitivo (n-grama repetido acima do limite) | Heurística de repetição | Descarte total | `normal` |
| ERR-LLM-08 | Violação do `ValidadorDeterministico` (diagnóstico definitivo, posologia sem referência, categoria sensível sem rede) | Regras 1–3 do validador promovido | Descarte total | `normal` |
| ERR-LLM-09 | Aviso do validador (fonte ausente, tom dirigido à paciente) | Regras 4–5 | **Não bloqueia.** Registra aviso no rastro | `normal` |
| ERR-LLM-10 | Timeout de geração | Limite de tempo no nó | Rejeição + registro | `normal` |

Duas observações sobre esta tabela:

**O modo continua `normal` em quase todos os casos.** Rejeição do texto do LLM não muda o modo de
auditoria, porque a predição de ML aconteceu normalmente. O que muda é o campo do rastro que
registra a substituição. Modo `degradado` é reservado para falha do **modelo de ML**, não do LLM —
distinção que importa porque as duas têm significados clínicos opostos: sem LLM, os números ainda
valem; sem modelo, não há números.

**ERR-LLM-09 é avisos, não violações.** O `ValidadorDeterministico` já faz essa distinção hoje
(`referencias/validador_resposta_llm.py`, listas `violacoes` vs `avisos`) e a promoção para
`lib/validacao.py` preserva a semântica em vez de endurecê-la.

---

## 8. Variação do payload por modo de execução

Nem todos os quatro caminhos de exceção do `ARQUITETURA_ALVO.md` §4 produzem um payload completo.
A obrigatoriedade das 13 chaves se mantém; o que varia é o conteúdo.

| Campo | `normal` | `bypass_regra` | `degradado` | `incompleto` |
|---|---|---|---|---|
| `prediction` | do modelo | `"alto_risco"` por regra, com marcação de origem | da regra determinística | `null` — **não houve predição** |
| `probabilities` | do modelo | `{}` | `{}` | `{}` |
| `threshold` | do `model_card` | `null` | `null` | `null` |
| `explanation_method` | da cascata | `null` | `null` | `null` |
| `explanation_scope` | da cascata | `null` | `null` | `null` |
| `top_features` | preenchido | `[]` | `[]` | `[]` |
| `regras_disparadas` | `[]` | **preenchido** | pode ser vazio | `[]` |
| `dados_imputados` | pode ter itens | `[]` | `[]` | `[]` |
| `retrieved_sources` | do RAG | do RAG | do RAG | do RAG ou `[]` |
| `safety_notice` | ✅ | ✅ | ✅ | ✅ |
| `aviso_dados_sinteticos` | ✅ | ✅ | ✅ | ✅ |

**Regra sem exceção:** os dois avisos estão presentes nos quatro modos. Um caso de emergência que
não passou pelo modelo ainda carrega `aviso_dados_sinteticos`? Sim — porque o texto entregue é
produzido pelo mesmo sistema, e a procedência do sistema não muda conforme o caminho tomado.

**`prediction: null` no modo `incompleto`.** Não existe rótulo. Usar `"habitual"` como sentinela
seria repetir literalmente o defeito de `_avaliar_risco_gestacional`. O prompt correspondente
(variante de dados incompletos, `PROMPTS_DE_EXPLICACAO.md` §6) não recebe rótulo algum e não pode
produzir um.

---

## 9. O que este contrato proíbe

| Proibição | Motivo |
|---|---|
| Recalcular `prediction` a partir de `probabilities` com outro limiar | O limiar é parte do artefato versionado, não escolha do consumidor (`CONTRATOS_DE_COMPONENTES.md` §2) |
| Pedir ao LLM que "revise" ou "corrija" um texto reprovado | Segunda chamada custa 5–10 s e devolve texto igualmente não verificado. A ADR-010 registra a latência como razão de descartar o `ValidadorLLM`; ela vale igualmente aqui |
| Editar parcialmente um texto reprovado (remover o número órfão e entregar o resto) | Se o modelo inventou um número, a confiança no restante do texto também caiu. Descarte é total |
| Omitir `safety_notice` por o texto "já estar longo" | Campo obrigatório sem exceção (`ARQUITETURA_ALVO.md` §8) |
| Afrouxar a tolerância numérica para reduzir a taxa de descarte | Viola o princípio de honestidade metodológica (ADR-007, consequências) |
| Enviar o payload ao LLM antes de a predição existir | Inverteria a ordem que sustenta todo o contrato (PRE-5) |

---

## 10. Assinaturas projetadas

```python
# lib/ml/llm_contract.py  — NÃO IMPLEMENTADO

ModoExecucao = Literal['normal', 'bypass_regra', 'degradado', 'incompleto']


def montar_payload(
    predicao: ResultadoPredicao | None,
    explicacao: ResultadoExplicacao | None,
    fontes: list[dict],
    regras_disparadas: list[str],
    modo: ModoExecucao,
) -> dict:
    """Monta o payload de ARQUITETURA_ALVO.md §5.2.

    Pós-condição: as 13 chaves estão presentes. Campos não aplicáveis ao modo
    recebem None ou [], nunca são omitidos.
    Levanta ContratoInvalidoError se as pré-condições PRE-1..PRE-4 falharem.
    """


def numeros_justificados(payload: dict) -> set[str]:
    """Conjunto canônico de numerais que o texto pode conter.

    Inclui os valores do payload e os derivados pré-computados de §5.3,
    em todas as formas de arredondamento aceitas.
    """


def sintetizar(chat_model, payload: dict, variante: str) -> str:
    """Gera o texto. `variante` seleciona o template de PROMPTS_DE_EXPLICACAO.md.

    Não verifica nada. A verificação é responsabilidade de lib/validacao.py.
    """


def resposta_estruturada(payload: dict) -> str:
    """Renderiza o payload em Markdown, sem LLM.

    É a saída entregue quando o texto do LLM é descartado, e também a saída
    do perfil de execução `ml-only`. Determinística, sempre disponível.
    """
```

`resposta_estruturada` é a peça que torna o descarte viável: **ela precisa ser boa o suficiente
para ser entregue sozinha.** Se a resposta estruturada fosse ilegível, o descarte deixaria de ser
degradação graciosa e viraria falha. Por isso ela é construída primeiro, na ordem de
implementação, e o LLM é o incremento — não o contrário.

---

## 11. Rastreabilidade

| Origem | Item |
|---|---|
| `ARQUITETURA_ALVO.md` §5.2 | Forma do payload, invariante central |
| `ARQUITETURA_ALVO.md` §5.3 | Regra de não persistir `value` |
| `ARQUITETURA_ALVO.md` §8 | Obrigatoriedade dos dois avisos |
| ADR-003 | Duas classes em `probabilities`, não três |
| ADR-007 | Contrato somente-leitura, verificação pós-geração, descarte |
| ADR-008 | `explanation_method` e `explanation_scope` no payload |
| ADR-010 | Validador determinístico promovido; `ValidadorLLM` fora por latência |
| `CONTRATOS_DE_COMPONENTES.md` §4, §5 | Esquema e verificação |
| `lib/agent.py` SYSTEM_PROMPT | Público-alvo, frase de cobertura ausente |
| `lib/workflows/common.py:49` | Falha silenciosa que este contrato existe para não repetir |

---

## 12. Estado atual

| Item | Estado |
|---|---|
| `lib/ml/llm_contract.py` | **Não existe** |
| `lib/validacao.py` | **Não existe** |
| Payload montado alguma vez | **Não** |
| Síntese gerada alguma vez | **Não** |
| Taxa de descarte medida | **Não** — ver `POLITICA_ANTI_ALUCINACAO.md` §6, tabela em branco |
