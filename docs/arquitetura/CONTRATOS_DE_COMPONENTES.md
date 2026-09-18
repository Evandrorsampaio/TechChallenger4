# Contratos entre Componentes

**Agente responsável:** `ArchitectureAgent`
**Status:** Especificação. Exceto onde marcado **`[COD]`**, nada aqui está implementado — as
assinaturas são projetadas, não lidas do repositório.
**Regra de acoplamento:** as camadas conversam por **estrutura de dados**, não por chamada direta
a implementações concretas. Quem produz garante as pós-condições; quem consome garante as
pré-condições.

---

## Índice

| § | Contrato | Fronteira | Status |
|---|---|---|---|
| 1 | `GestanteFeatures` | UI / tool / teste → camada 3 | projetado |
| 2 | `ResultadoPredicao` | camada 4 → camadas 5, 9, 12 | projetado |
| 3 | `ResultadoExplicacao` | camada 5 → camada 10 | projetado |
| 4 | Payload de entrada do LLM | camadas 4+5+6+7 → camada 10 | projetado (formato fixado em `ARQUITETURA_ALVO.md` §5.2) |
| 5 | Saída do LLM e verificação | camada 10 → camada 9 | projetado |
| 6 | Recuperação RAG | camada 7 → camadas 8, 9 | **`[COD]` — existe hoje** |
| 7 | Tool `predizer_risco_gestacional` | camada 8 → camada 4 | projetado |
| 8 | Registro de auditoria | camada 9 → camada 12 | projetado |

---

## 1. `GestanteFeatures` — contrato de entrada do modelo

**Fronteira:** qualquer produtor de dados clínicos → camada 3 (pré-processamento).
**Módulo:** `lib/ml/schema.py` *(novo)*.

### Assinatura projetada

```python
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal

Proteinuria = Literal['ausente', 'traços', '1+', '2+', '3+']


class GestanteFeatures(BaseModel):
    """Contrato de entrada do modelo de risco gestacional (dataset v1.0.0)."""

    model_config = ConfigDict(extra='forbid', frozen=True)

    # --- Obrigatórias (11) ---
    idade:               int   = Field(..., ge=13,   le=50)
    ig_semanas:          int   = Field(..., ge=4,    le=42)
    imc_pre_gestacional: float = Field(..., ge=15.0, le=55.0)
    pas_mmhg:            int   = Field(..., ge=80,   le=200)
    pad_mmhg:            int   = Field(..., ge=50,   le=130)
    gestacoes:           int   = Field(..., ge=1,    le=12)
    partos:              int   = Field(..., ge=0,    le=10)
    abortos:             int   = Field(..., ge=0,    le=6)
    has_cronica:         bool
    diabetes_previo:     bool
    gemelaridade:        bool

    # --- Opcionais (12) — imputadas pelo Pipeline e registradas como imputadas ---
    escolaridade_anos:            int   | None = Field(None, ge=0,   le=20)
    cesareas_previas:             int   | None = Field(None, ge=0,   le=5)
    natimorto_previo:             bool  | None = None
    pre_eclampsia_previa:         bool  | None = None
    intervalo_interpartal_meses:  float | None = Field(None, ge=0,   le=300)
    hemoglobina_g_dl:             float | None = Field(None, ge=5.0, le=16.0)
    glicemia_jejum_mg_dl:         float | None = Field(None, ge=60,  le=200)
    proteinuria_fita:      Proteinuria | None = None
    cardiopatia:                  bool  | None = None
    nefropatia:                   bool  | None = None
    tev_previo:                   bool  | None = None
    tabagismo:                    bool  | None = None
    infeccao_sexual_ativa:        bool  | None = None

    @model_validator(mode='after')
    def _coerencia_obstetrica(self):
        if self.partos + self.abortos > self.gestacoes:
            raise ValueError(
                'Inconsistência obstétrica: partos + abortos não pode exceder gestacoes.'
            )
        return self

    @model_validator(mode='after')
    def _coerencia_pressorica(self):
        if self.pad_mmhg >= self.pas_mmhg:
            raise ValueError('pad_mmhg deve ser menor que pas_mmhg.')
        return self
```

> O `CONTRATO_DE_DADOS.md` §3 lista **24 features**. Aqui são 11 obrigatórias + 13 opcionais = 24.
> `registro_id`, `dataset_version`, `split` e `risco_latente` **não** fazem parte deste contrato:
> são colunas de rastreabilidade do dataset, não entradas de inferência.

### Erros do contrato

```python
class DadosIncompletosError(Exception):
    """Campo obrigatório ausente. Não imputa; devolve a lista de faltantes."""
    campos_faltantes: list[str]

class DominioInvalidoError(Exception):
    """Valor fora da faixa aceita. Carrega campo, valor recebido e faixa."""
```

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | O chamador fornece um dicionário. Nada mais é assumido — nem tipos, nem presença de chaves. |
| **Pós-condições** | Ou uma instância imutável (`frozen=True`) com todos os obrigatórios presentes e todos os valores dentro do domínio; ou uma exceção que **nomeia** o problema. Nunca um objeto parcialmente válido. |
| **Invariantes** | (i) `partos + abortos ≤ gestacoes`; (ii) `pad_mmhg < pas_mmhg`; (iii) campo desconhecido é rejeitado (`extra='forbid'`); (iv) nenhum campo obrigatório é imputado, em nenhuma circunstância. |
| **Erros possíveis** | `DadosIncompletosError` → workflow segue para human-in-the-loop; `ValidationError` do Pydantic (domínio ou tipo) → nó `erro_validacao`, com mensagem por campo; `ValueError` dos validadores cruzados → idem. |

### Por que `extra='forbid'`

Se uma feature for renomeada no gerador e não no schema, com `extra='ignore'` a chave antiga
passaria silenciosamente e o modelo receberia o valor imputado no lugar do medido. `forbid`
transforma um erro silencioso de nomenclatura em falha de validação imediata (Princípio 5).

### Ponte com o banco existente

```python
def features_de_paciente(
    conn: sqlite3.Connection,
    paciente_id: int,
) -> tuple[dict, list[str]]:
    """Monta features parciais a partir de hospital.db.

    Devolve (dados_conhecidos, campos_ausentes). NÃO constrói GestanteFeatures:
    o banco não tem PA, IMC nem comorbidades estruturadas, logo o resultado é
    quase sempre incompleto — e isso é informação, não falha.
    """
```

**Pós-condição relevante:** a função nunca inventa valor. `CONTRATO_DE_DADOS.md` §4 registra que
essa incompletude é o que torna o cenário de demonstração "dados incompletos" genuíno.

---

## 2. `ResultadoPredicao` — saída da camada de ML

**Fronteira:** camada 4 → camadas 5, 9 e 12.
**Módulo:** `lib/ml/predict.py` *(novo)*.

```python
from dataclasses import dataclass
from typing import Literal

Classe = Literal['habitual', 'alto_risco']


@dataclass(frozen=True)
class ResultadoPredicao:
    predicao:         Classe
    probabilidades:   dict[Classe, float]   # soma 1.0 (tolerância 1e-6)
    threshold:        float                 # limiar operacional do model_card
    modelo_nome:      str                   # ex.: 'RandomForestClassifier'
    modelo_versao:    str                   # semver, lido do model_card
    dataset_versao:   str                   # ex.: 'v1.0.0'
    features_hash:    str                   # SHA-256 hex das features canonicalizadas
    dados_imputados:  list[str]             # campos opcionais preenchidos pelo Pipeline
    latencia_ms:      float


def prever(features: GestanteFeatures) -> ResultadoPredicao: ...
```

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | `features` é instância válida de `GestanteFeatures`. Existe artefato carregável cuja `dataset_version` tem a mesma MAJOR do dataset corrente. O `Pipeline` foi ajustado **somente** no split de treino. |
| **Pós-condições** | `sum(probabilidades.values()) == 1.0 ± 1e-6`; `predicao == 'alto_risco'` **se e somente se** `probabilidades['alto_risco'] >= threshold`; `modelo_versao` e `dataset_versao` vêm do `model_card.json`, nunca de literal no código; `features_hash` é determinístico para as mesmas features. |
| **Invariantes** | (i) O mesmo `GestanteFeatures` produz o mesmo `ResultadoPredicao`, exceto `latencia_ms` — verificado por `tests/regression/test_predicao_estavel.py`; (ii) `threshold ≠ 0.5` por decisão de projeto, e o valor efetivo é lido do artefato; (iii) `dados_imputados` lista apenas campos **opcionais** — se um obrigatório aparecer aqui, é defeito grave. |
| **Erros possíveis** | `ModeloIndisponivelError` (artefato ausente, corrompido, ou `dataset_version` de MAJOR incompatível) → workflow entra em `modo_degradado` **declarado**; `ValueError` se `features` não for `GestanteFeatures` (falha de programação, deve estourar). |

**O que este contrato proíbe.** Nenhum consumidor pode recalcular `predicao` a partir de
`probabilidades` com outro limiar. O limiar é parte do artefato versionado, não escolha de quem
chama (`DEFINICAO_DO_PROBLEMA.md` §5.1).

### Canonicalização de `features_hash`

Para o hash ser comparável entre execuções, a serialização precisa ser determinística:

```python
import hashlib, json

def _hash_features(features: GestanteFeatures) -> str:
    canonico = json.dumps(
        features.model_dump(mode='json'),
        sort_keys=True, ensure_ascii=False, separators=(',', ':'),
    )
    return hashlib.sha256(canonico.encode('utf-8')).hexdigest()
```

**Invariante:** duas predições com o mesmo `features_hash` partiram das mesmas entradas. É essa
propriedade que sustenta a auditoria sem armazenar valores clínicos (§8).

---

## 3. `ResultadoExplicacao` — saída da camada de explicabilidade

**Fronteira:** camada 5 → camada 10.
**Módulo:** `lib/ml/explain.py` *(novo)*. Ver **ADR-008**.

```python
from dataclasses import dataclass
from typing import Literal

MetodoExplicacao = Literal[
    'shap_tree',            # TreeExplainer — local e exato
    'contribuicao_linear',  # coef × valor padronizado — local
    'permutacao',           # permutation_importance — GLOBAL, não local
]
Direcao = Literal['aumenta', 'reduz']


@dataclass(frozen=True)
class ContribuicaoFeature:
    feature:      str        # nome ORIGINAL da feature, não o pós-transformação
    value:        object     # valor observado (bool | int | float | str)
    contribution: float      # magnitude com sinal
    direction:    Direcao


@dataclass(frozen=True)
class ResultadoExplicacao:
    metodo:        MetodoExplicacao
    escopo:        Literal['local', 'global']
    top_features:  list[ContribuicaoFeature]   # ordenado por |contribution| desc.
    aviso:         str | None                  # preenchido quando escopo == 'global'


def explicar(pipeline, linha, nomes_features, k: int = 5) -> ResultadoExplicacao: ...
```

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | `pipeline` está ajustado; `linha` é o mesmo `DataFrame` de 1 linha usado na predição; `nomes_features` vem de `get_feature_names_out()` do `ColumnTransformer`. |
| **Pós-condições** | `metodo` sempre preenchido e coerente com o que foi de fato executado; `top_features` ordenado por magnitude decrescente e com no máximo `k` itens; `escopo == 'global'` ⟹ `aviso` não é `None`; nomes remapeados para as features **originais**, não para os nomes gerados pela codificação. |
| **Invariantes** | (i) A explicabilidade **nunca fica indisponível** — a cascata termina sempre em `permutacao`; (ii) `metodo` é propagado ao payload e à auditoria; (iii) a detecção de disponibilidade de `shap` ocorre em tempo de importação, nunca dentro do laço de inferência; (iv) a explicação não altera nada do `ResultadoPredicao`. |
| **Erros possíveis** | Nenhuma exceção sobe. Falha de um método degrada para o próximo da cascata e isso fica registrado em `metodo`. Se até `permutacao` falhar, devolve `top_features=[]` com `aviso` explicando — jamais uma lista inventada. |

### Regra de honestidade

Uma importância por permutação é **global**: descreve o modelo, não aquela paciente. Apresentá-la
como se explicasse o caso individual seria mentira estatística. Por isso `escopo` é campo do
contrato e `aviso` é obrigatório quando ele vale `'global'`; a UI e o prompt do LLM devem
reproduzir esse aviso.

---

## 4. Payload de entrada do LLM

**Fronteira:** camadas 4, 5, 6 e 7 → camada 10.
**Módulo:** `lib/ml/llm_contract.py` *(novo)*. Ver **ADR-007**.

Forma exata, reproduzida de `ARQUITETURA_ALVO.md` §5.2:

```json
{
  "model_name": "RandomForestClassifier",
  "model_version": "1.0.0",
  "dataset_version": "v1.0.0",
  "prediction": "alto_risco",
  "threshold": 0.31,
  "probabilities": { "habitual": 0.25, "alto_risco": 0.75 },
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

### Esquema

| Campo | Tipo | Origem | Obrigatório |
|---|---|---|---|
| `model_name` | string | `ResultadoPredicao.modelo_nome` | sim |
| `model_version` | string (semver) | `ResultadoPredicao.modelo_versao` | sim |
| `dataset_version` | string | `ResultadoPredicao.dataset_versao` | sim |
| `prediction` | `"habitual"` \| `"alto_risco"` | camada 4 | sim |
| `threshold` | number ∈ [0,1] | `model_card.json` | sim |
| `probabilities` | objeto com as duas classes, soma 1 | camada 4 | sim |
| `top_features` | array de `{feature, value, contribution, direction}` | camada 5 | sim (pode ser vazio) |
| `dados_imputados` | array de string | camada 3/4 | sim (pode ser vazio) |
| `retrieved_sources` | array de `{doc_id, category, trecho}` | camada 7 | sim (pode ser vazio) |
| `regras_disparadas` | array de string | camada 6 | sim (pode ser vazio) |
| `safety_notice` | string | constante | sim |
| `aviso_dados_sinteticos` | string | constante | sim |

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | Todos os campos numéricos já foram produzidos pelas camadas 4 e 5. O payload é montado **depois** de predição e explicabilidade, nunca antes. |
| **Pós-condições** | Os 12 campos estão presentes. `safety_notice` e `aviso_dados_sinteticos` nunca são omitidos nem alterados. O payload é serializável em JSON, sem `NaN` e sem `Infinity`. |
| **Invariantes** | (i) **O payload é somente-leitura para o LLM** — `prediction`, `probabilities`, `threshold` e `contribution` só são produzidos pelas camadas 4 e 5; (ii) `retrieved_sources` vazio é estado legítimo (protocolo não encontrado) e deve ser dito no texto, não escondido; (iii) `regras_disparadas` não vazio ⟹ o modo não é `normal`. |
| **Erros possíveis** | `ContratoInvalidoError` se algum campo obrigatório faltar na montagem — falha de programação, deve estourar em teste, nunca em produção. |

### Pendência identificada

A ADR-008 exige que **o método de explicação seja registrado no payload**, mas a forma fixada em
`ARQUITETURA_ALVO.md` §5.2 não tem campo para isso. Duas saídas, ambas compatíveis com o
princípio de aditividade:

| Opção | Efeito |
|---|---|
| **A** — acrescentar `"explanation_method"` e `"explanation_scope"` ao payload | Explícito; exige atualizar §5.2 |
| **B** — carregar o método dentro de cada item de `top_features` | Não muda a forma de §5.2; repete o valor |

Recomendação: **opção A**, com atualização de `ARQUITETURA_ALVO.md` §5.2 por ADR. Registrado como
inconsistência aberta, não resolvido unilateralmente aqui.

---

## 5. Contrato de saída do LLM e verificação anti-alucinação

**Fronteira:** camada 10 → camada 9.
**Módulos:** `lib/ml/llm_contract.py` + `lib/validacao.py` *(novos)*. Ver **ADR-007** e **ADR-010**.

```python
@dataclass(frozen=True)
class ResultadoVerificacao:
    aprovada:            bool
    numeros_nao_justificados: list[str]   # numerais do texto ausentes do payload
    contradicao_rotulo:  bool             # texto afirma rótulo diferente de prediction
    violacoes_clinicas:  list[str]        # do ValidadorDeterministico
    avisos:              list[str]


def sintetizar(chat_model, payload: dict) -> str: ...

def verificar(texto: str, payload: dict,
              tolerancia: float = 0.005) -> ResultadoVerificacao: ...
```

### Regras da verificação

| # | Regra | Efeito |
|---|---|---|
| 1 | Todo numeral do texto deve corresponder a um valor do payload, com tolerância de arredondamento | Número órfão ⟹ `aprovada = False` |
| 2 | O rótulo mencionado no texto deve ser o de `prediction` | Contradição ⟹ `aprovada = False` |
| 3 | Sem diagnóstico definitivo; sem posologia sem referência a protocolo; serviços da rede em categoria sensível; tom dirigido ao profissional | Herdadas de `ValidadorDeterministico` **`[COD]`** |
| 4 | Citação de fonte | **Aviso**, não bloqueio (comportamento atual do validador) |

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | O payload de §4 está completo. O texto é a saída bruta do `chat_model`, sem pós-edição. |
| **Pós-condições** | `aprovada = True` ⟹ o texto entregue não contém número ausente do payload nem contradição de rótulo. `aprovada = False` ⟹ o texto é **descartado** e a resposta estruturada determinística é entregue no lugar (nó `usar_resposta_estruturada`). |
| **Invariantes** | (i) A verificação é **posterior** à geração e **anterior** à entrega; (ii) é implementada por regex — sem segunda chamada ao modelo, custo em microssegundos; (iii) a taxa de rejeição é contabilizada e reportada, nunca suprimida; (iv) rejeição não é erro: é o mecanismo funcionando. |
| **Erros possíveis** | Exceção de geração (`chat_model.invoke` falha) → tratada como rejeição e o fluxo segue por `usar_resposta_estruturada`; malformação do payload → `ContratoInvalidoError` antes da chamada. |

**Nota de calibração honesta.** Com um modelo de 3B, a taxa de descarte pode ser alta. Ela será
**medida e reportada**, não ajustada para parecer melhor (ADR-007, consequência negativa).
Afrouxar a tolerância para reduzir a taxa é violação do Princípio 3.

---

## 6. Contrato de recuperação RAG **`[COD]` — este existe hoje**

**Fronteira:** camada 7 → camadas 8 e 9.
**Módulo:** `lib/workflows/common.py::rag_search`, linhas 63-80. Lido do código, não projetado.

```python
def rag_search(retriever, query: str, categoria: str | None = None,
               k: int = 4) -> list[dict]:
    """Busca no Chroma. Filtra por categoria em pós-processamento."""
```

Forma de cada item devolvido, exatamente como o código a constrói:

```json
{
  "trecho":   "<d.page_content — texto integral do chunk>",
  "doc_id":   "<metadata['doc_id']   ou '?'>",
  "category": "<metadata['category'] ou '?'>",
  "chunk_id": "<metadata['chunk_id'] ou '?'>"
}
```

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | `retriever` expõe `.invoke(query) -> list[Document]`, e cada `Document` tem `.page_content` e `.metadata`. O índice Chroma existe e foi construído pelo notebook 06. |
| **Pós-condições** | Lista com **no máximo** `k` itens, cada um com exatamente as quatro chaves acima. Metadado ausente vira `'?'` — nunca `KeyError`. A ordem preserva o ranqueamento do retriever. |
| **Invariantes** | (i) A busca examina no máximo `docs[:k*2]`; (ii) o filtro por `categoria` é **pós-processado**, comparando `metadata['category']` por igualdade estrita; (iii) a função não lança exceção própria; (iv) nenhuma reescrita do trecho: `trecho` é o `page_content` íntegro. |
| **Erros possíveis** | Exceção de `retriever.invoke` **propaga** — hoje não há tratamento (`ARQUITETURA_ATUAL.md` §12.2). Lista vazia é resultado legítimo, não erro, e ocorre quando nenhum dos `2k` primeiros vizinhos pertence à categoria pedida. |

### Obrigações do consumidor novo

`risco_ml.py::recuperar_protocolos_rag` deve:

1. tratar lista vazia como estado válido e declará-lo no payload (`retrieved_sources: []`) e no
   texto final — "os protocolos recuperados não cobrem este cenário" é resposta aceitável;
2. envolver a chamada de forma que uma falha do Chroma não derrube a predição já calculada — o
   resultado de ML é válido mesmo sem protocolo;
3. **não** truncar `trecho` antes de montar o payload; o truncamento é responsabilidade do prompt.

### Divergência conhecida com a tool equivalente

`tools.buscar_protocolo` (linhas 215-237) devolve as mesmas quatro chaves, mas com default `None`
em vez de `'?'`, e inverte a ordem dos dois primeiros parâmetros. Um consumidor que aceite as duas
origens precisa tolerar `None` **e** `'?'`.

---

## 7. Tool `predizer_risco_gestacional`

**Fronteira:** camada 8 → camada 4.
**Módulo:** `lib/tools.py` *(estendido)* — décima tool da lista devolvida por
`build_langchain_tools`.

```python
class PredizerRiscoGestacionalInput(BaseModel):
    """Entrada da tool. Espelha os 11 campos obrigatórios de GestanteFeatures;
    os 12 opcionais são aceitos e default None."""
    model_config = ConfigDict(extra='forbid')

    idade:               int   = Field(..., ge=13, le=50,   description='Idade em anos')
    ig_semanas:          int   = Field(..., ge=4,  le=42,   description='Idade gestacional em semanas')
    imc_pre_gestacional: float = Field(..., ge=15.0, le=55.0)
    pas_mmhg:            int   = Field(..., ge=80, le=200,  description='Pressão sistólica')
    pad_mmhg:            int   = Field(..., ge=50, le=130,  description='Pressão diastólica')
    gestacoes:           int   = Field(..., ge=1,  le=12)
    partos:              int   = Field(..., ge=0,  le=10)
    abortos:             int   = Field(..., ge=0,  le=6)
    has_cronica:         bool  = Field(..., description='Hipertensão arterial crônica prévia')
    diabetes_previo:     bool
    gemelaridade:        bool
    paciente_id:         int | None = Field(None, description='ID interno, para auditoria')
    # ... campos opcionais de GestanteFeatures, todos default None


def predizer_risco_gestacional(conn, **campos) -> dict:
    """Estima risco gestacional (habitual/alto_risco) com modelo supervisionado.

    Devolve probabilidade, limiar, principais fatores e avisos obrigatórios.
    Registra a predição em predicoes_ml.
    """
```

### Forma da saída

```json
{
  "predicao": "alto_risco",
  "probabilidade": 0.75,
  "threshold": 0.31,
  "modelo": "RandomForestClassifier v1.0.0",
  "principais_fatores": [
    {"feature": "has_cronica", "valor": true, "contribuicao": 0.31, "direcao": "aumenta"}
  ],
  "metodo_explicacao": "shap_tree",
  "dados_imputados": ["hemoglobina_g_dl"],
  "modo": "normal",
  "safety_notice": "Resultado de apoio à decisão. Não substitui avaliação profissional.",
  "aviso_dados_sinteticos": "Modelo treinado em dados sintéticos. Sem validação clínica."
}
```

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | Existe artefato de modelo compatível. A conexão está aberta e `predicoes_ml` existe. `_USUARIO_ATUAL` está definido (default `'sessao_demo'`). |
| **Pós-condições** | Ou um dicionário com as 10 chaves acima **e** uma linha nova em `predicoes_ml`; ou um dicionário `{"erro": ...}` com causa nomeada — nunca exceção subindo ao agente. A tool preserva o padrão das 9 existentes: erro é dado de retorno, não exceção (ver `consultar_prontuario`, `registrar_violencia`). |
| **Invariantes** | (i) Diferentemente das 9 tools atuais, esta **tem** `args_schema` — a tool 9 (`buscar_protocolo`) é o contraexemplo a não repetir; (ii) a tool não reimplementa inferência: delega a `lib/ml/predict.py`, que é o ponto único (ADR-012); (iii) toda chamada audita, inclusive as que terminam em erro de validação; (iv) os dois avisos são sempre devolvidos. |
| **Erros possíveis** | `{'erro': 'dados_incompletos', 'campos_faltantes': [...]}`; `{'erro': 'dominio_invalido', 'campo': ..., 'valor': ..., 'faixa': ...}`; `{'erro': 'modelo_indisponivel', 'modo': 'degradado', ...}` acompanhado do resultado da regra determinística. |

### Riscos de tool calling com modelo de 3B

Onze parâmetros obrigatórios são muitos para um modelo pequeno preencher corretamente. Duas
mitigações de projeto:

1. `description` clínica curta em cada campo, para reduzir ambiguidade;
2. o caminho primário de uso é a **aba dedicada da UI**, com formulário — a tool existe para
   integração com o agente ReAct, não como via principal.

---

## 8. Contrato do registro de auditoria

**Fronteira:** camada 9 → camada 12.
**Destino:** tabela `predicoes_ml` (DDL em `ARQUITETURA_ALVO.md` §5.3).

```python
@dataclass(frozen=True)
class RegistroAuditoria:
    usuario:           str
    paciente_id:       int | None
    modelo_nome:       str
    modelo_versao:     str
    dataset_versao:    str
    features_hash:     str            # SHA-256; NUNCA os valores
    predicao:          str
    probabilidade:     float
    threshold:         float
    top_features:      str            # JSON serializado
    regras_disparadas: str            # JSON serializado
    modo:              Literal['normal', 'degradado', 'bypass_regra', 'incompleto']


def auditar(conn, registro: RegistroAuditoria) -> int:
    """INSERT em predicoes_ml. Devolve o id gerado."""
```

### Semântica de `modo`

| Valor | Quando | `probabilidade` | `regras_disparadas` |
|---|---|---|---|
| `normal` | ML executou; texto do LLM aprovado ou substituído pela resposta estruturada | do modelo | vazio |
| `bypass_regra` | Sinal de alarme obstétrico detectado; ML não consultado | convenção documentada para "não aplicável" | não vazio |
| `degradado` | Modelo indisponível; resultado veio da regra determinística | idem | pode ser vazio |
| `incompleto` | Campo obrigatório ausente; nenhuma predição emitida | idem | vazio |

> **Pendência.** A coluna `probabilidade` é `REAL NOT NULL` na DDL, mas em três dos quatro modos
> não existe probabilidade de modelo. É preciso decidir entre (a) tornar a coluna anulável —
> alteração da DDL de `ARQUITETURA_ALVO.md` §5.3 — ou (b) fixar um sentinela documentado
> (por exemplo `-1.0`). A opção (a) é mais honesta; a (b) preserva a DDL já publicada. Registrado
> como inconsistência aberta, a resolver por ADR antes da implementação.

| Aspecto | Especificação |
|---|---|
| **Pré-condições** | A predição (ou a decisão de não predizer) já ocorreu. `predicoes_ml` existe. |
| **Pós-condições** | Exatamente **uma** linha por invocação do workflow que chegue a `compilar_resposta`, em qualquer modo. O `id` devolvido permite correlacionar com o log estruturado. |
| **Invariantes** | (i) **Nenhum valor clínico é gravado** — só o hash; (ii) `modelo_versao` e `dataset_versao` vêm do `model_card.json`; (iii) o registro é gravado **antes** da resposta chegar à UI, para que uma falha de renderização não apague o rastro; (iv) o registro é imutável — não há `UPDATE` nem `DELETE` no caminho da aplicação. |
| **Erros possíveis** | Falha de `INSERT` (banco somente leitura, disco cheio) **não pode** ser silenciada: registra erro crítico no log estruturado e marca a resposta como não auditada. Uma predição entregue sem rastro é violação do Princípio 4 e precisa ser visível. |

### Por que hash e não valores

`features_hash` prova que duas predições partiram das mesmas entradas — o suficiente para
reprodutibilidade e para investigar inconsistência — **sem** criar uma segunda cópia de dados
clínicos sensíveis fora do prontuário. Ver `ARQUITETURA_ALVO.md` §5.3 e
`ESTRATEGIA_DE_SEGURANCA.md`.

O custo é assumido e declarado: não é possível reconstruir as entradas a partir do registro. Para
auditoria clínica retrospectiva isso seria insuficiente; para este escopo acadêmico, o
compromisso privacidade × rastreabilidade pende para a privacidade.

---

## 9. Matriz de contratos por caminho de execução

Quais contratos são atravessados em cada modo:

| Caminho | §1 | §2 | §3 | §4 | §5 | §6 | §8 |
|---|---|---|---|---|---|---|---|
| Predição normal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (`normal`) |
| Dados incompletos | ❌ erro | — | — | — | — | — | ✅ (`incompleto`) |
| Emergência (bypass) | ✅ | — | — | ✅ parcial | ✅ | ✅ | ✅ (`bypass_regra`) |
| Modelo indisponível | ✅ | ❌ erro | — | ✅ parcial | ✅ | ✅ | ✅ (`degradado`) |
| LLM rejeitado | ✅ | ✅ | ✅ | ✅ | ❌ rejeita | ✅ | ✅ (`normal`) |
| Consulta livre (ReAct) | — | — | — | — | — | ✅ | — |

"§4 parcial" significa payload montado sem `probabilities` nem `top_features`, com
`regras_disparadas` preenchido e os dois avisos presentes — a obrigatoriedade de
`safety_notice` e `aviso_dados_sinteticos` não tem exceção.

A última linha registra um fato importante: o fluxo de consulta livre com o agente ReAct, que é o
fluxo existente, **não atravessa nenhum dos contratos novos** — exceto quando o agente decide
chamar a tool de §7. A evolução não altera o caminho já entregue.
