# Contrato de Dados — Risco Gestacional

**Agente responsável:** `DataEngineeringAgent`
**Status:** Especificação aprovada — dataset **ainda não gerado**
**Versão do contrato:** `v1.0.0`

---

## 1. Declaração de ausência (obrigatória)

Antes de qualquer proposta, a constatação que motiva este documento:

> **Não existe, neste projeto, dataset tabular adequado para treinamento supervisionado
> de modelos tradicionais de Machine Learning.**

Evidências, todas confirmadas por leitura de código:

| Candidato | Por que não serve |
|---|---|
| `sft_train.jsonl` (dataset SFT) | Registros no formato `{messages: [system, user, assistant], category, sensitive, source_doc}`. São pares de conversa em texto. `category` e `sensitive` são metadados de origem documental, não features clínicas de uma paciente. Não há matriz de features nem variável alvo. |
| `hospital.db` | 50 pacientes. O schema (`lib/db.py:31-103`) tem cadastro, prontuário ginecológico descritivo, exames com resultado em **texto livre** (`'BI-RADS 2 (achados benignos)'`), ciclos menstruais, registros de violência e bula de medicamentos. **Nenhuma variável alvo. Nenhum sinal vital. Nenhum resultado laboratorial numérico. Nenhuma comorbidade estruturada. Nenhum desfecho.** n=50 é ordens de grandeza abaixo do necessário. |
| `fontes_saude_mulher_v2.json` | Texto de protocolos em PDF. Insumo de RAG. |
| `files/chroma/` | Índice vetorial. |

O prompt mestre (§5.4) prevê exatamente este caso e determina o procedimento: declarar a ausência,
propor dataset sintético controlado, documentar que é demonstrativo, tornar as regras de rotulagem
transparentes, explicar as limitações e **não apresentar resultado sintético como validação
clínica**. É o que os documentos desta pasta fazem.

---

## 2. Identificação do dataset proposto

| Campo | Valor |
|---|---|
| Nome | `risco_gestacional_sintetico` |
| Versão | `v1.0.0` |
| Natureza | **SINTÉTICO** — gerado programaticamente. Zero dados de pessoas reais. |
| Gerador | `lib/ml/dataset.py` (a implementar) |
| Comando | `python scripts/train.py --gerar-dataset` |
| Semente | `42` (fixa; regeneração é bit-a-bit idêntica) |
| Volume | 8 000 registros |
| Formato | Parquet (`artifacts/data/risco_gestacional_v1.parquet`) + manifesto JSON com SHA-256 |
| Unidade | Uma gestação avaliada num ponto do pré-natal |
| Licença/origem | Não aplicável — sem procedência externa |

### Classificação de natureza dos dados (exigida pelo prompt mestre §5.4)

| Categoria | Presente neste dataset? |
|---|---|
| Dados **reais** de pacientes | **Não.** Nenhum. |
| Dados **sintéticos** (gerados por processo estatístico definido por nós) | **Sim — 100 % do dataset.** |
| Dados **simulados** a partir de distribuições reais publicadas | **Não.** As distribuições marginais são *plausíveis* segundo literatura e protocolos MS/FEBRASGO, mas **não foram ajustadas a nenhuma coorte real**. |

Essa terceira linha é importante e costuma ser omitida: as faixas de valores (ex.: PAS entre 90 e
180 mmHg) são clinicamente plausíveis, mas as **frequências** com que ocorrem foram escolhidas por
nós para produzir um problema de aprendizado interessante — não medidas em população brasileira.

---

## 3. Esquema do dataset

**24 features + 1 alvo** (4 demográficas/antropométricas + 7 de história obstétrica + 5 de sinais
vitais e laboratório + 8 de comorbidades e exposições). Tipagem, faixas e semântica completas em
`docs/dados/DICIONARIO_DE_DADOS.md`.

### 3.1 Demográficas e antropométricas

| Coluna | Tipo | Domínio | Obrigatória na inferência |
|---|---|---|---|
| `idade` | int | 13–50 | **Sim** |
| `imc_pre_gestacional` | float | 15,0–55,0 | **Sim** |
| `escolaridade_anos` | int | 0–20 | Não |
| `ig_semanas` | int | 4–42 | **Sim** |

### 3.2 História obstétrica

| Coluna | Tipo | Domínio | Obrigatória |
|---|---|---|---|
| `gestacoes` | int | 1–12 | **Sim** |
| `partos` | int | 0–10 | **Sim** |
| `abortos` | int | 0–6 | **Sim** |
| `cesareas_previas` | int | 0–5 | Não |
| `natimorto_previo` | bool | 0/1 | Não |
| `pre_eclampsia_previa` | bool | 0/1 | Não |
| `intervalo_interpartal_meses` | float | 0–300, nulo se nulípara | Não |

### 3.3 Sinais vitais e laboratório

| Coluna | Tipo | Domínio | Obrigatória |
|---|---|---|---|
| `pas_mmhg` | int | 80–200 | **Sim** |
| `pad_mmhg` | int | 50–130 | **Sim** |
| `hemoglobina_g_dl` | float | 5,0–16,0 | Não |
| `glicemia_jejum_mg_dl` | float | 60–200 | Não |
| `proteinuria_fita` | ordinal | `ausente` \| `traços` \| `1+` \| `2+` \| `3+` | Não |

### 3.4 Comorbidades e exposições

| Coluna | Tipo | Domínio | Obrigatória |
|---|---|---|---|
| `has_cronica` | bool | 0/1 | **Sim** |
| `diabetes_previo` | bool | 0/1 | **Sim** |
| `cardiopatia` | bool | 0/1 | Não |
| `nefropatia` | bool | 0/1 | Não |
| `tev_previo` | bool | 0/1 | Não |
| `gemelaridade` | bool | 0/1 | **Sim** |
| `tabagismo` | bool | 0/1 | Não |
| `infeccao_sexual_ativa` | bool | 0/1 (HIV, sífilis ou hepatite em atividade) | Não |

### 3.5 Variável alvo

| Coluna | Tipo | Domínio | Prevalência-alvo |
|---|---|---|---|
| `alto_risco` | bool | 0/1 | ≈ 0,22 |

### 3.6 Colunas de rastreabilidade (não são features)

| Coluna | Uso |
|---|---|
| `registro_id` | UUID determinístico por registro |
| `dataset_version` | `v1.0.0` |
| `split` | `treino` \| `validacao` \| `teste` |
| `risco_latente` | Probabilidade real do processo gerador. **Excluída do treino.** Serve apenas para auditoria do gerador e para calcular o teto teórico de desempenho (erro de Bayes). |

> `risco_latente` é a variável mais perigosa do dataset: incluí-la como feature causaria vazamento
> total. O carregador em `lib/ml/dataset.py` a remove explicitamente, e o teste
> `tests/unit/test_dataset_sem_vazamento.py` falha se ela aparecer na matriz de features.

---

## 4. Alinhamento com `hospital.db`

O dataset sintético **não substitui** o banco existente; eles coexistem com papéis distintos.

| | `hospital.db` | `risco_gestacional_sintetico` |
|---|---|---|
| Papel | Prontuário de demonstração; alimenta tools e UI | Treinamento e avaliação do modelo |
| Volume | 50 pacientes | 8 000 gestações |
| Tem alvo? | Não | Sim |

**Ponte entre os dois:** para a demonstração ponta a ponta, o módulo
`lib/ml/schema.py` oferece `features_de_paciente(conn, paciente_id)`, que monta um
`GestanteFeatures` parcial a partir do prontuário real da paciente no `hospital.db` e **declara
explicitamente quais campos ficaram ausentes**. Os campos que o banco não possui (PA, IMC,
comorbidades) são os que disparam o caminho de dados incompletos no workflow — o que, por acaso,
torna o cenário de demonstração "dados incompletos" genuíno em vez de encenado.

**Decisão explícita:** o schema de `hospital.db` **não será alterado** para acomodar as features
de ML. Adicionar colunas de sinais vitais ao prontuário mock tornaria o banco inconsistente com os
notebooks 05/07/10 já escritos. A única alteração ao banco é **aditiva**: uma nova tabela
`predicoes_ml` para auditoria (ver `docs/seguranca/POLITICA_DE_AUDITORIA.md`).

---

## 5. Contrato de entrada em inferência

Em produção o modelo não recebe um DataFrame; recebe um objeto validado.

```python
# lib/ml/schema.py  (a implementar)
class GestanteFeatures(BaseModel):
    idade: int = Field(..., ge=13, le=50)
    ig_semanas: int = Field(..., ge=4, le=42)
    imc_pre_gestacional: float = Field(..., ge=15.0, le=55.0)
    pas_mmhg: int = Field(..., ge=80, le=200)
    pad_mmhg: int = Field(..., ge=50, le=130)
    gestacoes: int = Field(..., ge=1, le=12)
    partos: int = Field(..., ge=0, le=10)
    abortos: int = Field(..., ge=0, le=6)
    has_cronica: bool
    diabetes_previo: bool
    gemelaridade: bool
    # ... campos opcionais com default None
```

### Regras do contrato

| Regra | Comportamento |
|---|---|
| Campo obrigatório ausente | **Não imputa.** Devolve `DadosIncompletosError` listando os campos faltantes. O workflow encaminha ao caminho human-in-the-loop. |
| Campo opcional ausente | Imputado pelo `Pipeline` (mediana para numérico, categoria `desconhecido` para categórico) e **registrado na auditoria** como imputado. |
| Valor fora do domínio | Rejeitado pelo Pydantic com mensagem clara indicando campo, valor e faixa aceita. |
| `partos + abortos > gestacoes` | Rejeitado por validador cruzado — inconsistência obstétrica. |
| `pad_mmhg >= pas_mmhg` | Rejeitado por validador cruzado. |
| Campo desconhecido no payload | Rejeitado (`model_config = ConfigDict(extra='forbid')`) — impede que uma feature renomeada passe silenciosamente. |

A recusa em imputar campos obrigatórios é deliberada. Imputar a pressão arterial de uma gestante
pela mediana da população e devolver uma probabilidade como se fosse medida é precisamente o tipo
de silêncio perigoso que este sistema deve evitar.

---

## 6. Versionamento

| Artefato | Estratégia |
|---|---|
| Código do gerador | Versionado no git (`lib/ml/dataset.py`) |
| Dataset gerado | **Não versionado** no git (Parquet binário). Regenerável de forma determinística pela semente. |
| Manifesto | `artifacts/data/risco_gestacional_v1.manifest.json` — **versionado** — contém SHA-256 do Parquet, semente, versão do contrato, timestamp, contagem por classe e por split, e versão do gerador |
| Compatibilidade | Mudança em feature, domínio ou processo de rotulagem ⇒ **incremento de MAJOR** e novo treinamento. Modelos registram a `dataset_version` que os treinou; carregar um modelo com dataset de MAJOR diferente emite erro. |

O manifesto versionado é o que torna a afirmação "o dataset é reprodutível" verificável em vez de
declarativa: `scripts/train.py --verificar-dataset` recomputa o hash e compara.

---

## 7. Documentos relacionados

| Documento | Conteúdo |
|---|---|
| `DICIONARIO_DE_DADOS.md` | Semântica, unidade, faixa e distribuição de cada variável |
| `ESTRATEGIA_DE_ROTULAGEM.md` | Processo gerador do rótulo, em detalhe reproduzível |
| `QUALIDADE_DOS_DADOS.md` | Perfilamento, ausências, inconsistências, desbalanceamento |
| `ESTRATEGIA_TREINO_TESTE.md` | Divisão, estratificação, validação cruzada |
| `RISCOS_DE_VAZAMENTO.md` | Mapa de vazamentos e controles |
