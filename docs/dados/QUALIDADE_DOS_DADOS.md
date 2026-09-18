> **Medidas do manifesto v1.0.0** (`artifacts/data/risco_gestacional_v1.manifest.json` e `perfil_v1.json`): n=8000, sha256 `6a3b6aefe9e2cf1bb3ec9123386cac4812fd4ef1602657d7950668d5abc20e2f`, prevalência alto_risco **0,20575**, splits 5600/1200/1200. Dataset **sintético**. Nulos opcionais: `intervalo_interpartal_meses` 4010, `escolaridade_anos` 1643, `proteinuria_fita` 1347, `glicemia_jejum_mg_dl` 1188, `hemoglobina_g_dl` 924 (obrigatórias 0 nulos).

# Qualidade dos Dados — Plano e Modelo de Relatório


**Agente responsável:** `DataEngineeringAgent`
**Status:** Plano definido — **dataset não gerado, nenhuma verificação executada**
**Escopo:** `risco_gestacional_sintetico` v1.0.0
**Implementação alvo:** `lib/ml/dataset.py::perfilar()`, `tests/unit/test_qualidade_dataset.py`

---

> ## ⚠ NENHUMA VERIFICAÇÃO FOI EXECUTADA
>
> O dataset ainda **não foi gerado**. `lib/ml/dataset.py` não existe. `artifacts/data/` não existe.
>
> Todas as tabelas de resultado deste documento estão **vazias**, com células preenchidas por `—`.
> Elas serão populadas **exclusivamente** a partir de
> `artifacts/data/risco_gestacional_v1.manifest.json` e do relatório de perfilamento produzido por
> `python scripts/train.py --gerar-dataset --perfilar`.
>
> Os números que **aparecem** neste documento são **limites de tolerância e critérios de aceite**
> — decisões de projeto tomadas *antes* de ver os dados, o que é justamente o que lhes dá valor.
> Nenhum é uma medida.

---

## 1. Por que um plano de qualidade para dado sintético

A objeção é legítima: se nós geramos os dados, por que verificá-los?

Porque o que se verifica **não é a realidade dos dados — é a fidelidade do gerador à sua própria
especificação**. Um gerador com um índice trocado, um `rng` reconstruído dentro de um laço ou uma
máscara de ausência aplicada na ordem errada produz um Parquet perfeitamente bem-formado e
completamente diferente do que `DICIONARIO_DE_DADOS.md` descreve. Sem verificação automatizada, a
divergência só apareceria — se aparecesse — como uma métrica estranha três etapas adiante, quando
já seria cara de diagnosticar.

Há um segundo motivo, mais importante: **o pipeline de qualidade precisa existir e ser exercitado**
para que o projeto demonstre a prática. Um pipeline de validação testado contra dado sintético
transporta-se para dado real; um pipeline inexistente não.

E há o motivo negativo, que a §7 desenvolve: **várias dimensões clássicas de qualidade de dados são
simplesmente inaplicáveis aqui**, e dizer isso com todas as letras vale mais do que preencher a
seção com métricas que não significam nada.

---

## 2. Dimensões de qualidade avaliadas

| # | Dimensão | Pergunta que responde | Avaliável neste dataset? |
|---|---|---|---|
| D1 | **Completude** | As ausências estão nas colunas previstas, nas taxas previstas, pelos mecanismos previstos? | **Sim** |
| D2 | **Consistência** | As relações entre campos respeitam as restrições obstétricas e lógicas? | **Sim** |
| D3 | **Validade** | Todo valor está dentro do domínio declarado no contrato? | **Sim** |
| D4 | **Unicidade** | Cada registro é único e identificável? Há duplicatas? | **Sim** |
| D5 | **Distribuição** | As marginais correspondem às distribuições geradoras especificadas? | **Sim** |
| D6 | **Balanceamento** | A prevalência da classe positiva está próxima do alvo de projeto? | **Sim** |
| D7 | **Reprodutibilidade** | Duas gerações com a mesma semente produzem bytes idênticos? | **Sim** |
| D8 | **Integridade referencial** | O contrato, o gerador e o schema Pydantic concordam sobre as colunas? | **Sim** |
| — | Representatividade | Os dados refletem a população-alvo? | **NÃO** — ver §7 |
| — | Acurácia (vs. fonte de verdade) | Os valores correspondem ao que foi medido na paciente? | **NÃO** — ver §7 |
| — | Atualidade / vigência temporal | Os dados são recentes o bastante? | **NÃO** — ver §7 |
| — | Proveniência | A origem de cada registro é rastreável a uma fonte? | **NÃO** — ver §7 |

---

### D1 — Completude

O que se verifica não é "há poucos nulos" (a resposta desejada aqui não é zero — as ausências são
**intencionais**), e sim que as ausências estão **exatamente onde e na proporção em que foram
especificadas**.

| Coluna | Mecanismo especificado | Taxa-alvo | Tolerância |
|---|---|---|---|
| `hemoglobina_g_dl` | MCAR | 12 % | ± 1,5 pp |
| `glicemia_jejum_mg_dl` | MCAR | 15 % | ± 1,5 pp |
| `proteinuria_fita` (IG < 20 sem) | MAR | 30 % | ± 3,0 pp |
| `proteinuria_fita` (IG ≥ 20 sem) | MAR | 5 % | ± 1,5 pp |
| `escolaridade_anos` | MCAR | 20 % | ± 2,0 pp |
| `intervalo_interpartal_meses` | Estrutural | **100 % em `partos == 0`** | **0,0 pp — exato** |
| Todas as demais 19 colunas | Nenhum | **0 %** | **0,0 pp — exato** |

As tolerâncias assimétricas têm razão: as taxas MCAR são amostrais e flutuam com o tamanho do
subgrupo (daí ± 1,5 pp em n = 8 000), mas a ausência estrutural é **determinística** — se uma
nulípara tiver `intervalo_interpartal_meses` preenchido, ou uma multípara tiver `NaN`, o gerador
está errado, não é flutuação. Tolerância zero.

A verificação do mecanismo **MAR** é a única que exige mais que uma contagem: é preciso confirmar
que a ausência de `proteinuria_fita` **depende de `ig_semanas` e não depende do alvo**. Duas
checagens:

1. Taxa de ausência em `ig_semanas < 20` significativamente maior que em `ig_semanas ≥ 20`.
2. Taxa de ausência **condicional ao alvo**, dentro de cada faixa de IG, estatisticamente
   indistinguível entre `alto_risco = 0` e `alto_risco = 1`. Se divergirem, a ausência seria
   **MNAR** e dependente do rótulo — o que criaria uma forma real de vazamento via o padrão de
   ausência (ver `RISCOS_DE_VAZAMENTO.md`, risco **VAZ-08**).

### D2 — Consistência entre campos

Restrições que precisam valer para **todos os 8 000 registros**, sem exceção:

| ID | Restrição | Origem |
|---|---|---|
| C1 | `partos + abortos ≤ gestacoes` | Validador cruzado do contrato (§5) |
| C2 | `pad_mmhg < pas_mmhg` | Validador cruzado do contrato (§5) |
| C3 | `cesareas_previas ≤ partos` | Lógica obstétrica |
| C4 | `partos == 0` ⟹ `intervalo_interpartal_meses` é nulo | Ausência estrutural |
| C5 | `partos ≥ 1` ⟹ `intervalo_interpartal_meses` **não** é nulo (v1.0.0 não tem ausência não-estrutural nesta coluna) | Especificação do gerador |
| C6 | `partos == 0` ⟹ `natimorto_previo == 0` | Não há natimorto sem parto |
| C7 | `partos == 0` ⟹ `pre_eclampsia_previa == 0` | Não há gestação anterior |
| C8 | `gestacoes ≥ 1` | A gestação avaliada já conta |
| C9 | `pas_mmhg − pad_mmhg ≥ 15` | Pressão de pulso mínima (restrição forte do gerador; ver `DICIONARIO_DE_DADOS.md` §5.2) |

C9 merece nota: ela é mais forte que C2 e vale **para o dataset gerado**, mas o validador Pydantic
de inferência aplica apenas C2. A diferença é deliberada — em inferência, os dados vêm de fora e
uma pressão de pulso estreita, embora incomum, é clinicamente possível. Rejeitar entrada real por
uma regra que só o nosso gerador precisa obedecer seria confundir especificação do gerador com
especificação do domínio.

### D3 — Validade de domínio

Para cada uma das 24 features, verificar `min ≥ limite_inferior` e `max ≤ limite_superior`
conforme `CONTRATO_DE_DADOS.md` §3. Verificar também:

- **Tipos:** inteiros são realmente inteiros no Parquet (não `float` com `.0`) — um `int` que vira
  `float` na serialização quebra a comparação de hash e confunde o `OrdinalEncoder`.
- **Categorias:** `proteinuria_fita` contém **apenas** os cinco literais especificados (ou nulo).
  Um `'traços'` grafado `'tracos'` em parte dos registros criaria uma sexta categoria silenciosa.
- **Alvo:** `alto_risco ∈ {0, 1}`, sem terceiro valor e sem nulo.
- **`risco_latente` ∈ (0, 1)**, estritamente — nem 0 nem 1 exatos, que indicariam saturação da
  sigmoide e, portanto, um `z` numericamente extremo.

### D4 — Unicidade

| Verificação | Critério |
|---|---|
| `registro_id` único | `df['registro_id'].nunique() == len(df) == 8000` |
| `registro_id` não nulo | Zero nulos |
| Linhas de **feature** integralmente duplicadas | Contadas e reportadas. **Não são erro** — ver abaixo |
| Duplicata **entre splits** | **Erro fatal.** Zero tolerância — é vazamento (`RISCOS_DE_VAZAMENTO.md`, **VAZ-06**) |

Sobre duplicatas de features: com 10 binárias e várias contagens pequenas, é **matematicamente
esperado** que dois registros coincidam em todas as 24 colunas — e, por causa da amostragem de
Bernoulli, eles podem ter **rótulos diferentes**. Isso não é defeito: é a manifestação direta do
erro de Bayes. O que seria defeito é o **mesmo `registro_id`** aparecer em dois splits.

A contagem de duplicatas de features é, porém, informativa por outro motivo: ela é um **limite
empírico do desempenho máximo alcançável**. Nenhum classificador determinístico pode acertar os dois
rótulos de um par idêntico-com-rótulos-opostos. Por isso a contagem entra na tabela de resultados e
é insumo do cálculo do teto teórico em `METRICAS_E_RESULTADOS.md` §11.

### D5 — Distribuição

Comparar as marginais observadas com as distribuições geradoras de `DICIONARIO_DE_DADOS.md`.

| Tipo de coluna | Verificação | Tolerância |
|---|---|---|
| Numérica contínua | Média e desvio-padrão observados vs. parâmetros especificados | Média dentro de ± 3 erros-padrão; desvio dentro de ± 10 % relativo |
| Numérica contínua | Assimetria no sentido esperado (positiva para `glicemia_jejum_mg_dl`, que é lognormal) | Sinal correto |
| Contagem | Moda e cauda compatíveis com Poisson/Binomial especificada | Inspeção do histograma + teste qui-quadrado de aderência |
| Binária | Prevalência observada vs. taxa especificada | ± 1,0 pp para taxas ≥ 0,05; ± 0,5 pp para taxas < 0,05 |
| Ordinal | Frequência por categoria; monotonicidade da relação com `pas_mmhg ≥ 140` | Direção correta |

Nota sobre a truncagem: várias distribuições são **truncadas** (Normal em [13, 50] para `idade`,
por exemplo). Truncagem desloca a média e comprime o desvio em relação aos parâmetros nominais. A
comparação deve ser feita contra os momentos da **distribuição truncada**, não contra μ e σ
nominais. Confundir os dois geraria um alarme falso permanente — e, pior, poderia levar alguém a
"corrigir" um gerador que estava certo.

### D6 — Balanceamento

| Métrica | Alvo de projeto | Tolerância |
|---|---|---|
| Prevalência global de `alto_risco = 1` | **0,22** | **± 2,0 pp** (aceitável: 0,20 a 0,24) |
| Prevalência no split `treino` | 0,22 | ± 1,0 pp do global |
| Prevalência no split `validacao` | 0,22 | ± 2,0 pp do global |
| Prevalência no split `teste` | 0,22 | ± 2,0 pp do global |
| Contagem absoluta de positivos no `teste` | — | **≥ 200**, para que o intervalo de confiança do recall seja utilizável |

A tolerância de ± 2 pp no global não é frouxa por comodidade: a prevalência emerge da interação
entre o intercepto β₀ = −3,10 e **todas** as distribuições marginais que especificamos. Não há
forma fechada de prevê-la. Se o valor observado cair fora da faixa, o procedimento é:

1. **Não** aceitar silenciosamente.
2. Recalibrar **apenas β₀** — nunca os coeficientes clínicos, que carregam a semântica.
3. Registrar o novo β₀ em `ESTRATEGIA_DE_ROTULAGEM.md` e **incrementar a versão do contrato**.
4. Regenerar, recomputar o hash do manifesto, e **descartar qualquer modelo treinado** na versão
   anterior.

A tolerância mais estreita no split de treino (± 1 pp) é consequência da estratificação: se o split
é estratificado corretamente, as três partições reproduzem a prevalência global quase exatamente.
Um desvio maior que 1 pp no treino indicaria falha na estratificação, não flutuação amostral.

O mínimo de 200 positivos no teste é o que torna o relatório honesto: com 15 % de 8 000 = 1 200
registros de teste a 22 % de prevalência, espera-se algo em torno de 264 positivos. Abaixo de 200,
o intervalo de confiança por bootstrap do recall ficaria largo demais para sustentar qualquer
comparação entre modelos — e o documento precisaria dizer isso em vez de reportar um ponto isolado.

### D7 — Reprodutibilidade

| Verificação | Critério |
|---|---|
| Duas gerações consecutivas, mesma semente | DataFrames **idênticos** (`pandas.testing.assert_frame_equal`) |
| SHA-256 do Parquet | Igual ao registrado no manifesto versionado |
| Independência de ordem | Gerar o registro *i* isoladamente produz a mesma linha que gerá-lo em lote |
| Independência de plataforma | `[PEND]` — a verificar entre Windows e Linux (Docker) |

A independência de plataforma é o item frágil, e está declarado como pendente em vez de assumido.
`numpy.random.default_rng` (PCG64) tem fluxo estável por contrato da NumPy, mas o arredondamento de
`float` e a serialização Parquet podem introduzir diferenças de último bit entre plataformas. Se o
hash divergir entre Windows e o contêiner Linux, a resposta correta **não** é relaxar a verificação
— é fixar a política de arredondamento e a versão do `pyarrow`, e registrar o hash por plataforma.

### D8 — Integridade referencial entre contrato, gerador e schema

Esta dimensão verifica que **três artefatos independentes concordam**, e é a que pega a classe de
erro mais cara: a divergência silenciosa entre documentação e código.

| Verificação | Critério |
|---|---|
| Colunas do Parquet == colunas declaradas no contrato | Igualdade de conjunto e de ordem |
| Campos de `GestanteFeatures` (Pydantic) == features do dataset | Igualdade de conjunto |
| `ge`/`le` do Pydantic == domínios do contrato | Igualdade campo a campo |
| Lista de features obrigatórias no código == as 11 do contrato | Igualdade de conjunto |
| `len(FEATURES) == N_FEATURES` | Pendência **PC-01** (ver `DICIONARIO_DE_DADOS.md` §1) |
| `dataset_version` no Parquet == versão do manifesto == versão no `model_card.json` | Igualdade |

---

## 3. Verificações automatizadas — onde cada uma vive

Separação de responsabilidades: **o gerador perfila e reporta; o teste afirma e falha.**

### 3.1 `lib/ml/dataset.py` — em tempo de geração

| Função | Responsabilidade | Comportamento em falha |
|---|---|---|
| `gerar_dataset(seed, n)` | Produz o DataFrame conforme a ordem vinculante de operações (`DICIONARIO_DE_DADOS.md` §7.2) | — |
| `validar_dominios(df)` | D3 — domínio, tipo, categorias | **`ValueError`**. Não grava Parquet |
| `validar_consistencia(df)` | D2 — restrições C1 a C9 | **`ValueError`**. Não grava Parquet |
| `perfilar(df)` | D1, D4, D5, D6 — produz `dict` com o perfil completo | Nunca falha; **reporta** |
| `escrever_manifesto(df, path)` | SHA-256, semente, contagens por classe e por split, versão do gerador, versão do contrato, timestamp, **e o perfil de `perfilar()` embutido** | — |

A decisão de **abortar a gravação** em falha de D2/D3 é intencional: um Parquet inválido em
`artifacts/data/` é pior que nenhum, porque pode ser carregado por engano em uma execução seguinte
e contaminar um treino inteiro.

D1, D5 e D6 **não** abortam a geração — elas são reportadas e comparadas com as tolerâncias pelos
testes. Motivo: são verificações **amostrais**. Fazer o gerador falhar por uma flutuação legítima
tornaria a pipeline intermitente, e pipeline intermitente é pipeline que se aprende a ignorar.

### 3.2 `tests/unit/` — em CI

| Arquivo de teste | Dimensões | O que assere |
|---|---|---|
| `test_qualidade_dataset.py` | D1, D2, D3, D5, D6 | Taxas de ausência dentro da tolerância; C1–C9 para todas as linhas; domínios; marginais; prevalência em 0,22 ± 2 pp |
| `test_dataset_reprodutivel.py` | D7 | Duas gerações idênticas; hash bate com o manifesto |
| `test_dataset_sem_vazamento.py` | D4 | `risco_latente` e demais colunas de rastreabilidade fora de `X`; zero `registro_id` repetido entre splits |
| `test_schema_gestante.py` | D8 | Pydantic ↔ contrato; obrigatórias; `len(FEATURES) == N_FEATURES`; `extra='forbid'` rejeita campo desconhecido |
| `test_split_estratificado.py` | D6 | Proporções 70/15/15; prevalência por split dentro da tolerância |

### 3.3 Princípio: teste por propriedade, não por valor fixo

Os testes asserem **propriedades e tolerâncias declaradas neste documento**, nunca valores
literais capturados de uma execução.

A diferença importa. Um teste escrito como `assert prevalencia == 0.2184` é um teste que:

- **passa a documentar um resultado**, transformando-se numa métrica fabricada com aparência de
  verificação — exatamente o que este projeto se comprometeu a não fazer;
- **quebra** a cada mudança irrelevante de versão de biblioteca;
- **não verifica** o que interessa (que a prevalência está na faixa de projeto).

Um teste escrito como `assert 0.20 <= prevalencia <= 0.24` verifica a especificação. A única
exceção legítima a essa regra é o **hash do dataset** em `test_dataset_reprodutivel.py`, que é um
valor fixo por definição — e que só é gravado no manifesto **depois** de a primeira geração válida
existir, nunca antecipado.

---

## 4. Relatório de qualidade — MODELO A PREENCHER

> **Todas as tabelas desta seção estão vazias.** Serão preenchidas exclusivamente a partir de
> `artifacts/data/risco_gestacional_v1.manifest.json`, gerado por
> `python scripts/train.py --gerar-dataset --perfilar`.
>
> **Nenhuma célula pode ser preenchida por estimativa, por cálculo manual ou por expectativa.**

### 4.1 Identificação da execução

| Campo | Valor |
|---|---|
| Data/hora da geração | — |
| Semente | — |
| Versão do contrato | — |
| Versão do gerador (commit) | — |
| SHA-256 do Parquet | — |
| Nº de registros | — |
| Nº de colunas | — |
| Plataforma (SO / Python / NumPy / PyArrow) | — |
| Tempo de geração (s) | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.2 D1 — Completude observada

| Coluna | Mecanismo | Taxa-alvo | Taxa observada | Tolerância | Situação |
|---|---|---|---|---|---|
| `hemoglobina_g_dl` | MCAR | 12 % | — | ± 1,5 pp | — |
| `glicemia_jejum_mg_dl` | MCAR | 15 % | — | ± 1,5 pp | — |
| `proteinuria_fita` (IG < 20) | MAR | 30 % | — | ± 3,0 pp | — |
| `proteinuria_fita` (IG ≥ 20) | MAR | 5 % | — | ± 1,5 pp | — |
| `escolaridade_anos` | MCAR | 20 % | — | ± 2,0 pp | — |
| `intervalo_interpartal_meses` (nulíparas) | Estrutural | 100 % | — | exato | — |
| Demais 19 colunas | — | 0 % | — | exato | — |

**Verificação de que a ausência de `proteinuria_fita` não depende do alvo (MAR, não MNAR):**

| Faixa de IG | Ausência em `alto_risco = 0` | Ausência em `alto_risco = 1` | Diferença (pp) | Situação |
|---|---|---|---|---|
| IG < 20 sem | — | — | — | — |
| IG ≥ 20 sem | — | — | — | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.3 D2 — Consistência entre campos

| ID | Restrição | Violações | Critério | Situação |
|---|---|---|---|---|
| C1 | `partos + abortos ≤ gestacoes` | — | 0 | — |
| C2 | `pad_mmhg < pas_mmhg` | — | 0 | — |
| C3 | `cesareas_previas ≤ partos` | — | 0 | — |
| C4 | nulípara ⟹ intervalo nulo | — | 0 | — |
| C5 | multípara ⟹ intervalo não nulo | — | 0 | — |
| C6 | nulípara ⟹ sem natimorto prévio | — | 0 | — |
| C7 | nulípara ⟹ sem pré-eclâmpsia prévia | — | 0 | — |
| C8 | `gestacoes ≥ 1` | — | 0 | — |
| C9 | `pas − pad ≥ 15` | — | 0 | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.4 D3 — Validade de domínio

| Coluna | Domínio do contrato | Mín. observado | Máx. observado | Tipo observado | Situação |
|---|---|---|---|---|---|
| `idade` | 13–50 | — | — | — | — |
| `imc_pre_gestacional` | 15,0–55,0 | — | — | — | — |
| `escolaridade_anos` | 0–20 | — | — | — | — |
| `ig_semanas` | 4–42 | — | — | — | — |
| `gestacoes` | 1–12 | — | — | — | — |
| `partos` | 0–10 | — | — | — | — |
| `abortos` | 0–6 | — | — | — | — |
| `cesareas_previas` | 0–5 | — | — | — | — |
| `natimorto_previo` | 0/1 | — | — | — | — |
| `pre_eclampsia_previa` | 0/1 | — | — | — | — |
| `intervalo_interpartal_meses` | 0–300 | — | — | — | — |
| `pas_mmhg` | 80–200 | — | — | — | — |
| `pad_mmhg` | 50–130 | — | — | — | — |
| `hemoglobina_g_dl` | 5,0–16,0 | — | — | — | — |
| `glicemia_jejum_mg_dl` | 60–200 | — | — | — | — |
| `proteinuria_fita` | 5 categorias | — | — | — | — |
| `has_cronica` | 0/1 | — | — | — | — |
| `diabetes_previo` | 0/1 | — | — | — | — |
| `cardiopatia` | 0/1 | — | — | — | — |
| `nefropatia` | 0/1 | — | — | — | — |
| `tev_previo` | 0/1 | — | — | — | — |
| `gemelaridade` | 0/1 | — | — | — | — |
| `tabagismo` | 0/1 | — | — | — | — |
| `infeccao_sexual_ativa` | 0/1 | — | — | — | — |
| `alto_risco` (alvo) | 0/1 | — | — | — | — |
| `risco_latente` (auditoria) | (0, 1) | — | — | — | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.5 D4 — Unicidade

| Verificação | Observado | Critério | Situação |
|---|---|---|---|
| `registro_id` distintos | — | = 8 000 | — |
| `registro_id` nulos | — | = 0 | — |
| `registro_id` repetidos entre splits | — | = 0 (**fatal**) | — |
| Linhas de feature integralmente duplicadas | — | reportar (não é erro) | — |
| Pares duplicados **com rótulos opostos** | — | reportar (insumo do teto de Bayes) | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.6 D5 — Distribuição das features numéricas

| Coluna | Distribuição especificada | Média obs. | DP obs. | Mediana obs. | P05 | P95 | Assimetria | Situação |
|---|---|---|---|---|---|---|---|---|
| `idade` | Normal trunc. μ=27 σ=6 | — | — | — | — | — | — | — |
| `imc_pre_gestacional` | Normal trunc. μ=26,0 σ=5,0 | — | — | — | — | — | — | — |
| `escolaridade_anos` | Normal trunc. μ=10 σ=3,5 | — | — | — | — | — | — | — |
| `ig_semanas` | Mistura por trimestre 0,30/0,40/0,30 | — | — | — | — | — | — | — |
| `gestacoes` | 1 + Poisson(0,9) | — | — | — | — | — | — | — |
| `partos` | Binomial derivada | — | — | — | — | — | — | — |
| `abortos` | Binomial derivada | — | — | — | — | — | — | — |
| `cesareas_previas` | Binomial(partos; 0,42) | — | — | — | — | — | — | — |
| `intervalo_interpartal_meses` | Lognormal med.=30 | — | — | — | — | — | — | — |
| `pas_mmhg` | Normal μ=112 σ=12 (+18 se HAS) + N(0,4) | — | — | — | — | — | — | — |
| `pad_mmhg` | Normal μ=71 σ=9 (+12 se HAS) + N(0,4) | — | — | — | — | — | — | — |
| `hemoglobina_g_dl` | Normal trunc. μ=12,2 σ=1,3 | — | — | — | — | — | — | — |
| `glicemia_jejum_mg_dl` | Lognormal med.=85 (+25 se DM) | — | — | — | — | — | — | — |

**Features binárias:**

| Coluna | Prevalência especificada | Prevalência observada | Tolerância | Situação |
|---|---|---|---|---|
| `has_cronica` | ≈ 0,080 | — | ± 1,0 pp | — |
| `diabetes_previo` | ≈ 0,060 | — | ± 1,0 pp | — |
| `cardiopatia` | 0,015 | — | ± 0,5 pp | — |
| `nefropatia` | 0,012 | — | ± 0,5 pp | — |
| `tev_previo` | 0,020 | — | ± 0,5 pp | — |
| `gemelaridade` | 0,016 | — | ± 0,5 pp | — |
| `tabagismo` | 0,100 | — | ± 1,0 pp | — |
| `infeccao_sexual_ativa` | 0,040 | — | ± 0,5 pp | — |
| `natimorto_previo` | condicional a `partos ≥ 1` | — | ± 0,5 pp | — |
| `pre_eclampsia_previa` | condicional a `partos ≥ 1` | — | ± 0,5 pp | — |

**Feature ordinal `proteinuria_fita`:**

| Categoria | Freq. em `pas < 140` | Freq. em `pas ≥ 140` | Monotonicidade esperada | Situação |
|---|---|---|---|---|
| `ausente` | — | — | ↓ com PAS alta | — |
| `traços` | — | — | ↑ | — |
| `1+` | — | — | ↑ | — |
| `2+` | — | — | ↑ | — |
| `3+` | — | — | ↑ | — |
| `desconhecido` (ausente) | — | — | sem relação com PAS | — |

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.7 D6 — Balanceamento e splits

| Split | n | % do total | Positivos | Negativos | Prevalência | Desvio do alvo (0,22) | Situação |
|---|---|---|---|---|---|---|---|
| `treino` | — | 70 % | — | — | — | — | — |
| `validacao` | — | 15 % | — | — | — | — | — |
| `teste` | — | 15 % | — | — | — | — | — |
| **Total** | — | 100 % | — | — | — | — | — |

**Distribuição de `risco_latente` (auditoria do gerador):**

| Estatística | Valor observado |
|---|---|
| Média de `risco_latente` | — |
| Prevalência observada de `alto_risco` | — |
| Diferença (média de `p` vs. frequência de `y`) | — |
| Mínimo / Máximo de `risco_latente` | — / — |
| % de registros com `risco_latente > 0,5` | — |

A diferença entre a **média de `risco_latente`** e a **prevalência observada** é a verificação mais
direta de que a amostragem de Bernoulli está correta: por construção, `E[y] = E[p]`, então as duas
devem coincidir dentro do erro amostral. Uma divergência sistemática indicaria erro na camada 3 do
gerador — por exemplo, limiarização acidental no lugar de amostragem.

_PENDENTE — será preenchido por `scripts/train.py --gerar-dataset --perfilar`_

### 4.8 D7 — Reprodutibilidade

| Verificação | Resultado | Critério | Situação |
|---|---|---|---|
| Duas gerações idênticas (mesma semente) | — | igualdade exata | — |
| SHA-256 recomputado == manifesto | — | igualdade | — |
| Geração isolada do registro *i* == geração em lote | — | igualdade | — |
| Hash Windows == hash Linux (Docker) | — | igualdade **ou** divergência documentada | — |

_PENDENTE — será preenchido por `python scripts/train.py --verificar-dataset` e por `tests/unit/test_dataset_reprodutivel.py`_

### 4.9 D8 — Integridade referencial

| Verificação | Resultado | Situação |
|---|---|---|
| Colunas do Parquet == contrato | — | — |
| Campos Pydantic == features | — | — |
| Limites Pydantic == domínios do contrato | — | — |
| Obrigatórias no código == 11 do contrato | — | — |
| `len(FEATURES) == N_FEATURES` (PC-01) | — | — |
| `dataset_version` consistente em Parquet / manifesto / model card | — | — |

_PENDENTE — será preenchido por `tests/unit/test_schema_gestante.py`_

### 4.10 Parecer consolidado

| Campo | Valor |
|---|---|
| Dimensões verificadas | — |
| Dimensões aprovadas | — |
| Dimensões reprovadas | — |
| Violações **fatais** (bloqueiam o treino) | — |
| Dataset liberado para treino? | — |
| Responsável pela liberação | — |
| Data do parecer | — |

_PENDENTE — nenhum parecer pode ser emitido antes da execução_

---

## 5. Critérios de bloqueio — o que impede o treino

Nem toda falha tem o mesmo peso. A separação abaixo é declarada **antes** da execução, para que
nenhuma decisão de "isso dá para tolerar" seja tomada já vendo o resultado.

| Severidade | Condição | Ação |
|---|---|---|
| **Fatal** | Qualquer violação de D2 (C1–C9) | Treino **bloqueado**. Corrigir o gerador |
| **Fatal** | Qualquer valor fora de domínio (D3) | Treino **bloqueado** |
| **Fatal** | `registro_id` duplicado entre splits (D4) | Treino **bloqueado** — é vazamento |
| **Fatal** | Coluna de rastreabilidade presente em `X` | Treino **bloqueado** — é vazamento total |
| **Fatal** | Geração não reprodutível (D7) | Treino **bloqueado** |
| **Fatal** | Divergência contrato ↔ schema (D8) | Treino **bloqueado** |
| **Alta** | Prevalência fora de 0,22 ± 2 pp (D6) | Recalibrar β₀, **incrementar versão do contrato**, regenerar |
| **Alta** | Ausência estrutural com taxa ≠ 100 % (D1) | Corrigir o gerador |
| **Alta** | Ausência de `proteinuria_fita` dependente do alvo (MNAR) | Corrigir o gerador — é vazamento potencial (**VAZ-08**) |
| **Média** | Taxa MCAR fora da tolerância (D1) | Investigar; pode ser flutuação. Registrar a decisão |
| **Média** | Marginal fora da tolerância (D5) | Investigar; conferir se a comparação usou os momentos da distribuição **truncada** |
| **Baixa** | Duplicatas de feature acima do esperado | Registrar. Entra no cálculo do teto de Bayes |

---

## 6. Perfilamento adicional — descritivo, sem critério de aprovação

Itens produzidos para o relatório técnico e para a análise de subgrupo, sem limiar de aceite
associado. Estão listados para que ninguém os confunda com verificações.

| Item | Uso |
|---|---|
| Matriz de correlação de Spearman entre as 24 features | Diagnóstico de multicolinearidade; insumo da ressalva sobre SHAP com features correlacionadas (`EXPLICABILIDADE.md` §7) |
| Correlação de cada feature com `alto_risco` | Auditoria de vazamento: \|corr\| > 0,95 dispara investigação (`DEFINICAO_DO_PROBLEMA.md` §6) |
| Correlação de cada feature com `risco_latente` | Confere se a direção observada bate com o sinal do β especificado |
| Histogramas das 13 numéricas | Anexo visual do relatório |
| Tabela de contingência: cada binária × `alto_risco` | Análise de subgrupo |
| Distribuição do alvo por faixa etária (< 20, 20–34, ≥ 35) | Base da análise de subgrupo de `METRICAS_E_RESULTADOS.md` §9 |
| Distribuição do alvo por trimestre de IG | Idem. **Espera-se ausência de relação** — `ig_semanas` tem β = 0 |
| Contagem de casos que o baseline `CRITERIOS_ALTO_RISCO` marcaria | Prevê a taxa de disparo do baseline determinístico antes de treiná-lo |

O penúltimo item é o controle negativo mencionado em `DICIONARIO_DE_DADOS.md` §3.4: como
`ig_semanas` não entra no escore latente, qualquer associação observada entre trimestre e alvo é
ruído amostral ou artefato de correlação induzida. Ter isso registrado **antes** de ver os números
evita a interpretação retrospectiva de um padrão que não existe.

---

## 7. Dimensões de qualidade que NÃO podem ser avaliadas

Esta seção existe porque um relatório de qualidade de dados sintéticos que omita estas limitações é
enganoso, mesmo que tudo o que ele afirme seja verdade.

### 7.1 Representatividade — **não avaliável**

Não há população de referência contra a qual comparar. As distribuições geradoras de
`DICIONARIO_DE_DADOS.md` são **plausíveis** segundo protocolos MS/FEBRASGO, mas
**não foram ajustadas a nenhuma coorte brasileira**. Dizer que "a idade materna média do dataset é
compatível com a literatura" seria comparar um número que escolhemos com um número que lemos, e
chamar a coincidência de validação.

Concretamente: a prevalência de 22 % de alto risco é uma **escolha de projeto** feita para produzir
um problema de aprendizado com desbalanceamento moderado. A prevalência real de gestação de alto
risco no pré-natal do SUS não foi consultada, não foi usada na calibração e não é conhecida por
este documento.

**O que seria necessário:** uma coorte real de pré-natal com as 24 variáveis medidas, e comparação
das marginais e da estrutura de dependência.

### 7.2 Viés de seleção — **não modelado**

Numa coorte real, quem chega ao pré-natal já é uma amostra selecionada: gestantes que acessaram o
serviço, que compareceram à consulta, cujos dados foram registrados. Gestantes sem acesso, com
abandono precoce ou atendidas em serviço sem prontuário eletrônico **não aparecem** — e são
sistematicamente diferentes das que aparecem.

Nosso gerador amostra de uma distribuição idealizada em que todos os 8 000 registros "compareceram"
e "foram registrados". **Não há mecanismo de seleção algum.** Consequência: o desempenho medido
aqui é um limite superior otimista em relação a qualquer implantação.

### 7.3 Viés de aferição — **modelado apenas de forma mínima e simétrica**

O único ruído de medida do dataset é `N(0, 4)` sobre `pas_mmhg` e `pad_mmhg`. É ruído
**gaussiano, centrado em zero e independente de tudo** — a forma mais benigna que erro de medida
pode ter.

O que ocorre no mundo real e **não** está representado:

| Fenômeno real | Efeito | Modelado? |
|---|---|---|
| Manguito de tamanho inadequado em paciente obesa | Erro de PA **correlacionado com o IMC** | **Não** |
| Arredondamento de PA para múltiplos de 10 (*digit preference*) | Distribuição em picos, não contínua | **Não** |
| Hipertensão do avental branco | PA elevada em ambiente clínico, normal fora | **Não** |
| Aferidor / equipamento diferente por unidade | Viés sistemático por centro | **Não** |
| Comorbidade subnotificada em quem acessa menos o serviço | `has_cronica = 0` falso, correlacionado com escolaridade | **Não** |
| Glicemia sem jejum adequado | Valor inflado de forma não aleatória | **Não** |

O quinto item é o mais sério: erro de medida **correlacionado com a variável de desfecho ou com
subgrupos** é o que produz desempenho desigual entre populações. Como ele não existe no nosso
gerador, a **análise de subgrupo** planejada em `METRICAS_E_RESULTADOS.md` §9 só pode detectar
desigualdade originada no **modelo ou na amostragem** — nunca a originada em viés de aferição, que
é a fonte dominante em dados reais.

### 7.4 Efeito de centro / agrupamento — **inexistente por construção**

Não há variável de unidade de saúde, município, profissional ou equipamento. Todos os 8 000
registros são i.i.d. de uma única distribuição.

Isso tem uma consequência metodológica direta e é o que **autoriza** a divisão aleatória simples
descrita em `ESTRATEGIA_TREINO_TESTE.md`: sem agrupamento, não há necessidade de `GroupKFold` nem
de divisão por centro. Em dado real, a divisão aleatória seria **otimista**, porque registros do
mesmo centro compartilham protocolo, equipamento e perfil de população — e cair no treino e no
teste inflaria a métrica.

### 7.5 Acurácia contra fonte de verdade — **não aplicável**

Em dado real, "acurácia" como dimensão de qualidade significa: o valor registrado corresponde ao
que foi medido na paciente? Verifica-se por auditoria de prontuário.

Aqui não existe paciente e não existe medição. O valor **é** o que o gerador produziu — ele é
exato por definição, o que torna a dimensão vazia, não excelente. Reportá-la como "100 % de
acurácia" seria um número verdadeiro e completamente enganoso.

### 7.6 Atualidade e vigência temporal — **não aplicável**

Não há dimensão temporal: nenhuma data de coleta, nenhuma janela de observação, nenhuma deriva.
Todos os registros são contemporâneos entre si e de lugar nenhum.

Consequência: **não é possível avaliar estabilidade temporal do modelo**, que é a validação
mínima exigida antes de qualquer implantação clínica. Ver `LIMITACOES_DO_MODELO.md` §3.

### 7.7 Proveniência — **trivial e, por isso, não informativa**

Cada registro é rastreável ao índice e à semente que o produziram. É rastreabilidade perfeita e
sem valor epistêmico: prova que o código é determinístico, não que o dado corresponde a algo.

### 7.8 Síntese honesta

> Este plano de qualidade verifica que **o gerador faz o que a especificação diz** — nada mais.
>
> Ele **não** verifica, e não tem como verificar, que o dataset representa gestantes brasileiras,
> que as relações entre variáveis correspondem à fisiopatologia, ou que um modelo treinado nele
> funcionaria em qualquer serviço de pré-natal.
>
> Um dataset que passe em todas as oito dimensões avaliáveis continua sendo **100 % sintético e
> sem validade clínica**. As oito dimensões medem fidelidade à especificação; nenhuma delas mede
> correspondência com a realidade.

---

## 8. Estado atual

| Item | Estado |
|---|---|
| `lib/ml/dataset.py` | **Não implementado** |
| `tests/unit/test_qualidade_dataset.py` | **Não implementado** |
| `tests/unit/test_dataset_reprodutivel.py` | **Não implementado** |
| `tests/unit/test_dataset_sem_vazamento.py` | **Não implementado** |
| `tests/unit/test_schema_gestante.py` | **Não implementado** |
| `artifacts/data/` | **Não existe** |
| Dataset gerado | **Não** |
| Verificações executadas | **Nenhuma** |
| Tabelas da §4 preenchidas | **Nenhuma** |

**Nenhuma métrica de qualidade foi medida. Todas as tabelas de resultado estão vazias por
obrigação, não por omissão.**
