> **Status (2026-09-18):** quatro modelos treinados (`artifacts/models/*/model_card.json`). Grids efetivos: LogReg `C=10` L2; RF ver card.

# Modelos Avaliados — Catálogo


**Agente responsável:** `MachineLearningAgent`
**Status:** Catálogo definido — **nenhum modelo treinado**
**Base normativa:** `DEFINICAO_DO_PROBLEMA.md` §4, `ESTRATEGIA_TREINO_TESTE.md`, ADR-002, ADR-004
**Implementação alvo:** `lib/ml/train.py`, `lib/ml/baseline.py`, `artifacts/models/`

---

> ## ⚠ NENHUM MODELO FOI TREINADO
>
> `lib/ml/` não existe. `artifacts/models/` não existe. Nenhum `fit` foi executado, nenhum
> hiperparâmetro foi selecionado, nenhum limiar foi calibrado.
>
> Os grids de hiperparâmetros abaixo são **declarações pré-registradas**: são publicados **antes**
> do primeiro treino justamente para que não possam ser ajustados retroativamente em função dos
> resultados. Os custos computacionais indicados são **ordens de grandeza estimadas pelo tamanho do
> problema** (n = 5 600, p = 24), não medições — e estão marcados como tal.
>
> O campo **Status** de todos os quatro modelos é **`Não treinado`**.

---

## 1. Os quatro modelos

| # | Modelo | Papel | Família | Status |
|---|---|---|---|---|
| 0 | `DummyClassifier(strategy='prior')` | Baseline trivial | Degenerado | **Não treinado** |
| 1 | Baseline determinístico por regra | Baseline forte — **é o sistema atual** | Regra booleana | **Não treinado** |
| 2 | `LogisticRegression` | Modelo linear interpretável | Linear generalizado | **Não treinado** |
| 3 | `RandomForestClassifier` | Ensemble não-linear | Árvores em *bagging* | **Não treinado** |

A ordem é de complexidade crescente, e a lista responde a uma pergunta específica. Não é
"qual modelo tem a melhor métrica?" — é **"o ML supera a regra que o sistema já usa?"**. Sem o
modelo #1, a primeira pergunta seria respondida e a segunda nem seria feita.

---

## 2. Modelo #0 — `DummyClassifier(strategy='prior')`

| Atributo | Conteúdo |
|---|---|
| **Papel** | Piso absoluto de desempenho. Qualquer modelo que não o supere é inútil |
| **Biblioteca e classe** | `sklearn.dummy.DummyClassifier(strategy='prior', random_state=42)` |
| **Hiperparâmetros a buscar** | **Nenhum.** Não há grid. `strategy='prior'` é fixo |
| **Pré-processamento exigido** | **Nenhum.** Ignora `X` inteiramente |
| **Custo computacional** | Desprezível — conta as classes do treino. *(estimativa por inspeção do algoritmo, não medida)* |
| **Interpretabilidade** | Total e trivial: prevê sempre a classe majoritária, com probabilidade constante igual à prevalência do treino |
| **Status** | **Não treinado** |

### Por que foi escolhido

Ele existe para tornar visível, com um número concreto no relatório, a armadilha central da métrica
neste problema: **com ≈ 22 % de positivos, prever sempre "habitual" produz ≈ 78 % de acurácia**.
Esse valor é aritmética sobre a prevalência-alvo de projeto, não um resultado — a acurácia
observada será medida e reportada em `METRICAS_E_RESULTADOS.md`.

Um leitor que veja apenas "acurácia de 85 %" de um modelo real não tem como julgar se é bom. Vendo
ao lado o Dummy, a comparação fica imediata. É por isso que ele entra na tabela comparativa e não
apenas numa nota de rodapé.

Tem também uma função de diagnóstico do pipeline: `recall = 0` e `precision` indefinida na classe
positiva são valores esperados e conhecidos. Se o pipeline de avaliação produzir outra coisa para o
Dummy, o bug está no pipeline, não no modelo.

### Limitações conhecidas

- Não é um competidor. Superá-lo não demonstra nada além de que o modelo aprendeu algo.
- `precision` da classe positiva é indefinida (divisão por zero). `scikit-learn` emite
  `UndefinedMetricWarning` e devolve `0.0` com `zero_division=0`. O relatório deve reportar
  **`indefinida`**, não `0,00` — são coisas diferentes, e escrever `0,00` sugeriria que o modelo
  fez predições positivas erradas quando na verdade não fez predição positiva alguma.

---

## 3. Modelo #1 — Baseline determinístico por regra (`CRITERIOS_ALTO_RISCO`)

| Atributo | Conteúdo |
|---|---|
| **Papel** | **Baseline forte. É o comportamento atual do sistema em produção** |
| **Biblioteca e classe** | Implementação própria: `lib/ml/baseline.py::BaselineCriteriosMS`, compatível com a API sklearn (`fit`, `predict`, `predict_proba`) |
| **Hiperparâmetros a buscar** | **Nenhum.** É uma regra fixa. `fit` é no-op |
| **Pré-processamento exigido** | **Nenhum.** Opera sobre os valores brutos, sem imputação e sem escalonamento |
| **Custo computacional** | Desprezível — uma disjunção booleana por linha. *(estimativa, não medida)* |
| **Interpretabilidade** | **Máxima.** A justificativa de cada predição é a lista literal dos critérios disparados |
| **Status** | **Não treinado** (não há o que treinar) |

### A regra

Origem: `lib/workflows/obstetrico.py:50-66`. Os 15 critérios MS/FEBRASGO, com a semântica
"qualquer um basta".

```python
CRITERIOS_ALTO_RISCO = [
    'idade <16 ou >35a',  'HAS prévia ou induzida',  'DM prévio ou gestacional',
    'cardiopatia',  'nefropatia',  'TEV prévio',  'cesárea prévia (≥2)',
    'abortamento de repetição (≥2)',  'natimorto prévio',  'malformação fetal prévia',
    'gemelaridade',  'IMC ≥35',  'tabagismo / álcool / drogas',
    'HIV / sífilis / hepatites',  'isoimunização Rh',
]
```

### Mapeamento dos 15 critérios para as features disponíveis

Tradução explícita, porque nem todos os critérios têm coluna correspondente:

| # | Critério textual | Expressão sobre as features | Disponível? |
|---|---|---|---|
| 1 | idade < 16 ou > 35a | `idade < 16 or idade > 35` | Sim |
| 2 | HAS prévia ou induzida | `has_cronica == 1` | **Parcial** — só a crônica; a induzida não é feature |
| 3 | DM prévio ou gestacional | `diabetes_previo == 1 or glicemia_jejum_mg_dl >= 92` | **Parcial** — DMG aproximado pelo rastreio |
| 4 | cardiopatia | `cardiopatia == 1` | Sim |
| 5 | nefropatia | `nefropatia == 1` | Sim |
| 6 | TEV prévio | `tev_previo == 1` | Sim |
| 7 | cesárea prévia (≥2) | `cesareas_previas >= 2` | Sim |
| 8 | abortamento de repetição (≥2) | `abortos >= 2` | Sim |
| 9 | natimorto prévio | `natimorto_previo == 1` | Sim |
| 10 | malformação fetal prévia | — | **NÃO** — não existe feature |
| 11 | gemelaridade | `gemelaridade == 1` | Sim |
| 12 | IMC ≥ 35 | `imc_pre_gestacional >= 35` | Sim |
| 13 | tabagismo / álcool / drogas | `tabagismo == 1` | **Parcial** — só tabagismo |
| 14 | HIV / sífilis / hepatites | `infeccao_sexual_ativa == 1` | Sim |
| 15 | isoimunização Rh | — | **NÃO** — não existe feature |

**11 critérios integralmente mapeáveis, 2 parcialmente, 2 não mapeáveis.**

Os dois não mapeáveis (malformação fetal prévia, isoimunização Rh) são **omitidos** da regra, não
aproximados por nada. Aproximá-los por outra variável seria inventar correspondência. A consequência
está declarada: o baseline opera com 13 dos 15 critérios, e **isso o desfavorece marginalmente** na
comparação — uma desvantagem que precisa aparecer no relatório para que a comparação seja lida
corretamente.

### Tratamento da ausência

A regra opera sobre valores brutos, e `glicemia_jejum_mg_dl` é ausente em 15 % dos casos. Decisão:

> **Critério com dado ausente é avaliado como FALSO** (não dispara).

É o comportamento conservador **do ponto de vista do disparo**, mas o **anticonservador do ponto de
vista clínico** — reduz falsos positivos e pode aumentar falsos negativos. Registrado aqui porque
é uma decisão de projeto que afeta a métrica do baseline, e a alternativa (tratar ausência como
disparo) infla artificialmente o recall.

### `predict_proba` de uma regra determinística

A regra produz rótulo, não probabilidade. Para que ela entre nas curvas ROC e PR junto com os
demais, `predict_proba` devolve:

```
P(alto_risco) = 1.0  se algum critério dispara
P(alto_risco) = 0.0  caso contrário
```

**Consequência a declarar no relatório:** com apenas dois valores possíveis, a curva ROC do baseline
tem **um único ponto** entre os extremos, e a "área sob a curva" resultante é a interpolação linear
desse ponto. Ela **não é comparável** à AUC de um modelo que produz probabilidades contínuas, e
reportá-la lado a lado sem essa ressalva seria enganoso. A comparação justa com o baseline é feita
por **recall e precisão em seu ponto único de operação** (`COMPARACAO_MODELOS.md` §3), não por AUC.

Uma alternativa considerada e rejeitada: devolver `n_criterios_disparados / 13` como probabilidade,
o que produziria uma curva com mais pontos. Rejeitada porque **não é o que o sistema faz hoje**. O
baseline existe para representar o comportamento atual, e o comportamento atual é binário. Torná-lo
mais sofisticado para melhorar sua curva seria comparar o ML contra um adversário fictício.

### Por que foi escolhido

É a peça mais importante do catálogo. Ele transforma a pergunta de avaliação:

| Sem o baseline #1 | Com o baseline #1 |
|---|---|
| "O modelo tem boa métrica?" | **"O modelo é melhor do que a regra que já temos?"** |

A segunda é a única pergunta que justifica acrescentar ML a um sistema que já funciona. É também o
que conecta este trabalho ao achado que o originou: hoje, `_avaliar_risco_gestacional`
(`obstetrico.py:124-144`) passa esses mesmos critérios como texto para um LLM de 3B decidir, com
`default='habitual'` em caso de falha de parse — ou seja, a falha silenciosa produz falso negativo
(ADR-002).

### Hipótese a testar

`ESTRATEGIA_DE_ROTULAGEM.md` §3 antecipa que o baseline terá **alto recall e baixa precisão**,
porque uma disjunção ampla dispara com qualquer fator isolado.

> **Isto é uma hipótese, não um resultado.** Ela pode ser refutada. Se o baseline apresentar alta
> precisão, ou recall baixo, o achado será reportado como contrário à expectativa, e a conclusão do
> projeto mudará — possivelmente para "o ML não se justifica neste caso". Esse desfecho é
> legítimo e está previsto em `COMPARACAO_MODELOS.md` §4.4.

### Limitações conhecidas

- Não produz probabilidade calibrada; não há grau de confiança.
- Não tem limiar ajustável — o ponto de operação é fixo.
- Ignora magnitude: PA de 141/91 e de 180/120 são o mesmo "sim".
- Não captura interações.
- Trata todos os critérios com peso idêntico, embora a literatura os diferencie fortemente.
- Opera com 13 de 15 critérios (acima).

Essas limitações são **a motivação clínica do projeto**, não defeitos da implementação do baseline.
Encaminhar ao pré-natal de alto risco toda gestante com um único fator leve sobrecarrega um serviço
que é escasso.

---

## 4. Modelo #2 — `LogisticRegression`

| Atributo | Conteúdo |
|---|---|
| **Papel** | Modelo linear interpretável. Padrão-ouro em escores de risco clínico |
| **Biblioteca e classe** | `sklearn.linear_model.LogisticRegression` |
| **Pré-processamento exigido** | **Obrigatório e completo**: imputação (mediana) → `StandardScaler` → `OrdinalEncoder` para `proteinuria_fita`. Sem escalonamento, a regularização L1/L2 penaliza desproporcionalmente as variáveis de escala menor e os coeficientes ficam incomparáveis entre si |
| **Custo computacional** | Baixo. Convexo, com solução única. *(estimativa: segundos para o grid inteiro em CPU, n = 5 600, p = 24 — não medido)* |
| **Interpretabilidade** | **Alta e nativa.** `exp(coef_)` é a razão de chances por desvio-padrão da feature. Contribuição local exata: `coef × valor_padronizado` |
| **Status** | **Não treinado** |

### Grid de hiperparâmetros — pré-registrado

```python
GRID_LOGREG = {
    'clf__C':            [0.01, 0.1, 1.0, 10.0],
    'clf__penalty':      ['l1', 'l2'],
    'clf__solver':       ['liblinear', 'saga'],
    'clf__class_weight': ['balanced'],
    'clf__max_iter':     [2000],
}
```

| Hiperparâmetro | Valores | Por quê |
|---|---|---|
| `C` | 0,01 / 0,1 / 1,0 / 10,0 | Inverso da regularização, em escala logarítmica. Quatro ordens de grandeza cobrem de fortemente regularizado a praticamente irrestrito |
| `penalty` | `l1`, `l2` | L1 produz esparsidade (zera coeficientes), o que é informativo com 24 features — em especial para `escolaridade_anos`, cujo efeito gerador é deliberadamente fraco (β = −0,04). L2 é o padrão estável |
| `solver` | `liblinear`, `saga` | Restrição técnica: nem todo solver aceita L1. `liblinear` e `saga` aceitam ambas as penalidades. Combinações inválidas são filtradas pelo `GridSearchCV` |
| `class_weight` | `balanced` **fixo** | Determinado por `DEFINICAO_DO_PROBLEMA.md` §6. Não é um grau de liberdade — é decisão de projeto para o desbalanceamento de 22 % |
| `max_iter` | 2000 | Margem contra não-convergência do `saga` com L1. Um aviso de convergência tornaria os coeficientes não confiáveis, e coeficientes não confiáveis contaminam a explicabilidade |

**Tamanho do grid:** 4 × 2 × 2 = 16 combinações nominais, das quais aproximadamente metade é
válida após o filtro solver × penalty, × 5 *folds* = algumas dezenas de ajustes.

### Por que foi escolhido

1. **É o padrão do domínio.** Escores de risco clínico em uso (Framingham, Wells, CRB-65) são
   lineares, e a razão é auditabilidade: cada variável tem um peso legível por um clínico.
2. **Probabilidades bem calibradas por construção.** A regressão logística otimiza diretamente a
   log-verossimilhança de Bernoulli, o que é uma regra de pontuação própria. Para um sistema em que
   a probabilidade é comunicada ao profissional e entregue a um LLM, calibração não é acessório —
   uma probabilidade mal calibrada é desinformação com aparência de número (`DEFINICAO_DO_PROBLEMA.md` §5.2).
3. **Explicabilidade sem dependência externa.** Os coeficientes **são** a explicação global; a
   contribuição local é `coef × valor_padronizado`. Isso é o que torna a explicabilidade viável
   mesmo quando `shap` não está disponível (ADR-008).
4. **Exigido pelo prompt mestre** §5.5.
5. **Alinhamento estrutural com o gerador.** O rótulo vem de um modelo latente logístico. A LogReg
   é, portanto, o modelo **corretamente especificado** para os termos lineares — o que faz dela uma
   referência de teto para a parte linear do problema. Ver a ressalva em §4 sobre por que isso
   **não** é uma vantagem injusta.

### Limitações conhecidas

- **Não captura as três interações** do gerador (`idade ≥ 35 × has_cronica`,
  `imc ≥ 30 × diabetes_previo`, `gemelaridade × pas_centrada`) sem engenharia manual de features —
  que está **proibida** por `RISCOS_DE_VAZAMENTO.md` **VAZ-07**.
- **Não captura os efeitos de degrau.** Vários termos do gerador são indicadores
  (`abortos ≥ 2`, `hemoglobina < 11`, `glicemia ≥ 92`, `proteinuria ≥ 1+`). A LogReg vê as
  variáveis contínuas e precisa aproximar uma função-degrau por uma reta.
- **Não captura a forma em banheira de `idade`.** O gerador usa dois termos separados
  (`idade < 16` e `(idade − 28)/10` para idade ≥ 28); a LogReg sobre `idade` crua ajusta uma única
  inclinação monotônica.
- Sensível a multicolinearidade — e `idade`, `imc` e `has_cronica` são correlacionadas por
  construção (`DICIONARIO_DE_DADOS.md` §6.2). Coeficientes de variáveis correlacionadas ficam
  instáveis e a interpretação individual de cada um passa a exigir cautela.

Essas quatro limitações **são o desenho do experimento**, não acidentes. Elas definem o espaço em
que o Random Forest pode se destacar.

---

## 5. Modelo #3 — `RandomForestClassifier`

| Atributo | Conteúdo |
|---|---|
| **Papel** | Ensemble não-linear. Captura interações e efeitos de degrau sem engenharia manual |
| **Biblioteca e classe** | `sklearn.ensemble.RandomForestClassifier` |
| **Pré-processamento exigido** | **Tecnicamente nenhum** além da imputação e da codificação ordinal — árvores são invariantes a transformações monotônicas. O `StandardScaler` é aplicado mesmo assim, por decisão de simplicidade do `Pipeline` compartilhado (`DICIONARIO_DE_DADOS.md` §10) |
| **Custo computacional** | Moderado — o mais caro dos quatro. Paralelizável por `n_jobs=-1`. *(estimativa: minutos para o grid completo em CPU — não medido)* |
| **Interpretabilidade** | **Média.** Não tem coeficientes. Depende de `feature_importances_` (global, enviesada para variáveis de alta cardinalidade) e de SHAP `TreeExplainer` (local e **exato** para árvores) |
| **Status** | **Não treinado** |

### Grid de hiperparâmetros — pré-registrado

```python
GRID_RF = {
    'clf__n_estimators':      [200, 500],
    'clf__max_depth':         [None, 8, 16],
    'clf__min_samples_leaf':  [1, 5, 20],
    'clf__max_features':      ['sqrt', 0.5],
    'clf__class_weight':      ['balanced'],
    'clf__random_state':      [42],
}
```

| Hiperparâmetro | Valores | Por quê |
|---|---|---|
| `n_estimators` | 200 / 500 | Abaixo de ~100 a variância entre execuções prejudica a estabilidade do SHAP (`EXPLICABILIDADE.md` §7). Acima de 500 o ganho é marginal e o custo do `TreeExplainer` cresce linearmente |
| `max_depth` | `None` / 8 / 16 | `None` cresce até folhas puras (maior variância). 8 e 16 impõem regularização. Note que **8 já é profundidade suficiente** para representar as 3 interações de dois fatores do gerador — profundidades maiores capturam ruído, e essa é a hipótese que o grid testa |
| `min_samples_leaf` | 1 / 5 / 20 | Controla a granularidade da folha. Com ≈ 1 232 positivos no treino, folhas com 1 amostra memorizam; 20 suaviza. Impacta diretamente a **estabilidade** das explicações locais |
| `max_features` | `'sqrt'` / 0,5 | `sqrt(24) ≈ 5` é o padrão e maximiza a descorrelação entre árvores. 0,5 (12 features) fortalece cada árvore individualmente ao custo de mais correlação entre elas. Com apenas 24 features, o padrão pode ser restritivo demais — por isso o grid testa os dois |
| `class_weight` | `balanced` **fixo** | Mesma justificativa da LogReg |
| `random_state` | 42 **fixo** | Reprodutibilidade. Sem isso, o SHAP e as métricas mudam entre execuções |

**Tamanho do grid:** 2 × 3 × 3 × 2 = **36 combinações** × 5 *folds* = **180 ajustes**. É o item
mais caro do protocolo experimental e justifica `n_jobs=-1`.

### Por que foi escolhido

1. **Captura as três interações do gerador sem que nós as informemos.** É a razão de existir das
   interações (`ESTRATEGIA_DE_ROTULAGEM.md` §2, camada 2): "dar ao Random Forest algo que a
   Regressão Logística não captura sem engenharia manual. Sem elas, os dois modelos empatariam e a
   comparação seria estéril."
2. **Captura efeitos de degrau naturalmente.** Divisões binárias em `abortos ≥ 2` ou
   `glicemia ≥ 92` são exatamente o que uma árvore faz.
3. **`TreeExplainer` é exato e rápido.** Para modelos de árvore, o SHAP não é aproximado — é
   calculado em tempo polinomial com valores exatos. Isso é uma vantagem prática relevante sobre
   qualquer modelo que exigisse `KernelExplainer` (ADR-008).
4. **Robusto a outliers e a escalas heterogêneas.**
5. **Exigido pelo prompt mestre** §5.5.

### Limitações conhecidas

- **Probabilidades tipicamente mal calibradas.** A saída é a fração de árvores que votaram na
  classe, o que costuma ser conservador nos extremos. Por isso `Brier score` e **curva de
  calibração** são métricas obrigatórias do relatório, e por isso o `risco_latente` do gerador
  permite avaliar a calibração contra a probabilidade verdadeira — uma oportunidade que dados reais
  não oferecem.
- **`feature_importances_` (impureza) é enviesada** para variáveis contínuas e de alta cardinalidade.
  `idade` e `pas_mmhg` têm muito mais pontos de corte possíveis que `cardiopatia`. A importância por
  impureza **não** será usada como medida principal; `permutation_importance` e SHAP a substituem
  (`EXPLICABILIDADE.md` §4).
- **Não extrapola.** Predições fora da faixa observada no treino são constantes. Irrelevante aqui,
  porque o domínio é limitado pelo contrato, mas relevante em produção com valor fora de faixa.
- **Menos interpretável que a LogReg.** Não há "o coeficiente de `has_cronica`". É o eixo do
  trade-off de `COMPARACAO_MODELOS.md` §6.
- **Instabilidade da explicação local em floresta pequena.** Com `n_estimators=200` e
  `min_samples_leaf=1`, dois registros quase idênticos podem receber atribuições SHAP visivelmente
  diferentes. Documentado em `EXPLICABILIDADE.md` §7.

---

## 6. Comparabilidade entre os quatro

Condições idênticas obrigatórias, para que a comparação signifique alguma coisa:

| Condição | Aplicação |
|---|---|
| Mesmo dataset | `risco_gestacional_sintetico` v1.0.0, mesmo `dataset_sha256` |
| Mesmo split | Mesmo `split_sha256`; verificado por `scripts/evaluate.py` |
| Mesmo conjunto de features | As 24 do contrato. Nenhum modelo recebe feature derivada (**VAZ-07**) |
| Mesma semente | 42 em tudo |
| Mesmo critério de limiar | Menor `t` com recall ≥ 0,90 **na validação**, para cada modelo individualmente |
| Mesmas métricas | As de `DEFINICAO_DO_PROBLEMA.md` §5.2 |
| Mesmo bootstrap | 1 000 reamostragens, **pareadas** — as mesmas reamostras para todos os modelos |

O bootstrap **pareado** é o detalhe técnico que sustenta a comparação: reamostrar
independentemente para cada modelo produziria intervalos de confiança que ignoram a correlação
entre os erros dos modelos no mesmo conjunto, e a diferença entre dois modelos pareceria menos
significativa do que é. Ver `COMPARACAO_MODELOS.md` §3.

### Ressalvas de comparabilidade a declarar no relatório

Três assimetrias que a tabela comparativa não mostra sozinha:

1. **Modelos #0 e #1 não têm limiar ajustável.** Operam num ponto fixo. A regra "menor limiar com
   recall ≥ 0,90" não se aplica a eles. A comparação com #2 e #3 é, portanto, entre um ponto fixo e
   um ponto escolhido — em favor do ML.
2. **O baseline #1 usa 13 dos 15 critérios** (§3), em ligeira desvantagem.
3. **A LogReg é o modelo corretamente especificado para a parte linear do gerador.** O rótulo vem
   de um modelo latente logístico; os termos lineares da LogReg têm exatamente a forma funcional do
   gerador. Isso lhe dá uma vantagem estrutural que **não existiria em dados reais**, onde ninguém
   conhece a forma funcional verdadeira. Um bom desempenho da LogReg aqui é, em parte, consequência
   de termos escolhido uma sigmoide para gerar os rótulos.

A terceira ressalva é a mais importante e a menos óbvia. Ela precisa aparecer em
`COMPARACAO_MODELOS.md` §5 e em `LIMITACOES_DO_MODELO.md` §2, porque afeta a leitura do resultado
qualquer que ele seja: se a LogReg vencer, parte do mérito é do nosso gerador; se o RF vencer
mesmo com essa desvantagem, o achado é mais forte do que parece.

---

## 7. Modelos considerados e rejeitados

Registro das alternativas avaliadas, com o motivo da exclusão. O escopo obrigatório é definido por
`DEFINICAO_DO_PROBLEMA.md` §4; a rejeição aqui é do escopo do **Ciclo 1**, não definitiva.

### 7.1 `GradientBoostingClassifier` / `HistGradientBoostingClassifier`

| Campo | Conteúdo |
|---|---|
| **O que é** | Ensemble sequencial de árvores rasas, cada uma corrigindo o resíduo da anterior |
| **Por que seria atraente** | Costuma superar Random Forest em dados tabulares; captura as mesmas interações; `HistGradientBoosting` trata `NaN` nativamente, sem imputação; disponível no sklearn, sem dependência nova |
| **Por que foi rejeitado no Ciclo 1** | **(1) Não acrescenta capacidade qualitativamente nova.** Como o RF, é um ensemble de árvores não-linear; o eixo "linear vs. não-linear" já está coberto, e um terceiro modelo do mesmo lado do eixo adiciona custo sem adicionar informação sobre a hipótese. **(2) Multiplica o espaço de busca** — `learning_rate` × `n_estimators` × `max_depth` × `subsample` é combinatoriamente maior que o grid do RF, e o tempo é melhor investido em explicabilidade, testes e integração. **(3) Aumenta a superfície de seleção adaptativa** (**VAZ-04**): cada modelo a mais é uma comparação a mais e um pouco mais de viés de otimismo |
| **Condição de inclusão** | Prevista em `DEFINICAO_DO_PROBLEMA.md` §4: **se LogReg e RF empatarem dentro do intervalo de confiança**. A inclusão seria registrada aqui com data e justificativa, e o grid seria pré-registrado antes do primeiro treino, como os demais |

### 7.2 `XGBoost` / `LightGBM` / `CatBoost`

| Campo | Conteúdo |
|---|---|
| **Por que seria atraente** | Estado da arte em competições com dados tabulares; SHAP `TreeExplainer` nativo e otimizado |
| **Por que foi rejeitado** | **(1) Dependência externa com binários compilados.** O ambiente alvo é Python 3.13 em Windows, e o Docker `ml-only` precisa ser enxuto e construível (ADR-005). Acrescentar uma dependência nativa por um ganho marginal contraria a decisão de manter a imagem em centenas de MB. **(2) O mesmo argumento de 7.1** — não cobre um eixo novo. **(3) Ganho esperado muito pequeno neste problema:** o desempenho de *boosting* sobre RF costuma aparecer em datasets grandes com relações complexas; aqui são 8 000 registros e 24 features, de um processo gerador que **nós** definimos com 3 interações de dois fatores. Não há complexidade oculta a descobrir |

### 7.3 `SVC` (Support Vector Machine)

| Campo | Conteúdo |
|---|---|
| **Por que seria atraente** | Kernel RBF captura não-linearidade; eficaz em espaços de dimensão moderada |
| **Por que foi rejeitado** | **(1) Não produz probabilidade nativamente.** Exige `probability=True`, que roda calibração de Platt por validação cruzada interna — custo alto e probabilidade de segunda mão. Para um sistema em que a **probabilidade calibrada é requisito** (`DEFINICAO_DO_PROBLEMA.md` §5.2), isso é desqualificante. **(2) Explicabilidade ruim.** Não tem coeficientes nem estrutura de árvore; exigiria `KernelExplainer`, que é aproximado e caro — contrariando o ADR-008, que escolheu o caminho de explicabilidade exata. **(3) Escalabilidade** — o custo é aproximadamente quadrático em n; com 5 600 amostras × 5 *folds* × um grid de `C` e `gamma`, o custo supera o do RF sem contrapartida |

### 7.4 Redes neurais (MLP, TabNet, FT-Transformer)

| Campo | Conteúdo |
|---|---|
| **Por que seria atraente** | Capacidade de representação; aproximador universal |
| **Por que foi rejeitado** | **(1) Dados insuficientes.** 5 600 registros de treino com 24 features tabulares é o regime em que redes neurais reconhecidamente **não superam** ensembles de árvores. **(2) Explicabilidade incompatível com o requisito.** Exigiria métodos aproximados (`DeepExplainer`, gradientes integrados) em um domínio clínico onde a explicação precisa ser auditável. **(3) Não determinística sem esforço adicional** — reprodutibilidade bit-a-bit exige controle de sementes em múltiplas bibliotecas e desabilitar otimizações. **(4) Contradiz a arquitetura do projeto.** A ADR-002 escolheu risco gestacional porque o ML **substitui uma decisão que hoje um LLM de 3B toma**; trocar uma caixa-preta neural por outra caixa-preta neural anularia o ganho de auditabilidade que motiva a substituição. **(5) Custo de infraestrutura** — `torch` no Docker levaria a imagem de centenas de MB a vários GB, quebrando o perfil `ml-only` (ADR-005) |

O ponto (4) é o mais decisivo e é específico deste projeto: aqui, interpretabilidade não é
preferência estética — é o requisito que justifica a existência do componente.

### 7.5 Naive Bayes

| Campo | Conteúdo |
|---|---|
| **Por que seria atraente** | Trivial, rápido, probabilístico, mais um baseline |
| **Por que foi rejeitado** | A premissa de independência condicional entre features é **violada por construção neste dataset**: `has_cronica` depende de `idade` e `imc`; `pas_mmhg` depende de `has_cronica`; `glicemia` depende de `diabetes_previo` (`DICIONARIO_DE_DADOS.md` §6.2). Um modelo cuja premissa central sabemos ser falsa produziria probabilidades sistematicamente mal calibradas. Além disso, o papel de baseline já está coberto duas vezes, e a segunda cobertura (#1) é clinicamente significativa — o que um Naive Bayes não seria |

### 7.6 `KNeighborsClassifier`

| Campo | Conteúdo |
|---|---|
| **Por que foi rejeitado** | **(1)** Nenhuma explicabilidade global; a explicação local seria "casos parecidos", inadequada ao requisito de contribuição por variável. **(2)** Mistura de binárias, contagens e contínuas torna a métrica de distância arbitrária — com 10 features binárias, a distância euclidiana sobre valores padronizados não tem interpretação clínica. **(3)** Inferência lenta: exige o dataset de treino em memória, contrariando o empacotamento do modelo em `artifacts/models/` |

### 7.7 Resumo das rejeições

| Modelo | Motivo dominante | Reversível? |
|---|---|---|
| `GradientBoosting` | Não cobre eixo novo; custo de busca | **Sim** — condição declarada em §7.1 |
| `XGBoost` / `LightGBM` / `CatBoost` | Dependência compilada + não cobre eixo novo | Sim, se houver justificativa forte |
| `SVC` | Sem probabilidade nativa; explicabilidade aproximada | Improvável |
| Redes neurais | Dados insuficientes + explicabilidade + contradiz ADR-002 | **Não** neste projeto |
| Naive Bayes | Premissa violada por construção | Não |
| KNN | Sem explicabilidade por variável | Não |

---

## 8. Artefatos por modelo

Cada modelo treinado produzirá:

```
artifacts/models/<nome_do_modelo>/
├── pipeline.joblib        Pipeline completo (pré-processamento + estimador)
├── model_card.json        Metadados (abaixo)
└── cv_results.json        Saída completa do GridSearchCV
```

`model_card.json`:

| Campo | Conteúdo |
|---|---|
| `model_name` | Nome da classe |
| `model_version` | Versão semântica do modelo |
| `dataset_version` | `v1.0.0` — carregar com MAJOR diferente gera erro |
| `dataset_sha256`, `split_sha256` | Rastreabilidade do dado e da partição |
| `hiperparametros` | Os selecionados pela CV |
| `grid_pesquisado` | O grid **pré-registrado** deste documento |
| `threshold` | Limiar da validação (`ESTRATEGIA_TREINO_TESTE.md` §6) |
| `metricas_validacao` | Usadas para escolher o limiar e comparar |
| `features` | Lista ordenada das 24, na ordem canônica |
| `seed` | 42 |
| `treinado_em` | ISO-8601 |
| `commit` | Estado do repositório |
| `aviso_dados_sinteticos` | Texto obrigatório |

Atende a **ML-AC-01** e **ML-AC-05** de `DEFINICAO_DO_PROBLEMA.md` §9.

---

## 9. Estado atual

| Modelo | Implementado | Treinado | Hiperparâmetros selecionados | Limiar | `model_card.json` |
|---|---|---|---|---|---|
| #0 `DummyClassifier` | **Não** | **Não** | n/a | n/a | **Não existe** |
| #1 Baseline por regra | **Não** | **Não** | n/a | n/a | **Não existe** |
| #2 `LogisticRegression` | **Não** | **Não** | **Nenhum** | **Nenhum** | **Não existe** |
| #3 `RandomForestClassifier` | **Não** | **Não** | **Nenhum** | **Nenhum** | **Não existe** |

| Artefato | Estado |
|---|---|
| `lib/ml/train.py` | **Não implementado** |
| `lib/ml/baseline.py` | **Não implementado** |
| `artifacts/models/` | **Não existe** |
| `GridSearchCV` executado | **Nunca** |
| Métricas | **Nenhuma medida** — ver `METRICAS_E_RESULTADOS.md` |

**Status de todos os modelos: `Não treinado`.** Os grids são pré-registros; os custos são
estimativas de ordem de grandeza. **Nenhum resultado existe.**

---

## 10. Documentos relacionados

| Documento | Relação |
|---|---|
| `DEFINICAO_DO_PROBLEMA.md` | Define os 4 modelos, as métricas e o protocolo |
| `ESTRATEGIA_TREINO_TESTE.md` | Define a CV, o limiar e a regra de abertura do teste |
| `METRICAS_E_RESULTADOS.md` | Receberá as métricas de cada modelo |
| `COMPARACAO_MODELOS.md` | Receberá a comparação e o critério pré-registrado |
| `EXPLICABILIDADE.md` | Define o método por modelo (TreeExplainer / coeficientes / permutação) |
| `LIMITACOES_DO_MODELO.md` | Consolida as limitações listadas aqui |
| `RISCOS_DE_VAZAMENTO.md` | **VAZ-07** rege o que é vedado ao configurar estes modelos |
