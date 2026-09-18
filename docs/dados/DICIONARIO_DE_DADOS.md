# Dicionário de Dados — `risco_gestacional_sintetico` v1.0.0

**Agente responsável:** `DataEngineeringAgent`
**Status:** Especificação normativa — **dataset ainda não gerado, nenhuma estatística medida**
**Contrato de referência:** `docs/dados/CONTRATO_DE_DADOS.md` (v1.0.0)
**Rotulagem de referência:** `docs/dados/ESTRATEGIA_DE_ROTULAGEM.md`
**Implementação alvo:** `lib/ml/dataset.py`, `lib/ml/schema.py`, `lib/ml/features.py`

---

## 0. Como ler este documento

> **Nenhum número deste documento é um resultado.** Tudo o que aparece aqui é **especificação de
> projeto**: as faixas, as distribuições geradoras e as taxas de ausência são *parâmetros que nós
> escolhemos* e que `lib/ml/dataset.py` deverá implementar. Não são estatísticas medidas em dado
> algum, nem foram estimadas a partir de coorte real.
>
> As estatísticas **observadas** (médias, contagens, prevalência efetiva, taxa de ausência real)
> serão registradas em `docs/dados/QUALIDADE_DOS_DADOS.md` **depois** da geração, a partir de
> `artifacts/data/risco_gestacional_v1.manifest.json`.

Classificação usada nas colunas:

| Marcador | Significado |
|---|---|
| `[ESPEC]` | Parâmetro de projeto definido por nós. Vinculante para a implementação. |
| `[DERIV]` | Derivado de outra coluna durante a geração. |
| `[PEND]` | A ser medido após a geração. Nunca preenchido por estimativa. |

---

## 1. Pendência de contrato PC-01 — **Resolvida (ciclo 1, planejamento)**

**Decisão:** `N_FEATURES = 24`. Fonte de verdade: enumeração explícita das subseções §3.1–3.4
do contrato (e deste dicionário). O texto “23 variáveis” em versões anteriores de
`DEFINICAO_DO_PROBLEMA.md` era erro de contagem, não uma feature a remover.

> Histórico: chegou a haver menção a **"23 features + 1 alvo"** contra a enumeração de
> **24 colunas de feature**:
>
> | Subseção | Colunas enumeradas | Contagem |
> |---|---|---|
> | §3.1 Demográficas e antropométricas | `idade`, `imc_pre_gestacional`, `escolaridade_anos`, `ig_semanas` | 4 |
> | §3.2 História obstétrica | `gestacoes`, `partos`, `abortos`, `cesareas_previas`, `natimorto_previo`, `pre_eclampsia_previa`, `intervalo_interpartal_meses` | 7 |
> | §3.3 Sinais vitais e laboratório | `pas_mmhg`, `pad_mmhg`, `hemoglobina_g_dl`, `glicemia_jejum_mg_dl`, `proteinuria_fita` | 5 |
> | §3.4 Comorbidades e exposições | `has_cronica`, `diabetes_previo`, `cardiopatia`, `nefropatia`, `tev_previo`, `gemelaridade`, `tabagismo`, `infeccao_sexual_ativa` | 8 |
> | **Total** | | **24** |

**Encaminhamento residual (código, Sprint 2):** `lib/ml/schema.py` deve expor `N_FEATURES = 24` e
o teste `tests/unit/test_schema_gestante.py` deve assertar `len(FEATURES) == N_FEATURES`.
Remover `escolaridade_anos` **não** está autorizado — seria mudança de contrato MAJOR.

---

## 2. Visão geral das colunas

| Grupo | Colunas | É feature? | Entra na matriz de treino? |
|---|---|---|---|
| Demográficas/antropométricas | 4 | Sim | Sim |
| História obstétrica | 7 | Sim | Sim |
| Sinais vitais e laboratório | 5 | Sim | Sim |
| Comorbidades e exposições | 8 | Sim | Sim |
| Alvo | `alto_risco` | Não (é `y`) | Como rótulo |
| Rastreabilidade | `registro_id`, `dataset_version`, `split`, `risco_latente` | **Não** | **Nunca** |

**Total de colunas no Parquet:** 24 features + 1 alvo + 4 de rastreabilidade = **29 colunas**.

---

## 3. Features demográficas e antropométricas

### 3.1 `idade`

| Atributo | Valor |
|---|---|
| Tipo | `int` (inteiro, anos completos) |
| Unidade | anos |
| Domínio / faixa | 13–50 (validado por Pydantic `ge=13, le=50`) |
| Distribuição geradora planejada `[ESPEC]` | Normal truncada **μ = 27, σ = 6**, truncada em [13, 50], arredondada para inteiro |
| Semântica clínica | Idade materna na data da consulta de pré-natal |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum — sempre presente |
| Papel na rotulagem | Entra duas vezes: termo `idade < 16` (β = +1,15) e termo `(idade − 28)/10` **apenas para idade ≥ 28** (β = +0,40). Participa da interação `idade ≥ 35 × has_cronica` (β = +0,80) |
| Tratamento no pipeline | Numérica. `StandardScaler`. Sem imputação (nunca ausente). Sem discretização — a dicotomização por corte é característica do baseline determinístico, não dos modelos de ML |
| Observações | A forma em "banheira" do risco por idade (extremos jovem e tardio) é imposta **explicitamente** pelo modelo latente, não emerge dos dados. A Regressão Logística só a captura porque os dois termos já entram separados na geração; um modelo linear sobre `idade` crua não a recuperaria. Isso é uma limitação declarada, ver `LIMITACOES_DO_MODELO.md` |

### 3.2 `imc_pre_gestacional`

| Atributo | Valor |
|---|---|
| Tipo | `float` |
| Unidade | kg/m² |
| Domínio / faixa | 15,0–55,0 |
| Distribuição geradora planejada `[ESPEC]` | Normal truncada **μ = 26,0, σ = 5,0** em [15,0; 55,0], arredondada a 1 casa decimal |
| Semântica clínica | Índice de massa corporal aferido **antes** da gestação (ou no 1º trimestre), base para a curva de ganho ponderal do pré-natal |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | Termo contínuo `(imc − 24)/5` (β = +0,34); participa da interação `imc ≥ 30 × diabetes_previo` (β = +0,70) |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | Gerado com **correlação positiva moderada imposta** com `diabetes_previo` (ver §6.2). A dependência é nossa decisão de projeto, não uma correlação medida |

### 3.3 `escolaridade_anos`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | anos de estudo formal concluídos |
| Domínio / faixa | 0–20 |
| Distribuição geradora planejada `[ESPEC]` | Normal truncada **μ = 10, σ = 3,5** em [0, 20], arredondada |
| Semântica clínica | Proxy socioeconômico. Não é fator causal — é marcador de acesso a serviços e a informação |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | **MCAR, 20 %** — campo administrativo frequentemente vazio |
| Papel na rotulagem | β = **−0,04** por ano. É o menor coeficiente absoluto do modelo; efeito deliberadamente fraco |
| Tratamento no pipeline | Numérica. `SimpleImputer(strategy='median')` → `StandardScaler`. Presença de imputação registrada em `dados_imputados` no payload |
| Observações | Efeito pequeno (β = −0,04). Nenhum modelo tem obrigação de recuperá-lo — um dataset em que toda feature é fortemente preditiva não exercita seleção de variáveis. **Não será removida** (PC-01 fechada com 24 colunas). |

### 3.4 `ig_semanas`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | semanas de gestação |
| Domínio / faixa | 4–42 |
| Distribuição geradora planejada `[ESPEC]` | Mistura por trimestre: 1º trimestre (4–13 sem) com peso **0,30**; 2º (14–27) com peso **0,40**; 3º (28–42) com peso **0,30**; uniforme discreta dentro de cada faixa |
| Semântica clínica | Idade gestacional no momento da avaliação. Define a rotina de exames (`obstetrico.py:219-273`) e a periodicidade de consultas (`obstetrico.py:276-317`) |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | **β = 0 — não entra no escore latente.** É deliberado: a IG define *conduta*, não *risco basal*. Ver observações |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | Esta é a variável mais importante para a **análise de subgrupo** (`METRICAS_E_RESULTADOS.md` §9) precisamente porque o gerador não lhe atribui efeito: se o modelo apresentar desempenho desigual por faixa de IG, isso é **artefato de amostragem ou do modelo**, não sinal do processo gerador. Ela funciona como um controle negativo embutido. Além disso, `ig_semanas` **é** determinante do mecanismo MAR de `proteinuria_fita` (§5.5) — ou seja, afeta a *observabilidade* de outra feature sem afetar o rótulo diretamente |

---

## 4. Features de história obstétrica

### 4.1 `gestacoes`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | contagem |
| Domínio / faixa | 1–12 |
| Distribuição geradora planejada `[ESPEC]` | `1 + Poisson(λ = 0,9)`, truncado em 12 |
| Semântica clínica | Número total de gestações **incluindo a atual** (o "G" do `G_P_A`) |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | β = 0 diretamente; atua como base para `partos`, `abortos` e `cesareas_previas`, que entram |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | O mínimo é 1 porque a gestação avaliada já conta. Isso torna `gestacoes = 0` impossível por construção e por validação — relevante para o mapeamento de `hospital.db` (§8.2), onde `G0` ocorre |

### 4.2 `partos`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | contagem |
| Domínio / faixa | 0–10 |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | `Binomial(n = gestacoes − 1 − abortos, p = 0,88)`, truncado em 10 |
| Semântica clínica | Partos anteriores (qualquer via), o "P" do `G_P_A` |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | β = 0 diretamente; determina a aplicabilidade de `intervalo_interpartal_meses` e a possibilidade de `natimorto_previo` / `pre_eclampsia_previa` / `cesareas_previas` |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | A derivação a partir de `gestacoes − 1 − abortos` **garante por construção** o invariante `partos + abortos ≤ gestacoes` exigido pelo validador cruzado do contrato (§5). O invariante não é verificado *a posteriori* e corrigido — ele é impossível de violar pelo desenho da amostragem. `tests/unit/test_qualidade_dataset.py` assere mesmo assim, porque um invariante garantido por construção continua valendo a pena testar: ele protege contra regressão na refatoração do gerador |

### 4.3 `abortos`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | contagem |
| Domínio / faixa | 0–6 |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | `Binomial(n = gestacoes − 1, p = 0,15)`, truncado em 6 |
| Semântica clínica | Abortamentos anteriores, espontâneos ou provocados, o "A" do `G_P_A` |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | Indicador `abortos ≥ 2` (β = +0,75) — abortamento de repetição |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | O gerador usa a variável **contínua** (contagem), mas o rótulo só depende do **indicador ≥ 2**. Modelos lineares sobre a contagem crua terão que aproximar um degrau com uma reta — fonte legítima de erro do LogReg que o Random Forest pode reduzir. É parte do desenho que torna a comparação entre os dois informativa |

### 4.4 `cesareas_previas`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | contagem |
| Domínio / faixa | 0–5 |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | `Binomial(n = partos, p = 0,42)`, truncado em 5 |
| Semântica clínica | Cesarianas anteriores. ≥ 2 contraindica indução e eleva risco de acretismo e rotura |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | Nenhum (sempre gerada; zero é valor válido, não ausência) |
| Papel na rotulagem | Indicador `cesareas_previas ≥ 2` (β = +0,60) |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | `cesareas_previas ≤ partos` é garantido por construção e verificado por teste de consistência cruzada |

### 4.5 `natimorto_previo`

| Atributo | Valor |
|---|---|
| Tipo | `bool` (armazenado como 0/1) |
| Unidade | — |
| Domínio / faixa | {0, 1} |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | `Bernoulli(0,03)` **se `partos ≥ 1`**; `0` determinístico se `partos == 0` |
| Semântica clínica | Antecedente de óbito fetal ≥ 20 semanas ou ≥ 500 g |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | β = +1,10 |
| Tratamento no pipeline | Binária. Passa direto (`passthrough`), sem escalonamento |
| Observações | A condicionalidade em `partos ≥ 1` é uma restrição lógica: não se pode ter natimorto prévio sem parto prévio. Verificada por teste de consistência cruzada |

### 4.6 `pre_eclampsia_previa`

| Atributo | Valor |
|---|---|
| Tipo | `bool` |
| Unidade | — |
| Domínio / faixa | {0, 1} |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | `Bernoulli(0,06)` **se `partos ≥ 1`**; `0` se `partos == 0` |
| Semântica clínica | Pré-eclâmpsia em gestação anterior |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | **β = +1,70 — o maior coeficiente entre os fatores de antecedente**, coerente com a literatura que aponta recorrência como o preditor isolado mais forte de pré-eclâmpsia |
| Tratamento no pipeline | Binária. `passthrough` |
| Observações | É a feature que se espera ver no topo das explicações locais sempre que estiver presente. **Essa expectativa não é um resultado** — é uma consequência aritmética do β que escolhemos, e serve como *verificação de sanidade do explicador*: se o SHAP de um caso com `pre_eclampsia_previa = 1` **não** a destacar, a suspeita recai sobre o explicador ou sobre o treino, não sobre a clínica. Registrado como checagem em `EXPLICABILIDADE.md` §6 |

### 4.7 `intervalo_interpartal_meses`

| Atributo | Valor |
|---|---|
| Tipo | `float` (nulo permitido) |
| Unidade | meses |
| Domínio / faixa | 0–300; **nulo estrutural se `partos == 0`** |
| Distribuição geradora planejada `[ESPEC]` `[DERIV]` | Se `partos ≥ 1`: Lognormal com **mediana 30 meses**, σ<sub>log</sub> = 0,6, truncada em [3, 300]. Se `partos == 0`: `NaN` **estrutural** |
| Semântica clínica | Meses entre o último parto e a concepção atual. Intervalo < 18 meses associa-se a prematuridade, baixo peso e anemia |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | **Estrutural, 100 % em nulíparas.** Não é dado perdido: a variável **não se aplica** |
| Papel na rotulagem | Indicador `intervalo_interpartal_meses < 18` (β = +0,40). Em nulíparas o termo é **0** — ausência estrutural contribui zero, não contribui "mediana" |
| Tratamento no pipeline | **Tratamento duplo, deliberado:** (1) coluna indicadora `intervalo_interpartal_nao_aplicavel ∈ {0,1}`, derivada de `partos == 0`; (2) o valor numérico é preenchido com `0.0` **quando não aplicável** e imputado pela mediana **quando aplicável mas ausente** — mas na v1.0.0 não há ausência não-estrutural nesta coluna, então todo `NaN` é estrutural |
| Observações | Esta é a única coluna com ausência estrutural, e o motivo de o pipeline precisar distinguir *ausência* de *não-aplicabilidade*. Tratar as duas igual ensinaria ao modelo que "nulípara" e "dado perdido" são a mesma coisa (`ESTRATEGIA_DE_ROTULAGEM.md` §4). A coluna indicadora é **redundante com `partos == 0`**, e isso é aceito: redundância explícita é preferível a uma convenção implícita de sentinela |

---

## 5. Features de sinais vitais e laboratório

### 5.1 `pas_mmhg`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | mmHg |
| Domínio / faixa | 80–200 |
| Distribuição geradora planejada `[ESPEC]` | Base Normal **μ = 112, σ = 12**; **+18 mmHg se `has_cronica == 1`**; mais ruído de aferição **N(0, 4)**; soma truncada em [80, 200] e arredondada |
| Semântica clínica | Pressão arterial sistólica aferida na consulta. ≥ 140 define hipertensão |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | Termo contínuo `(pas − 120)/10` (β = +0,38); participa da interação `gemelaridade × (pas − 120)/10` (β = +0,45) |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | O ruído `N(0, 4)` é **ruído de aferição aplicado depois** do efeito de `has_cronica`, e é o mesmo valor usado no escore latente — ou seja, o rótulo é gerado a partir da PA **ruidosa**, a mesma que o modelo vê. Não há PA "verdadeira" oculta. Se houvesse, isso introduziria erro de medida clássico e **reduziria** o teto teórico de desempenho de um jeito não contabilizado pelo erro de Bayes do Bernoulli |

### 5.2 `pad_mmhg`

| Atributo | Valor |
|---|---|
| Tipo | `int` |
| Unidade | mmHg |
| Domínio / faixa | 50–130; **restrição adicional `pad_mmhg < pas_mmhg`** |
| Distribuição geradora planejada `[ESPEC]` | Base Normal **μ = 71, σ = 9**; **+12 mmHg se `has_cronica == 1`**; ruído **N(0, 4)**; truncado em [50, 130] e em `pas_mmhg − 15` como teto, garantindo pressão de pulso mínima de 15 mmHg |
| Semântica clínica | Pressão arterial diastólica. ≥ 90 define hipertensão |
| Obrigatória na inferência | **Sim** |
| Mecanismo de ausência | Nenhum |
| Papel na rotulagem | Termo contínuo `(pad − 75)/10` (β = +0,32) |
| Tratamento no pipeline | Numérica. `StandardScaler` |
| Observações | O teto em `pas − 15` é mais forte que a regra do contrato (`pad < pas`) e existe para não gerar pressão de pulso fisiologicamente absurda (ex.: 132/130). O validador Pydantic aplica a regra **fraca** (`pad < pas`) porque é ela que vale para dado de entrada em inferência, onde não controlamos a origem; o gerador aplica a **forte**. A diferença é intencional e está registrada aqui para não parecer inconsistência |

### 5.3 `hemoglobina_g_dl`

| Atributo | Valor |
|---|---|
| Tipo | `float` (nulo permitido) |
| Unidade | g/dL |
| Domínio / faixa | 5,0–16,0 |
| Distribuição geradora planejada `[ESPEC]` | Normal truncada **μ = 12,2, σ = 1,3** em [5,0; 16,0], 1 casa decimal |
| Semântica clínica | Hemoglobina do hemograma de rotina. < 11 g/dL define anemia na gestação (MS) |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | **MCAR, 12 %** — exame não colhido, ao acaso |
| Papel na rotulagem | Indicador `hemoglobina < 11` (β = +0,50). **O rótulo é gerado a partir do valor ANTES do mascaramento** — ver §7 |
| Tratamento no pipeline | Numérica. `SimpleImputer(strategy='median')` → `StandardScaler`. Imputação declarada em `dados_imputados` |
| Observações | Este é o ponto exato em que a imputação custa informação de verdade: para 12 % dos registros o modelo recebe a mediana enquanto o rótulo foi gerado sabendo o valor real. É uma limitação **desenhada de propósito**, para que o pipeline de imputação não seja decorativo |

### 5.4 `glicemia_jejum_mg_dl`

| Atributo | Valor |
|---|---|
| Tipo | `float` (nulo permitido) |
| Unidade | mg/dL |
| Domínio / faixa | 60–200 |
| Distribuição geradora planejada `[ESPEC]` | Lognormal com **mediana 85 mg/dL**, σ<sub>log</sub> = 0,13; **+25 mg/dL se `diabetes_previo == 1`**; truncada em [60, 200], 1 casa decimal |
| Semântica clínica | Glicemia de jejum. ≥ 92 mg/dL na gestação já caracteriza rastreio positivo para DMG (critério IADPSG/MS) |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | **MCAR, 15 %** |
| Papel na rotulagem | Indicador `glicemia_jejum ≥ 92` (β = +0,55), **a partir do valor pré-mascaramento** |
| Tratamento no pipeline | Numérica. `SimpleImputer(strategy='median')` → `StandardScaler` |
| Observações | Lognormal e não Normal porque a distribuição real de glicemia é assimétrica à direita. Correlaciona com `diabetes_previo` por construção — o modelo pode aprender a usar uma como proxy da outra, o que é esperado e **não** é vazamento (ambas são observáveis na consulta) |

### 5.5 `proteinuria_fita`

| Atributo | Valor |
|---|---|
| Tipo | `ordinal` categórico (string, nulo permitido) |
| Unidade | cruzes na fita reagente |
| Domínio / faixa | `ausente` < `traços` < `1+` < `2+` < `3+` |
| Distribuição geradora planejada `[ESPEC]` | Categórica condicional à PAS. Se `pas < 140`: pesos `[0,72; 0,15; 0,08; 0,035; 0,015]`. Se `pas ≥ 140`: pesos deslocados para `[0,45; 0,20; 0,18; 0,11; 0,06]` |
| Semântica clínica | Proteinúria de fita. Proteinúria + hipertensão após 20 semanas é o critério clássico de pré-eclâmpsia |
| Obrigatória na inferência | Não |
| Mecanismo de ausência | **MAR — depende de `ig_semanas`.** 30 % de ausência se `ig_semanas < 20`; 5 % se `ig_semanas ≥ 20`. Racional: a fita é rotina a partir do 2º trimestre |
| Papel na rotulagem | Indicador `proteinuria ≥ 1+` (β = +0,95), a partir do valor pré-mascaramento |
| Tratamento no pipeline | **Ordinal, não one-hot.** `OrdinalEncoder` com ordem explícita `['ausente','traços','1+','2+','3+'] → [0,1,2,3,4]`, precedido de `SimpleImputer(strategy='constant', fill_value='desconhecido')`. A categoria `desconhecido` recebe código próprio (`-1`) em vez de ser confundida com `ausente` |
| Observações | Duas armadilhas evitadas aqui, ambas comuns o bastante para merecer registro: (1) **`ausente` ≠ `desconhecido`** — "fita feita, deu negativo" e "fita não feita" são estados clinicamente opostos e não podem compartilhar código; (2) **one-hot destruiria a ordem** — `3+` é pior que `1+`, e uma codificação sem ordem obrigaria a árvore a redescobrir a monotonicidade a partir dos dados. A ausência é **MAR**, então imputar pela moda introduziria viés dependente de `ig_semanas`; por isso a escolha é categoria explícita, não imputação |

---

## 6. Features de comorbidades e exposições

Todas são `bool` armazenadas como 0/1, todas sem mecanismo de ausência (sempre geradas), todas
tratadas no pipeline por `passthrough` (sem escalonamento — escalonar uma binária não muda nada
para modelos de árvore e distorce a leitura do coeficiente no LogReg, onde o coeficiente de uma
binária não-escalonada é diretamente o log-odds do "sim" contra o "não").

### 6.1 Tabela consolidada

| Coluna | Prevalência geradora planejada `[ESPEC]` | β na rotulagem | Obrigatória | Semântica clínica |
|---|---|---|---|---|
| `has_cronica` | ≈ 0,08, via `Bernoulli(σ(−3,4 + 0,055·(idade−28) + 0,07·(imc−26)))` | **+1,60** | **Sim** | Hipertensão arterial crônica (prévia à gestação ou < 20 sem) |
| `diabetes_previo` | ≈ 0,06, via `Bernoulli(σ(−3,6 + 0,10·(imc−26) + 0,03·(idade−28)))` | **+1,45** | **Sim** | Diabetes mellitus tipo 1 ou 2 prévio à gestação |
| `cardiopatia` | 0,015, `Bernoulli` fixo | **+1,90** | Não | Cardiopatia materna de qualquer etiologia |
| `nefropatia` | 0,012, `Bernoulli` fixo | **+1,75** | Não | Doença renal crônica materna |
| `tev_previo` | 0,020, `Bernoulli` fixo | **+1,20** | Não | Tromboembolismo venoso prévio / trombofilia conhecida |
| `gemelaridade` | 0,016, `Bernoulli` fixo | **+1,30** | **Sim** | Gestação múltipla (dupla ou mais) |
| `tabagismo` | 0,100, `Bernoulli` fixo | **+0,45** | Não | Tabagismo ativo na gestação |
| `infeccao_sexual_ativa` | 0,040, `Bernoulli` fixo | **+0,85** | Não | HIV, sífilis ou hepatite B/C **em atividade** |

### 6.2 Notas sobre as dependências impostas

`has_cronica` e `diabetes_previo` são as **duas únicas comorbidades geradas condicionalmente** a
outras features. Isso é deliberado e tem três consequências que precisam estar documentadas:

1. **Cria confusão (*confounding*) genuína.** `idade`, `imc` e `has_cronica` ficam correlacionados.
   O modelo terá que distribuir crédito entre variáveis correlacionadas — que é exatamente a
   situação em que a interpretação de SHAP fica delicada (ver `EXPLICABILIDADE.md` §7).
2. **Torna as interações não-triviais.** `idade ≥ 35 × has_cronica` só é informativa se as duas não
   forem independentes de forma degenerada.
3. **A prevalência marginal resultante é `[PEND]`.** Os valores "≈ 0,08" e "≈ 0,06" acima são o
   **alvo** da parametrização, não uma medida. A prevalência efetiva só será conhecida após a
   geração e será registrada em `QUALIDADE_DOS_DADOS.md`. Se divergir do alvo além da tolerância
   definida lá, o intercepto do gerador é ajustado — e **o ajuste é registrado como mudança de
   versão do contrato**, nunca aplicado silenciosamente.

As seis comorbidades com `Bernoulli` de taxa fixa são geradas **independentemente entre si**, o que
é uma simplificação reconhecida: cardiopatia e nefropatia coocorrem no mundo real. Ver
`ESTRATEGIA_DE_ROTULAGEM.md` §6.2.

---

## 7. Variável alvo

### 7.1 `alto_risco`

| Atributo | Valor |
|---|---|
| Tipo | `bool` (0/1) |
| Unidade | — |
| Domínio / faixa | {0, 1}; `1` = classe positiva = alto risco |
| Processo gerador | Três camadas (`ESTRATEGIA_DE_ROTULAGEM.md`): (1) escore latente `z = β₀ + Σ βᵢxᵢ` com β₀ = −3,10; (2) três termos de interação; (3) `p = σ(z)` e **`alto_risco ~ Bernoulli(p)`** |
| Prevalência-alvo `[ESPEC]` | **≈ 0,22** — escolha de projeto, calibrada pelo intercepto. **Não é medida epidemiológica brasileira** |
| Prevalência observada | `[PEND]` — será medida após a geração e registrada em `QUALIDADE_DOS_DADOS.md` |
| Semântica clínica | Gestação que requer encaminhamento ao pré-natal de alto risco e vigilância intensificada, na estratificação assistencial MS/FEBRASGO. **Não é diagnóstico de doença** |
| Obrigatória na inferência | Não se aplica — é a saída |
| Tratamento no pipeline | É `y`. Não passa por transformação |

### 7.2 Ordem crítica das operações no gerador

A ordem abaixo é **vinculante** e a inversão de dois passos quaisquer muda o significado do dataset:

```
1. Amostrar todas as features com seus valores COMPLETOS (incluindo hemoglobina,
   glicemia e proteinúria — nenhum NaN ainda)
2. Aplicar o ruído de aferição N(0,4) a pas_mmhg e pad_mmhg
3. Calcular z (escore latente) a partir dos valores COMPLETOS e JÁ RUIDOSOS
4. p = sigmoide(z)            → salvar em risco_latente
5. alto_risco ~ Bernoulli(p)  → salvar como alvo
6. SÓ ENTÃO aplicar as máscaras de ausência (MCAR/MAR) sobre as features
7. Atribuir registro_id, dataset_version e split
```

**Por que o passo 6 vem depois do 5:** no mundo real, o desfecho de uma gestante não depende de o
laboratório ter processado o hemograma dela. A ausência é do *registro*, não da *paciente*. Gerar o
rótulo antes do mascaramento reproduz essa assimetria, e é o que torna a imputação um problema
real: o modelo precisa estimar um rótulo que foi determinado por informação que ele não recebeu.

**O que aconteceria se invertêssemos:** se as máscaras fossem aplicadas antes do passo 3, teríamos
que decidir o que fazer com o `NaN` no cálculo de `z` — e qualquer decisão (tratar como 0, imputar a
mediana) faria a ausência *causar* mudança no risco verdadeiro. O modelo então aprenderia a prever
a política de imputação do gerador, que é uma forma sutil de circularidade.

---

## 8. Colunas de rastreabilidade (não são features)

### 8.1 Tabela

| Coluna | Tipo | Domínio | Uso | Entra na matriz `X`? |
|---|---|---|---|---|
| `registro_id` | `str` (UUID) | UUID v5 determinístico, derivado do índice + semente | Chave única do registro; permite provar unicidade e rastrear um caso entre splits | **Não** |
| `dataset_version` | `str` | `v1.0.0` | Gravada no `model_card.json`; carregar modelo com MAJOR diferente gera erro | **Não** |
| `split` | `str` | `treino` \| `validacao` \| `teste` | Define a partição; ver `ESTRATEGIA_TREINO_TESTE.md` | **Não** |
| `risco_latente` | `float` | (0, 1) | **Probabilidade verdadeira do processo gerador.** Auditoria do gerador; cálculo do teto teórico (erro de Bayes); avaliação de calibração | **NUNCA** |

### 8.2 `risco_latente` — a coluna mais perigosa do dataset

`risco_latente` é literalmente `P(alto_risco = 1)` para aquele registro. Um modelo que a recebesse
como feature atingiria o teto de Bayes trivialmente e **toda métrica reportada seria lixo com
aparência de excelência**.

Controles em três camadas, porque uma só não basta:

| Camada | Controle |
|---|---|
| Código | `lib/ml/dataset.py::carregar_features()` remove explicitamente `risco_latente`, `registro_id`, `dataset_version`, `split` e `alto_risco` por **lista de permissão** (allow-list de features), não por lista de exclusão |
| Teste | `tests/unit/test_dataset_sem_vazamento.py` falha se qualquer coluna de rastreabilidade aparecer em `X.columns` |
| Auditoria | Verificação de correlação: qualquer feature com \|corr\| > 0,95 com o alvo é investigada antes do treino (`DEFINICAO_DO_PROBLEMA.md` §6) |

A escolha de **allow-list em vez de deny-list** é o ponto técnico importante: com deny-list, uma
coluna nova acrescentada ao gerador entraria na matriz de features por padrão. Com allow-list, ela
fica de fora até ser declarada. O modo de falha seguro é excluir, não incluir.

Detalhamento completo em `docs/dados/RISCOS_DE_VAZAMENTO.md` (risco **VAZ-01**).

---

## 9. Mapeamento com `hospital.db` — o que o banco tem e o que não tem

Esta seção é obrigatória porque a demonstração ponta a ponta usa pacientes reais do banco mock, e
é preciso saber com precisão **quais features podem ser extraídas de lá** — e, sobretudo, quais não
podem.

### 9.1 O schema real de `hospital.db`

Confirmado por leitura de `lib/db.py:31-103`. Sete tabelas:

| Tabela | Colunas | Contém alguma feature de ML? |
|---|---|---|
| `pacientes` | `paciente_id`, `nome`, `data_nascimento`, `cpf_hash`, `convenio`, `cadastro_em` | Apenas `data_nascimento` → `idade` |
| `prontuario_gineco` | `paciente_id`, `menarca_idade`, `g_p_a`, `dum`, `metodo_contraceptivo`, `historico_familiar`, `observacoes` | `g_p_a` → `gestacoes`/`partos`/`abortos`; `dum` → `ig_semanas` |
| `exames` | `paciente_id`, `tipo`, `data_realizacao`, `resultado` (**TEXTO LIVRE**), `proximo_recomendado` | **Nenhuma** |
| `registros_violencia` | `tipo`, `data_atendimento`, `notificado_sinan`, `encaminhamentos`, `observacoes` | **Nenhuma** |
| `log_acesso` | auditoria LGPD | **Nenhuma** |
| `medicamentos` | bula: princípio ativo, indicações, contraindicações, categorias de gestação/lactação | **Nenhuma** |
| `ciclos_menstruais` | `data_inicio`, `duracao_dias`, `sintomas` | **Nenhuma** |

### 9.2 Declaração explícita das ausências

> **`hospital.db` NÃO possui sinais vitais.** Não há pressão arterial, frequência cardíaca,
> temperatura, peso, altura nem IMC em nenhuma das sete tabelas.
>
> **`hospital.db` NÃO possui resultados laboratoriais numéricos.** A tabela `exames` armazena
> `resultado` como **texto livre** — os valores gerados por `lib/mock_data.py` são literais como
> `'BI-RADS 2 (achados benignos)'`, `'NIC I / LSIL'`, `'Negativo para lesão intraepitelial'`,
> `'Gestação tópica única, IG compatível, BCF presentes'`. Não há hemoglobina, glicemia ou
> proteinúria — nem como número, nem como texto.
>
> **`hospital.db` NÃO possui comorbidades estruturadas.** Não existe tabela, coluna nem campo
> booleano para hipertensão, diabetes, cardiopatia, nefropatia, TEV ou gemelaridade. O que mais se
> aproxima é `prontuario_gineco.historico_familiar`, um texto livre sorteado de cinco frases fixas
> (`mock_data.py:187-191`) — e que é história **familiar**, não da paciente. `'HAS e DM2 na
> família'` **não** é `has_cronica = 1`; interpretá-lo assim seria inventar dado clínico.
>
> **`hospital.db` NÃO possui desfecho nem variável alvo.** Nenhuma coluna indica risco gestacional,
> encaminhamento, complicação ou resultado da gestação.

### 9.3 Mapeamento feature a feature

| Feature | Origem em `hospital.db` | Mapeável? | Observação |
|---|---|---|---|
| `idade` | `pacientes.data_nascimento` | **Sim** `[DERIV]` | `(TODAY − data_nascimento).days // 365`, com `TODAY = date(2026,5,22)` de `alertas.py:16`. **Cuidado:** a coorte do banco vai de 18 a 75 anos (`mock_data.py:118-124`), e o domínio do contrato é 13–50 — pacientes acima de 50 anos são rejeitadas pelo Pydantic, o que está **correto** (não são gestantes) |
| `ig_semanas` | `prontuario_gineco.dum` | **Parcial** `[DERIV]` | `(TODAY − dum).days // 7`. Só faz sentido para o cenário `gestante` de `mock_data.py:176-178`, que gera DUM de 6 a 36 semanas. Para as demais pacientes a DUM é o último ciclo menstrual e a IG derivada seria **sem sentido clínico**. Requer verificação de plausibilidade antes de usar |
| `gestacoes` | `prontuario_gineco.g_p_a` | **Parcial** `[DERIV]` | Parse de `'G2P1A0'`. **Problema conhecido:** `mock_data._gpa` (linhas 142-153) pode gerar `G0`, e o contrato exige `gestacoes ≥ 1`. Além disso, para uma paciente do cenário `gestante`, não há garantia de que o `G` já contabilize a gestação atual — os dois geradores foram escritos independentemente. O adaptador deve tratar isso explicitamente, **não silenciosamente** |
| `partos` | `prontuario_gineco.g_p_a` | **Parcial** `[DERIV]` | Parse do `P`. Sujeito à mesma ressalva |
| `abortos` | `prontuario_gineco.g_p_a` | **Parcial** `[DERIV]` | Parse do `A`. Sujeito à mesma ressalva |
| `imc_pre_gestacional` | — | **NÃO** | Sem peso nem altura no banco |
| `escolaridade_anos` | — | **NÃO** | Sem dado socioeconômico |
| `cesareas_previas` | — | **NÃO** | `g_p_a` não distingue via de parto |
| `natimorto_previo` | — | **NÃO** | Não registrado |
| `pre_eclampsia_previa` | — | **NÃO** | Não registrado |
| `intervalo_interpartal_meses` | — | **NÃO** | Sem datas de partos anteriores |
| `pas_mmhg` | — | **NÃO** | **Sem sinais vitais** |
| `pad_mmhg` | — | **NÃO** | **Sem sinais vitais** |
| `hemoglobina_g_dl` | — | **NÃO** | `exames` não cobre hemograma |
| `glicemia_jejum_mg_dl` | — | **NÃO** | `exames` não cobre bioquímica |
| `proteinuria_fita` | — | **NÃO** | `exames` não cobre EAS/fita |
| `has_cronica` | — | **NÃO** | Sem comorbidade estruturada |
| `diabetes_previo` | — | **NÃO** | Sem comorbidade estruturada |
| `cardiopatia` | — | **NÃO** | Sem comorbidade estruturada |
| `nefropatia` | — | **NÃO** | Sem comorbidade estruturada |
| `tev_previo` | — | **NÃO** | Sem comorbidade estruturada |
| `gemelaridade` | — | **NÃO** | `exames.resultado` do cenário gestante diz literalmente `'Gestação tópica única'` — é string fixa para todas, não um campo |
| `tabagismo` | — | **NÃO** | Sem histórico de hábitos |
| `infeccao_sexual_ativa` | — | **NÃO** | Sem sorologias |
| `alto_risco` (alvo) | — | **NÃO** | **Não existe desfecho no banco** |

### 9.4 Contagem e consequência

| | Total | Mapeáveis de `hospital.db` | Não mapeáveis |
|---|---|---|---|
| Todas as features | 24 | **5** (21 %) | 19 (79 %) |
| **Features obrigatórias** | **11** | **5** | **6** |

As 6 obrigatórias ausentes são `imc_pre_gestacional`, `pas_mmhg`, `pad_mmhg`, `has_cronica`,
`diabetes_previo` e `gemelaridade`.

**Consequência arquitetural direta:** `lib/ml/schema.py::features_de_paciente(conn, paciente_id)`
**sempre** devolverá um `GestanteFeatures` incompleto para qualquer paciente do `hospital.db`, e o
contrato (`CONTRATO_DE_DADOS.md` §5) determina que campo obrigatório ausente **não é imputado** —
levanta `DadosIncompletosError`.

Portanto o caminho `dados_incompletos → human-in-the-loop` do workflow
(`ARQUITETURA_ALVO.md` §4) **não é um cenário de demonstração encenado: é o comportamento
inevitável de qualquer paciente real do banco.** O complemento manual dos 6 campos obrigatórios
pelo profissional é parte legítima do fluxo, não um contorno.

### 9.5 O que explicitamente NÃO será feito

| Tentação | Por que é recusada |
|---|---|
| Adicionar colunas de sinais vitais ao schema de `hospital.db` | Vedado pelo contrato (§4) e pela ADR-001: quebraria os notebooks 05/07/10 |
| Inferir `has_cronica` de `historico_familiar` por regex | História **familiar** não é história **pessoal**. Seria inventar diagnóstico |
| Extrair valores laboratoriais de `exames.resultado` com LLM | Os textos são cinco literais fixos sorteados por `mock_data.py`; não há número a extrair. Rodar um LLM sobre eles produziria alucinação com aparência de extração |
| Imputar a PA pela mediana da população sintética | É precisamente o "silêncio perigoso" que `CONTRATO_DE_DADOS.md` §5 proíbe |

---

## 10. Resumo do pipeline de pré-processamento

Consolidação do que cada grupo recebe. Implementação em `lib/ml/features.py`, como
`ColumnTransformer` dentro de um `Pipeline` sklearn — `fit` **exclusivamente** sobre o conjunto de
treino (ver `RISCOS_DE_VAZAMENTO.md`, risco **VAZ-02**).

| Grupo | Colunas | Imputação | Codificação | Escalonamento |
|---|---|---|---|---|
| Numéricas sem ausência | `idade`, `imc_pre_gestacional`, `ig_semanas`, `gestacoes`, `partos`, `abortos`, `cesareas_previas`, `pas_mmhg`, `pad_mmhg` | Nenhuma | — | `StandardScaler` |
| Numéricas com ausência MCAR | `hemoglobina_g_dl`, `glicemia_jejum_mg_dl`, `escolaridade_anos` | `SimpleImputer(median)` | — | `StandardScaler` |
| Numérica com ausência estrutural | `intervalo_interpartal_meses` | `fill_value=0.0` + coluna indicadora `*_nao_aplicavel` | — | `StandardScaler` |
| Ordinal com ausência MAR | `proteinuria_fita` | `SimpleImputer(constant='desconhecido')` | `OrdinalEncoder` com ordem explícita; `desconhecido → −1` | Nenhum |
| Binárias | `natimorto_previo`, `pre_eclampsia_previa`, `has_cronica`, `diabetes_previo`, `cardiopatia`, `nefropatia`, `tev_previo`, `gemelaridade`, `tabagismo`, `infeccao_sexual_ativa` | Nenhuma | `passthrough` | Nenhum |

**Nota sobre o escalonamento e os dois modelos:** `StandardScaler` é indispensável para a Regressão
Logística (escalas heterogêneas distorcem a regularização e tornam os coeficientes incomparáveis
entre si) e **indiferente** para o Random Forest, que só usa ordenação. Mantê-lo no `Pipeline`
comum aos dois é decisão de simplicidade: um único caminho de transformação, um único objeto
serializado, nenhuma chance de treino e inferência divergirem. O custo é nulo; o ganho é que
`tests/regression/test_predicao_estavel.py` precisa verificar **um** pipeline, não dois.

---

## 11. Estado atual

| Item | Estado |
|---|---|
| Dataset gerado | **Não.** `artifacts/data/` não existe |
| `lib/ml/dataset.py` | **Não implementado** |
| `lib/ml/schema.py` | **Não implementado** |
| `lib/ml/features.py` | **Não implementado** |
| Estatísticas descritivas observadas | **Nenhuma medida.** Ver `QUALIDADE_DOS_DADOS.md` |
| Pendência PC-01 (23 vs 24 features) | **Resolvida: 24 features** |

Todo valor numérico deste documento é especificação de projeto. **Nenhum é resultado de execução.**

---

## 12. Documentos relacionados

| Documento | Relação |
|---|---|
| `CONTRATO_DE_DADOS.md` | Define o esquema e as regras de validação que este dicionário detalha |
| `ESTRATEGIA_DE_ROTULAGEM.md` | Define os coeficientes β citados na coluna "Papel na rotulagem" |
| `QUALIDADE_DOS_DADOS.md` | Receberá as estatísticas observadas marcadas `[PEND]` aqui |
| `ESTRATEGIA_TREINO_TESTE.md` | Define como a coluna `split` é atribuída |
| `RISCOS_DE_VAZAMENTO.md` | Detalha os controles sobre `risco_latente` e sobre o pré-processamento |
| `docs/ml/DEFINICAO_DO_PROBLEMA.md` | Consome este dicionário para a definição de `X` e `y` |
