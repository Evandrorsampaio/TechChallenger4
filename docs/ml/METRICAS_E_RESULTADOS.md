> **Status (2026-09-18):** implementação executada. Números abaixo vêm de `artifacts/metrics/*`. Dataset 100 % sintético — **não é validação clínica**.

## Resultados do teste (n=1200, semente 42, contrato v1.0.0)

Fonte: `artifacts/metrics/<modelo>_teste.json` e `comparacao.json` (`bootstrap_teste`).

| Modelo | Limiar (validação) | Recall + | Precisão + | PR-AUC | ROC-AUC | F1-macro | Acurácia (não decisória) |
|---|---|---|---|---|---|---|---|
| dummy_prior | 0,206 | 1,000 | 0,206 | 0,206 | 0,500 | 0,171 | 0,206 |
| baseline_regra | 0,000 | 1,000 | 0,206 | 0,263 | 0,618 | 0,171 | 0,206 |
| **logistic_regression (vencedor PR-AUC)** | **0,278** | **0,955** | **0,265** | **0,590** | **0,804** | **0,444** | 0,445 |
| random_forest | 0,323 | 0,947 | 0,246 | 0,557 | 0,793 | 0,390 | 0,390 |

LogReg no teste, IC bootstrap 95 % (`comparacao.json`): recall + 0,955 [0,927 ; 0,980]; PR-AUC 0,592 [0,527 ; 0,652].

O limiar da regra ficou 0,0: `predict_proba` é {0,1} e o maior limiar com recall ≥ 0,90 na validação colapsa a “sempre positivo” se o recall da classe positiva da regra no limiar 1,0 cair abaixo do alvo. Isso é limitação da regra + política de limiar, não um bug escondido.

**Decisão:** modelo operacional = `logistic_regression` (maior PR-AUC no teste, recall ≥ 0,90 no limiar da validação). O Random Forest não superou a logística neste gerador. A regra determinística não é um classificador calibrado; o ML supera a regra em PR-AUC (0,59 vs 0,26).

FN LogReg no teste: 11. FP: 655 (custo do recall alto).

# Métricas e Resultados


**Agente responsável:** `MachineLearningAgent`
**Status:** **MODELO DE RELATÓRIO VAZIO** — nenhum modelo treinado, nenhuma métrica calculada
**Base normativa:** `DEFINICAO_DO_PROBLEMA.md` §5, `ESTRATEGIA_TREINO_TESTE.md`, `MODELOS_AVALIADOS.md`

---

> # ⛔ NENHUM MODELO FOI TREINADO. NENHUMA MÉTRICA FOI CALCULADA.
>
> Este documento é uma **estrutura de relatório vazia**. Todas as células de resultado contêm `—`.
>
> **Nenhum número deste documento pode ser preenchido por estimativa, por expectativa, por cálculo
> manual ou por analogia com outro projeto.** Toda célula será preenchida **exclusivamente** a
> partir dos arquivos JSON produzidos por `python scripts/evaluate.py`:
>
> ```
> artifacts/metrics/
> ├── <modelo>_treino.json
> ├── <modelo>_validacao.json
> ├── <modelo>_teste.json
> ├── <modelo>_bootstrap.json
> ├── <modelo>_calibracao.json
> ├── <modelo>_subgrupos.json
> ├── analise_erros.json
> ├── teto_teorico.json
> └── comparacao.json
> ```
>
> **Estado atual:** `artifacts/` não existe. `lib/ml/` não existe. `scripts/evaluate.py` não
> existe. O conjunto de teste **nunca foi aberto**.
>
> Exigência **ML-AC-07** (`DEFINICAO_DO_PROBLEMA.md` §9): *todo número rastreável a um arquivo em
> `artifacts/metrics/`*. Enquanto não houver arquivo, não há número.
>
> **Aviso permanente, que continuará válido depois de preenchido:** estas métricas medirão a
> capacidade do modelo de recuperar um processo gerador que nós mesmos definimos, sobre dados
> **100 % sintéticos**. Elas **não constituem validação clínica**, não são evidência de desempenho
> em população real e não sustentam nenhum uso assistencial.

---

## 1. Identificação da execução

| Campo | Valor |
|---|---|
| Data/hora da avaliação | — |
| Commit do repositório | — |
| `dataset_version` | — |
| `dataset_sha256` | — |
| `split_sha256` | — |
| Semente | — |
| Nº de execuções sobre o teste até esta data | — |
| Motivo registrado desta execução | — |
| Plataforma (SO / Python / scikit-learn) | — |

_PENDENTE — será preenchido por `scripts/evaluate.py` a partir de `artifacts/metrics/` e de `artifacts/data/risco_gestacional_v1.manifest.json`_

---

## 2. Métricas por modelo — treino / validação / teste

Quatro tabelas, uma por modelo. Estrutura idêntica para permitir leitura comparada.

**Convenções:**
- Todas as métricas de classe referem-se à **classe positiva** (`alto_risco = 1`), salvo indicação.
- `Acurácia` é reportada por obrigação e **nunca é critério de escolha** (`DEFINICAO_DO_PROBLEMA.md` §5.3).
- Modelos #0 e #1 não têm limiar ajustável; a coluna "Limiar" traz `n/a`.

### 2.1 Modelo #0 — `DummyClassifier(strategy='prior')`

| Métrica | Treino | Validação | Teste |
|---|---|---|---|
| n | — | — | — |
| Positivos reais | — | — | — |
| Limiar aplicado | n/a | n/a | n/a |
| **Recall (sensibilidade)** | — | — | — |
| **Precisão (VPP)** | — | — | — |
| F1 | — | — | — |
| Especificidade | — | — | — |
| VPN | — | — | — |
| Acurácia *(não é critério)* | — | — | — |
| **PR-AUC** (`average_precision`) | — | — | — |
| ROC-AUC | — | — | — |
| Brier score | — | — | — |

> **Nota obrigatória:** a precisão da classe positiva é **indefinida** para este modelo (nenhuma
> predição positiva ⇒ divisão por zero). A célula deve conter `indefinida`, **nunca** `0,00`
> (`MODELOS_AVALIADOS.md` §2).

_PENDENTE — `artifacts/metrics/dummy_{treino,validacao,teste}.json`_

### 2.2 Modelo #1 — Baseline determinístico (`CRITERIOS_ALTO_RISCO`)

| Métrica | Treino | Validação | Teste |
|---|---|---|---|
| n | — | — | — |
| Positivos reais | — | — | — |
| Limiar aplicado | n/a (ponto fixo) | n/a | n/a |
| Taxa de disparo da regra | — | — | — |
| **Recall (sensibilidade)** | — | — | — |
| **Precisão (VPP)** | — | — | — |
| F1 | — | — | — |
| Especificidade | — | — | — |
| VPN | — | — | — |
| Acurácia *(não é critério)* | — | — | — |
| **PR-AUC** ⚠ | — | — | — |
| ROC-AUC ⚠ | — | — | — |
| Brier score | — | — | — |

> ⚠ **Ressalva obrigatória sobre PR-AUC e ROC-AUC deste modelo.** O baseline produz apenas dois
> valores de "probabilidade" (0,0 e 1,0). Sua curva tem **um único ponto** entre os extremos, e a
> área resultante é interpolação linear. **Não é comparável** com a AUC de modelos que produzem
> probabilidades contínuas. A comparação justa é por recall e precisão no ponto único de operação
> (`MODELOS_AVALIADOS.md` §3).

**Critérios disparados por frequência** (diagnóstico do baseline):

| Critério | Nº de disparos no teste | % dos disparos | Precisão isolada |
|---|---|---|---|
| idade < 16 ou > 35a | — | — | — |
| `has_cronica` | — | — | — |
| DM prévio ou glicemia ≥ 92 | — | — | — |
| `cardiopatia` | — | — | — |
| `nefropatia` | — | — | — |
| `tev_previo` | — | — | — |
| `cesareas_previas ≥ 2` | — | — | — |
| `abortos ≥ 2` | — | — | — |
| `natimorto_previo` | — | — | — |
| `gemelaridade` | — | — | — |
| `imc ≥ 35` | — | — | — |
| `tabagismo` | — | — | — |
| `infeccao_sexual_ativa` | — | — | — |
| malformação fetal prévia | **não mapeável** | n/a | n/a |
| isoimunização Rh | **não mapeável** | n/a | n/a |

_PENDENTE — `artifacts/metrics/baseline_regra_{treino,validacao,teste}.json`_

### 2.3 Modelo #2 — `LogisticRegression`

| Métrica | Treino | Validação | Teste |
|---|---|---|---|
| n | — | — | — |
| Positivos reais | — | — | — |
| **Limiar aplicado** | — | — | — |
| **Recall (sensibilidade)** | — | — | — |
| **Precisão (VPP)** | — | — | — |
| F1 | — | — | — |
| Especificidade | — | — | — |
| VPN | — | — | — |
| Acurácia *(não é critério)* | — | — | — |
| **PR-AUC** | — | — | — |
| ROC-AUC | — | — | — |
| Brier score | — | — | — |

| Campo | Valor |
|---|---|
| Hiperparâmetros selecionados pela CV | — |
| `average_precision` médio na CV (5 *folds*) | — |
| Desvio-padrão entre *folds* | — |
| Convergiu sem aviso? | — |

_PENDENTE — `artifacts/metrics/logreg_{treino,validacao,teste}.json`, `artifacts/models/logreg/cv_results.json`_

### 2.4 Modelo #3 — `RandomForestClassifier`

| Métrica | Treino | Validação | Teste |
|---|---|---|---|
| n | — | — | — |
| Positivos reais | — | — | — |
| **Limiar aplicado** | — | — | — |
| **Recall (sensibilidade)** | — | — | — |
| **Precisão (VPP)** | — | — | — |
| F1 | — | — | — |
| Especificidade | — | — | — |
| VPN | — | — | — |
| Acurácia *(não é critério)* | — | — | — |
| **PR-AUC** | — | — | — |
| ROC-AUC | — | — | — |
| Brier score | — | — | — |

| Campo | Valor |
|---|---|
| Hiperparâmetros selecionados pela CV | — |
| `average_precision` médio na CV (5 *folds*) | — |
| Desvio-padrão entre *folds* | — |
| Diferença treino − teste em PR-AUC (*overfitting*) | — |

_PENDENTE — `artifacts/metrics/rf_{treino,validacao,teste}.json`, `artifacts/models/rf/cv_results.json`_

---

## 3. Matrizes de confusão

Uma por modelo, no **conjunto de teste**, no limiar operacional. Valores absolutos e normalizados
por linha (isto é, condicionados à classe **real** — a normalização que expõe recall e
especificidade diretamente na diagonal).

### 3.1 Modelo #0 — `DummyClassifier`

**Absoluta:**

| | Predito: habitual | Predito: alto risco | Total |
|---|---|---|---|
| **Real: habitual** | — (VN) | — (FP) | — |
| **Real: alto risco** | — (**FN**) | — (VP) | — |
| **Total** | — | — | — |

**Normalizada por linha:**

| | Predito: habitual | Predito: alto risco |
|---|---|---|
| **Real: habitual** | — | — |
| **Real: alto risco** | — | — |

### 3.2 Modelo #1 — Baseline determinístico

**Absoluta:**

| | Predito: habitual | Predito: alto risco | Total |
|---|---|---|---|
| **Real: habitual** | — (VN) | — (FP) | — |
| **Real: alto risco** | — (**FN**) | — (VP) | — |
| **Total** | — | — | — |

**Normalizada por linha:**

| | Predito: habitual | Predito: alto risco |
|---|---|---|
| **Real: habitual** | — | — |
| **Real: alto risco** | — | — |

### 3.3 Modelo #2 — `LogisticRegression`

**Absoluta:**

| | Predito: habitual | Predito: alto risco | Total |
|---|---|---|---|
| **Real: habitual** | — (VN) | — (FP) | — |
| **Real: alto risco** | — (**FN**) | — (VP) | — |
| **Total** | — | — | — |

**Normalizada por linha:**

| | Predito: habitual | Predito: alto risco |
|---|---|---|
| **Real: habitual** | — | — |
| **Real: alto risco** | — | — |

### 3.4 Modelo #3 — `RandomForestClassifier`

**Absoluta:**

| | Predito: habitual | Predito: alto risco | Total |
|---|---|---|---|
| **Real: habitual** | — (VN) | — (FP) | — |
| **Real: alto risco** | — (**FN**) | — (VP) | — |
| **Total** | — | — | — |

**Normalizada por linha:**

| | Predito: habitual | Predito: alto risco |
|---|---|---|
| **Real: habitual** | — | — |
| **Real: alto risco** | — | — |

> **A célula FN é a mais importante de todas as quatro tabelas.** Cada unidade nela é uma gestante
> de alto risco classificada como habitual, que perderia vigilância intensificada e teria consultas
> espaçadas em 30 dias em vez de 7–14 (`obstetrico.py:276-317`). É o erro de consequência
> potencialmente irreversível, e é a razão de o recall ser a métrica primária
> (`DEFINICAO_DO_PROBLEMA.md` §5.1).

_PENDENTE — `artifacts/metrics/<modelo>_teste.json`, chave `matriz_confusao`_

---

## 4. Precisão, recall e F1 por classe

Relatório por classe no **teste**, incluindo médias macro e ponderada.

### 4.1 Modelo #0 — `DummyClassifier`

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| `habitual` (0) | — | — | — | — |
| `alto_risco` (1) | — | — | — | — |
| **Média macro** | — | — | — | — |
| **Média ponderada** | — | — | — | — |

### 4.2 Modelo #1 — Baseline determinístico

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| `habitual` (0) | — | — | — | — |
| `alto_risco` (1) | — | — | — | — |
| **Média macro** | — | — | — | — |
| **Média ponderada** | — | — | — | — |

### 4.3 Modelo #2 — `LogisticRegression`

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| `habitual` (0) | — | — | — | — |
| `alto_risco` (1) | — | — | — | — |
| **Média macro** | — | — | — | — |
| **Média ponderada** | — | — | — | — |

### 4.4 Modelo #3 — `RandomForestClassifier`

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| `habitual` (0) | — | — | — | — |
| `alto_risco` (1) | — | — | — | — |
| **Média macro** | — | — | — | — |
| **Média ponderada** | — | — | — | — |

> **Nota de leitura:** a **média ponderada** é dominada pela classe `habitual` (≈ 78 % do suporte)
> e, por isso, é quase tão enganosa quanto a acurácia neste problema. Ela é reportada por
> completude. A comparação entre modelos usa as métricas da **classe positiva**.

_PENDENTE — `artifacts/metrics/<modelo>_teste.json`, chave `classification_report`_

---

## 5. ROC-AUC e PR-AUC

### 5.1 Tabela comparativa

| Modelo | ROC-AUC (teste) | IC 95 % | PR-AUC (teste) | IC 95 % | Linha de base PR-AUC |
|---|---|---|---|---|---|
| #0 `DummyClassifier` | — | — | — | — | — |
| #1 Baseline por regra ⚠ | — | — | — | — | — |
| #2 `LogisticRegression` | — | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — | — |

⚠ Ver ressalva de §2.2: as áreas do modelo #1 não são comparáveis às dos modelos probabilísticos.

**Linha de base da PR-AUC:** para um classificador aleatório, a PR-AUC esperada é igual à
prevalência da classe positiva. A coluna registra a prevalência **observada no teste**, para que a
PR-AUC de cada modelo seja lida contra a referência correta.

### 5.2 Por que PR-AUC é a métrica de ranqueamento principal

Com ≈ 22 % de positivos, a ROC-AUC é pouco sensível a aumentos absolutos grandes de falsos
positivos, porque a taxa de falso-positivo tem os ≈ 78 % de negativos no denominador. A PR-AUC usa
a precisão, cujo denominador são as predições positivas — e é essa a quantidade que determina a
carga assistencial real de encaminhamentos desnecessários.

### 5.3 Curvas

| Arquivo | Conteúdo |
|---|---|
| `artifacts/metrics/curvas_roc.png` | ROC dos 4 modelos sobrepostas, com a diagonal |
| `artifacts/metrics/curvas_pr.png` | Precisão-Recall dos 4, com a linha da prevalência |
| `artifacts/metrics/curvas_pr.json` | Pontos das curvas, para reprodução |

**Estado:** nenhum arquivo existe.

_PENDENTE — `scripts/evaluate.py`_

---

## 6. Brier score e calibração

### 6.1 Brier score

| Modelo | Brier (teste) | IC 95 % | Brier de referência (prevalência constante) |
|---|---|---|---|
| #0 `DummyClassifier` | — | — | — |
| #1 Baseline por regra | — | — | — |
| #2 `LogisticRegression` | — | — | — |
| #3 `RandomForestClassifier` | — | — | — |

Menor é melhor. O Brier de referência é o de um modelo que prevê sempre a prevalência do treino —
um modelo com Brier pior que a referência produz probabilidades **piores que não ter modelo**.

### 6.2 Curva de calibração (10 faixas de probabilidade)

**Modelo #2 — `LogisticRegression`:**

| Faixa de probabilidade prevista | n | Média prevista | Frequência observada | Desvio |
|---|---|---|---|---|
| [0,0 – 0,1) | — | — | — | — |
| [0,1 – 0,2) | — | — | — | — |
| [0,2 – 0,3) | — | — | — | — |
| [0,3 – 0,4) | — | — | — | — |
| [0,4 – 0,5) | — | — | — | — |
| [0,5 – 0,6) | — | — | — | — |
| [0,6 – 0,7) | — | — | — | — |
| [0,7 – 0,8) | — | — | — | — |
| [0,8 – 0,9) | — | — | — | — |
| [0,9 – 1,0] | — | — | — | — |

**Modelo #3 — `RandomForestClassifier`:**

| Faixa de probabilidade prevista | n | Média prevista | Frequência observada | Desvio |
|---|---|---|---|---|
| [0,0 – 0,1) | — | — | — | — |
| [0,1 – 0,2) | — | — | — | — |
| [0,2 – 0,3) | — | — | — | — |
| [0,3 – 0,4) | — | — | — | — |
| [0,4 – 0,5) | — | — | — | — |
| [0,5 – 0,6) | — | — | — | — |
| [0,6 – 0,7) | — | — | — | — |
| [0,7 – 0,8) | — | — | — | — |
| [0,8 – 0,9) | — | — | — | — |
| [0,9 – 1,0] | — | — | — | — |

| Métrica de calibração | #2 LogReg | #3 RF |
|---|---|---|
| Erro de calibração esperado (ECE) | — | — |
| Erro de calibração máximo (MCE) | — | — |
| Inclinação da reta de calibração (ideal = 1,0) | — | — |
| Intercepto (ideal = 0,0) | — | — |

### 6.3 Calibração contra `risco_latente` — verificação exclusiva de dado sintético

Esta comparação **não é possível com dados reais** e é uma das poucas vantagens epistêmicas do
dataset sintético: conhecemos a probabilidade verdadeira de cada registro.

| Modelo | Correlação (Pearson) com `risco_latente` | Correlação (Spearman) | EAM \|p̂ − p_verdadeiro\| | Viés médio (p̂ − p) |
|---|---|---|---|---|
| #2 `LogisticRegression` | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — |

O **erro absoluto médio contra `risco_latente`** é a medida mais direta de qualidade da
probabilidade que este projeto pode produzir: ela compara a estimativa do modelo com a quantidade
que a gerou, sem passar pelo rótulo amostrado. Um modelo pode ter recall alto e ainda assim estimar
mal a probabilidade — e é a probabilidade, não o rótulo, que é comunicada ao profissional e
entregue ao LLM.

> **Por que isto não é vazamento:** `risco_latente` é usada **apenas na avaliação, depois do
> treino**, e nunca entra em `X` (`RISCOS_DE_VAZAMENTO.md` **VAZ-01**). Usá-la para medir
> calibração é auditoria; usá-la para treinar seria fraude.

_PENDENTE — `artifacts/metrics/<modelo>_calibracao.json`_

---

## 7. Especificidade e VPN

| Modelo | Especificidade | IC 95 % | VPN | IC 95 % | VPP (precisão) | IC 95 % |
|---|---|---|---|---|---|---|
| #0 `DummyClassifier` | — | — | — | — | indefinida | n/a |
| #1 Baseline por regra | — | — | — | — | — | — |
| #2 `LogisticRegression` | — | — | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — | — | — |

**Definições, para que a leitura não dependa de memória:**

| Métrica | Fórmula | Pergunta clínica que responde |
|---|---|---|
| Recall / sensibilidade | VP / (VP + FN) | Das gestantes que **são** alto risco, quantas o modelo captura? |
| Especificidade | VN / (VN + FP) | Das gestantes que **não são** alto risco, quantas o modelo libera corretamente? |
| VPP / precisão | VP / (VP + FP) | Das que o modelo **marcou** como alto risco, quantas realmente são? |
| VPN | VN / (VN + FN) | Das que o modelo **liberou**, quantas realmente eram habituais? |

> **VPP e VPN dependem da prevalência**; sensibilidade e especificidade não. Como a prevalência
> aqui é uma **escolha de projeto** (≈ 22 %, `ESTRATEGIA_DE_ROTULAGEM.md` §6.4) e não uma medida
> epidemiológica, **VPP e VPN não transferem para nenhum serviço real**, nem mesmo em ordem de
> grandeza. Um serviço com prevalência de 10 % teria VPP substancialmente menor com exatamente o
> mesmo modelo. Esta ressalva é obrigatória sempre que estes números forem citados.

_PENDENTE — `artifacts/metrics/<modelo>_teste.json`_

---

## 8. Intervalos de confiança por bootstrap

**Protocolo:** 1 000 reamostragens com reposição do conjunto de **teste**, estratificadas pelo
alvo, semente 42. As **mesmas reamostras** são usadas para todos os modelos (bootstrap **pareado**),
para que as diferenças entre modelos possam ser avaliadas com a correlação dos erros preservada.

| Modelo | Métrica | Ponto | IC 95 % inferior | IC 95 % superior | Largura |
|---|---|---|---|---|---|
| #0 `DummyClassifier` | Recall | — | — | — | — |
| #0 | Precisão | — | — | — | — |
| #0 | PR-AUC | — | — | — | — |
| #1 Baseline | Recall | — | — | — | — |
| #1 | Precisão | — | — | — | — |
| #1 | Especificidade | — | — | — | — |
| #2 LogReg | Recall | — | — | — | — |
| #2 | Precisão | — | — | — | — |
| #2 | PR-AUC | — | — | — | — |
| #2 | ROC-AUC | — | — | — | — |
| #2 | Brier | — | — | — | — |
| #3 RF | Recall | — | — | — | — |
| #3 | Precisão | — | — | — | — |
| #3 | PR-AUC | — | — | — | — |
| #3 | ROC-AUC | — | — | — | — |
| #3 | Brier | — | — | — | — |

**Diferenças pareadas entre modelos** estão em `COMPARACAO_MODELOS.md` §3, não aqui.

_PENDENTE — `artifacts/metrics/<modelo>_bootstrap.json`_

---

## 9. Análise de erros

Exigida por **ML-AC-04** (`DEFINICAO_DO_PROBLEMA.md` §9). Realizada sobre o **modelo escolhido**,
no conjunto de teste.

### 9.1 Falsos negativos — o erro que mais importa

**Perguntas que esta seção deve responder:**

1. Quantos falsos negativos ocorreram, em absoluto e em proporção dos positivos reais?
2. Quais fatores de risco estavam **presentes** nesses casos e foram ignorados pelo modelo?
3. Algum falso negativo tinha um fator de risco **maior** (`pre_eclampsia_previa`, `cardiopatia`,
   `nefropatia`, `has_cronica`, `diabetes_previo`, `gemelaridade`)? Se sim, é o subgrupo mais grave
   e exige análise caso a caso.
4. Qual a distribuição do `risco_latente` **verdadeiro** dos falsos negativos? Eram casos de risco
   genuinamente alto que o modelo errou, ou casos de `p` baixo que o Bernoulli sorteou como
   positivos — isto é, **erro de Bayes irredutível** e não falha do modelo?
5. Qual a probabilidade prevista? Ficaram **logo abaixo** do limiar ou muito distantes dele?
6. Os falsos negativos têm mais campos imputados que a média? Se sim, a perda de informação por
   ausência é uma causa identificável.
7. O **baseline determinístico** teria capturado algum deles? Essa é a pergunta decisiva para
   justificar a substituição do sistema atual.

**Resumo quantitativo:**

| Item | Valor |
|---|---|
| Total de falsos negativos | — |
| % dos positivos reais | — |
| Com ≥ 1 fator de risco maior | — |
| **`risco_latente` verdadeiro mediano dos FN** | — |
| `risco_latente` verdadeiro mediano dos VP | — |
| % de FN com `risco_latente < 0,30` (provável erro de Bayes) | — |
| Probabilidade prevista mediana dos FN | — |
| Distância mediana até o limiar | — |
| % com ao menos um campo imputado | — |
| Idem, na população geral do teste | — |
| **FN que o baseline #1 teria capturado** | — |
| **FN que o baseline #1 também erraria** | — |

**Fatores de risco presentes nos falsos negativos:**

| Fator | Nº de FN com o fator | % dos FN | % na população do teste |
|---|---|---|---|
| `pre_eclampsia_previa` | — | — | — |
| `cardiopatia` | — | — | — |
| `nefropatia` | — | — | — |
| `has_cronica` | — | — | — |
| `diabetes_previo` | — | — | — |
| `gemelaridade` | — | — | — |
| `tev_previo` | — | — | — |
| `natimorto_previo` | — | — | — |
| `pas_mmhg ≥ 140` | — | — | — |
| `imc ≥ 35` | — | — | — |
| `abortos ≥ 2` | — | — | — |
| `idade > 35` ou `< 16` | — | — | — |
| `infeccao_sexual_ativa` | — | — | — |
| `proteinuria ≥ 1+` | — | — | — |
| **Nenhum fator maior** | — | — | — |

**Casos individuais de maior gravidade** (FN com fator de risco maior presente):

| `registro_id` | Fatores maiores | Prob. prevista | Limiar | `risco_latente` | Baseline capturaria? |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
| — | — | — | — | — | — |

> A pergunta 4 é a que separa uma análise honesta de uma superficial. Uma parte dos falsos
> negativos será **inevitável por construção**: o rótulo é amostrado de `Bernoulli(p)`, então um
> registro com `p = 0,15` pode legitimamente ter `alto_risco = 1`, e **nenhum** classificador o
> preveria — nem o próprio processo gerador. Atribuir esses casos a falha do modelo seria tão
> incorreto quanto ignorar os falsos negativos de `p` alto, que são falha real.

_PENDENTE — `artifacts/metrics/analise_erros.json`, chave `falsos_negativos`_

### 9.2 Falsos positivos

**Perguntas que esta seção deve responder:**

1. Quantos, em absoluto e em proporção dos negativos reais?
2. O modelo está **superponderando alguma variável isolada**? Há um fator presente em
   desproporção nos FP?
3. Qual o `risco_latente` verdadeiro dos FP? Eram casos de risco genuinamente alto que o Bernoulli
   sorteou como negativos (erro de Bayes, "falso" falso positivo) ou erro real do modelo?
4. Qual a carga assistencial adicional estimada? (Em encaminhamentos excedentes — não em custo
   financeiro, que este projeto não tem base para estimar.)
5. Como se compara com a taxa de falsos positivos do baseline determinístico? **É aqui que o ganho
   esperado do ML deve aparecer**, dado que o recall foi fixado em ≥ 0,90 para todos.

**Resumo quantitativo:**

| Item | Valor |
|---|---|
| Total de falsos positivos | — |
| % dos negativos reais (1 − especificidade) | — |
| `risco_latente` verdadeiro mediano dos FP | — |
| % de FP com `risco_latente > 0,50` (provável erro de Bayes) | — |
| Probabilidade prevista mediana | — |
| Fator isolado mais frequente | — |
| FP com **exatamente um** fator de risco | — |
| **FP do baseline #1, no mesmo teste** | — |
| **Redução absoluta de FP (baseline − modelo escolhido)** | — |
| **Redução relativa** | — |

**Fatores presentes nos falsos positivos:**

| Fator | Nº de FP com o fator | % dos FP | % na população do teste | Razão de sobrerrepresentação |
|---|---|---|---|---|
| `has_cronica` | — | — | — | — |
| `diabetes_previo` | — | — | — | — |
| `idade > 35` | — | — | — | — |
| `imc ≥ 30` | — | — | — | — |
| `pas_mmhg ≥ 140` | — | — | — | — |
| `tabagismo` | — | — | — | — |
| `abortos ≥ 2` | — | — | — | — |
| `cesareas_previas ≥ 2` | — | — | — | — |

_PENDENTE — `artifacts/metrics/analise_erros.json`, chave `falsos_positivos`_

---

## 10. Análise por subgrupo

Exigida por `DEFINICAO_DO_PROBLEMA.md` §5.4. Desempenho desigual entre subgrupos é um risco de
equidade e precisa ser medido, não presumido ausente.

### 10.1 Por faixa etária

| Faixa | n | Positivos | Prevalência | Recall | IC 95 % | Precisão | IC 95 % | Especificidade |
|---|---|---|---|---|---|---|---|---|
| < 16 anos | — | — | — | — | — | — | — | — |
| 16–19 | — | — | — | — | — | — | — | — |
| 20–34 | — | — | — | — | — | — | — | — |
| 35–39 | — | — | — | — | — | — | — | — |
| ≥ 40 | — | — | — | — | — | — | — | — |
| **Global** | — | — | — | — | — | — | — | — |

### 10.2 Por idade gestacional

| Faixa | n | Positivos | Prevalência | Recall | IC 95 % | Precisão | IC 95 % | Especificidade |
|---|---|---|---|---|---|---|---|---|
| 1º trimestre (4–13 sem) | — | — | — | — | — | — | — | — |
| 2º trimestre (14–27 sem) | — | — | — | — | — | — | — | — |
| 3º trimestre (28–42 sem) | — | — | — | — | — | — | — | — |
| **Global** | — | — | — | — | — | — | — | — |

> **Controle negativo embutido.** `ig_semanas` tem **β = 0** no processo gerador
> (`DICIONARIO_DE_DADOS.md` §3.4): a idade gestacional **não afeta o risco verdadeiro**. Portanto,
> a prevalência real deve ser estatisticamente igual nos três trimestres, e qualquer diferença de
> desempenho entre eles é **artefato do modelo ou ruído amostral**, nunca sinal clínico.
>
> Há uma exceção que torna a análise interessante: `ig_semanas` **determina o mecanismo MAR** de
> `proteinuria_fita` (30 % de ausência no 1º trimestre contra 5 % depois). Se o desempenho cair no
> 1º trimestre, a hipótese principal é **perda de informação por ausência**, não efeito da IG.

### 10.3 Por presença de dados imputados

| Grupo | n | Recall | Precisão | Brier |
|---|---|---|---|---|
| Sem nenhum campo imputado | — | — | — | — |
| 1 campo imputado | — | — | — | — |
| ≥ 2 campos imputados | — | — | — | — |

Esta é a medida direta do **custo da imputação**. Ela informa a decisão de interface: se o
desempenho cair de forma relevante com campos imputados, a interface deve destacar a imputação com
mais ênfase (`INTERPRETACAO_DAS_PREDICOES.md` §5).

### 10.4 Subgrupos de tamanho insuficiente

| Subgrupo | n esperado no teste | Análise viável? |
|---|---|---|
| `cardiopatia = 1` | — | **Provavelmente não** — ver nota |
| `nefropatia = 1` | — | **Provavelmente não** |
| `gemelaridade = 1` | — | **Provavelmente não** |
| `tev_previo = 1` | — | **Provavelmente não** |
| `idade < 16` | — | — |

> **Limitação antecipada** (`ESTRATEGIA_TREINO_TESTE.md` §4.2): com prevalências geradoras entre
> 1,2 % e 2,0 %, esses subgrupos terão poucas dezenas de casos no teste. Um recall calculado sobre
> ~18 observações tem intervalo de confiança largo demais para ser informativo.
>
> **A conduta obrigatória é reportar `n` e declarar a análise inconclusiva** — nunca reportar o
> ponto isolado como se fosse uma medida de desempenho no subgrupo. Esta é uma decisão tomada
> **antes** de ver os números, o que a torna um compromisso e não uma desculpa.

_PENDENTE — `artifacts/metrics/<modelo>_subgrupos.json`_

---

## 11. Teto teórico de desempenho — erro de Bayes do gerador

Seção que só é possível porque os dados são sintéticos e `risco_latente` é conhecido.

### 11.1 O que é o teto

O rótulo é **amostrado** de `Bernoulli(p)`, não limiarizado (`ESTRATEGIA_DE_ROTULAGEM.md` §2,
camada 3). Portanto existe **erro irredutível**: mesmo um oráculo que conhecesse `p` exatamente
para cada registro não conseguiria prever `y` com certeza.

O **classificador de Bayes** — o melhor classificador possível — prevê `1` quando `p > t` para o
limiar `t` escolhido. Seu desempenho é o teto absoluto. Nenhum dos quatro modelos pode superá-lo,
e a distância até ele é a medida correta de quanto ainda havia para aprender.

### 11.2 Classificador de Bayes (oráculo) no conjunto de teste

| Métrica | Oráculo em `t` = 0,5 | Oráculo no limiar do modelo escolhido |
|---|---|---|
| Recall | — | — |
| Precisão | — | — |
| F1 | — | — |
| Especificidade | — | — |
| Acurácia | — | — |
| **ROC-AUC do oráculo** | — | — |
| **PR-AUC do oráculo** | — | — |
| Brier score do oráculo | — | — |

**Quantidades derivadas:**

| Item | Valor |
|---|---|
| Erro de Bayes (taxa de erro mínima possível em `t` = 0,5) | — |
| Entropia média de Bernoulli, `E[H(p)]` | — |
| % de registros com `risco_latente` entre 0,3 e 0,7 (zona irredutível) | — |
| Pares de features idênticas com rótulos opostos | — |

O último item vem de `QUALIDADE_DOS_DADOS.md` §4.5 e é um limite **empírico** complementar: dois
registros com features idênticas e rótulos opostos são impossíveis de acertar simultaneamente por
qualquer função determinística das features.

### 11.3 Distância de cada modelo até o teto

| Modelo | PR-AUC | PR-AUC do oráculo | Lacuna absoluta | % do teto atingida |
|---|---|---|---|---|
| #0 `DummyClassifier` | — | — | — | — |
| #1 Baseline por regra | — | — | — | — |
| #2 `LogisticRegression` | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — |

### 11.4 Recuperação dos parâmetros do gerador (diagnóstico)

Comparação entre os coeficientes **estimados** pela Regressão Logística e os β **do gerador**. É
análise **pós-treino** e legítima; usar os β antes ou durante o ajuste seria **VAZ-07**.

| Termo | β do gerador | Coef. estimado (escala original) | Razão | Sinal correto? |
|---|---|---|---|---|
| intercepto | −3,10 | — | — | — |
| `has_cronica` | +1,60 | — | — | — |
| `diabetes_previo` | +1,45 | — | — | — |
| `pre_eclampsia_previa` | +1,70 | — | — | — |
| `cardiopatia` | +1,90 | — | — | — |
| `nefropatia` | +1,75 | — | — | — |
| `gemelaridade` | +1,30 | — | — | — |
| `tev_previo` | +1,20 | — | — | — |
| `natimorto_previo` | +1,10 | — | — | — |
| `pas_mmhg` (por 10 mmHg) | +0,38 | — | — | — |
| `pad_mmhg` (por 10 mmHg) | +0,32 | — | — | — |
| `imc_pre_gestacional` (por 5) | +0,34 | — | — | — |
| `tabagismo` | +0,45 | — | — | — |
| `infeccao_sexual_ativa` | +0,85 | — | — | — |
| `escolaridade_anos` (por ano) | −0,04 | — | — | — |

> **Como ler esta tabela quando estiver preenchida.** Não se espera correspondência próxima, e a
> divergência **não** é defeito. Cinco razões conhecidas de discrepância, todas estruturais:
> (1) vários termos do gerador são **indicadores** (`abortos ≥ 2`, `hemoglobina < 11`,
> `glicemia ≥ 92`, `proteinuria ≥ 1+`, `idade < 16`) enquanto a LogReg recebe a variável contínua;
> (2) as **três interações** não estão no modelo estimado; (3) a **regularização** contrai os
> coeficientes em direção a zero, tanto mais quanto menor o `C` selecionado; (4) `class_weight='balanced'`
> reponderá as classes e **desloca o intercepto**, tornando-o não comparável diretamente com β₀;
> (5) `idade` entra no gerador por dois termos separados e na LogReg por um só.
>
> O que **é** informativo: o **sinal** de cada coeficiente e a **ordenação relativa** das
> magnitudes entre as binárias, que não sofrem os problemas (1) e (5).

_PENDENTE — `artifacts/metrics/teto_teorico.json`_

---

## 12. Procedimento de preenchimento

| Regra | Detalhe |
|---|---|
| Origem única | Todo número vem de `artifacts/metrics/*.json` produzido por `scripts/evaluate.py` |
| Sem digitação manual | O preenchimento é feito por script de renderização; um valor ausente do JSON não pode aparecer no Markdown |
| Sem arredondamento manual | A precisão é a do JSON |
| Rastreabilidade | Cada seção nomeia o arquivo e a chave de origem |
| Verificação | `tests/unit/test_documentos_sem_metrica_orfa.py` — todo número em célula de resultado tem chave correspondente no JSON (`RISCOS_DE_VAZAMENTO.md` **VAZ-12**) |
| Execução única do teste | Se `registro_avaliacoes.jsonl` tiver mais de uma entrada, **todas** aparecem em §1, com os motivos (`ESTRATEGIA_TREINO_TESTE.md` §8.4) |

---

## 13. Estado atual

| Item | Estado |
|---|---|
| Dataset gerado | **Não** |
| Modelos treinados | **0 de 4** |
| `GridSearchCV` executado | **Não** |
| Limiar calibrado | **Não** |
| **Conjunto de teste aberto** | **NUNCA** |
| `artifacts/metrics/` | **Não existe** |
| `scripts/evaluate.py` | **Não implementado** |
| Métricas calculadas | **Nenhuma** |
| Células preenchidas neste documento | **Zero** |

> **Confirmação explícita:** este documento **não contém nenhum resultado**. Todos os números que
> nele aparecem são (a) parâmetros de projeto pré-declarados — 22 %, 0,90, 1 000 reamostragens,
> semente 42; (b) os coeficientes β do gerador, publicados em `ESTRATEGIA_DE_ROTULAGEM.md` §2 como
> especificação; ou (c) rótulos de faixa em cabeçalhos de tabela. **Nenhum é uma medida.**
