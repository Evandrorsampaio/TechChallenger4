> **Status (2026-09-18):** `lib/ml/explain.py` implementado. SHAP **não** está instalado neste ambiente (`SHAP_DISPONIVEL=False`). Exemplo local (LogReg, `coef_linear`) = `artifacts/explainability/shap_exemplo.json`. Importância global (RF, permutação, n=200 validação, 2 repeats) = `artifacts/explainability/importancia_global.json`.

As variáveis que mais contribuíram para esta classificação (cópia literal do JSON, caso D1-like, LogReg):

| feature | value | contribution | direction |
|---|---|---|---|
| pas_mmhg | 118 | 0.21195115104495132 | aumenta |
| imc_pre_gestacional | 24.0 | -0.1352754033297112 | reduz |
| glicemia_jejum_mg_dl | 82.0 | -0.086775660296531 | reduz |
| escolaridade_anos | 12 | -0.06115479792729405 | reduz |
| cesareas_previas | 0 | -0.03094286079170258 | reduz |

Linguagem permitida: “As variáveis que mais contribuíram para esta classificação foram…”. Proibido: causalidade (“causou o risco”).

# Estratégia de Explicabilidade


**Agente responsável:** `ExplainabilityAgent`
**Status:** Estratégia definida — **nada implementado, nenhuma explicação gerada**
**Base normativa:** **ADR-008** (SHAP com fallback obrigatório), prompt mestre §5.6
**Implementação alvo:** `lib/ml/explain.py`, `tests/unit/test_explicabilidade_reconcilia.py`

---

> ## ⚠ NENHUMA EXPLICAÇÃO FOI GERADA
>
> `lib/ml/explain.py` não existe. Nenhum modelo foi treinado, portanto nenhum valor SHAP, nenhuma
> importância por permutação e nenhum coeficiente foram calculados.
>
> Este documento define **como** a explicabilidade será produzida e validada. Ele **não** contém
> nenhuma importância de variável, nenhum ranking de features e nenhum exemplo de explicação com
> valores reais.
>
> Quando `MODELOS_AVALIADOS.md` §4 antecipa que `pre_eclampsia_previa` (β = +1,70) deve aparecer no
> topo das explicações, isso é **consequência aritmética de um coeficiente que nós escolhemos** e
> serve como verificação de sanidade do explicador — **não** é um resultado observado.

---

## 1. Por que a explicabilidade é requisito, não acessório

Neste sistema, a explicação tem três funções distintas, e só a primeira é a usual:

| Função | Para quem | O que perde sem ela |
|---|---|---|
| Permitir que o profissional **discorde do modelo com fundamento** | Obstetra | Sem saber o que pesou, discordar vira intuição contra número — e o número costuma ganhar |
| Tornar a predição **auditável** | Governança, revisão de casos | Sem rastro por variável, a auditoria registra que houve predição, não por quê |
| Alimentar o **LLM** com conteúdo verificável | Camada de síntese | Sem contribuições estruturadas, o LLM teria que inventar a justificativa — exatamente o que ADR-007 impede |

A segunda função conecta-se à motivação original do projeto. Hoje `_avaliar_risco_gestacional`
(`obstetrico.py:124-144`) devolve uma lista de `fatores` **gerada pelo LLM** — texto que o modelo
pode inventar, sem correspondência garantida com nenhum cálculo. Substituir isso por contribuições
numéricas derivadas do próprio classificador é parte central do ganho de auditabilidade que a
ADR-002 busca.

---

## 2. Técnicas escolhidas

### 2.1 Visão geral

| Modelo | Método primário | Escopo | Exato? | Fallback |
|---|---|---|---|---|
| #3 `RandomForestClassifier` | **SHAP `TreeExplainer`** | Local + global | **Sim** — exato para árvores | `permutation_importance` (global) |
| #2 `LogisticRegression` | **Coeficientes / razão de chances** (global) e **`coef × valor_padronizado`** (local) | Local + global | **Sim** — é o próprio modelo | Nenhum necessário |
| #1 Baseline por regra | **Lista literal dos critérios disparados** | Local | **Sim** — é a própria regra | Nenhum necessário |
| #0 `DummyClassifier` | "Prevê sempre a classe majoritária" | — | Trivial | Nenhum |

### 2.2 `TreeExplainer` para o Random Forest

**Por que SHAP e por que esta variante.**

`TreeExplainer` calcula os valores de Shapley **exatamente** para modelos baseados em árvores, em
tempo polinomial. Não é aproximação por amostragem — é o valor exato, sob a formulação de valor
esperado condicional que a implementação adota.

Isso o distingue de `KernelExplainer`, que é agnóstico ao modelo, aproximado e caro. A diferença
é decisiva num domínio clínico: uma explicação aproximada acrescenta uma segunda fonte de erro
(além do modelo) e torna a reconciliação de §6 impossível de verificar com tolerância estreita.

**Propriedades que interessam aqui:**

| Propriedade | Consequência prática |
|---|---|
| **Aditividade local** | `valor_base + Σ contribuições = saída do modelo`. É o que permite a validação de §6 |
| **Eficiência** (axioma de Shapley) | A soma das contribuições é exatamente a diferença entre a predição e a média — não sobra nem falta crédito |
| **Consistência** | Se um modelo passa a depender mais de uma feature, a contribuição dela não diminui |
| **Local e global com o mesmo método** | A importância global é derivada da média dos \|valores SHAP\| locais — não é uma métrica diferente com semântica diferente |

**Configuração planejada:**

```python
explainer = shap.TreeExplainer(
    modelo,
    feature_perturbation='tree_path_dependent',   # não exige dataset de fundo
)
```

`tree_path_dependent` usa a estrutura das árvores e as contagens de amostras que já estão no modelo
treinado, em vez de um conjunto de fundo. Duas razões: (a) evita a escolha arbitrária de um
*background set*, que muda os valores; (b) torna a explicação **reprodutível** — dois cálculos com
o mesmo modelo e a mesma entrada devolvem o mesmo resultado, o que é requisito para a auditoria.

### 2.3 Coeficientes e contribuição linear para a Regressão Logística

Para um modelo linear, **o modelo é a explicação**. Não há necessidade de método externo.

**Explicação global — razões de chance:**

```
razão_de_chances_i = exp(coef_i)
```

Como as features passam por `StandardScaler`, `exp(coef_i)` é a **razão de chances por
desvio-padrão** da feature *i*, não por unidade original. Isso tem duas consequências que precisam
ser comunicadas e nunca omitidas:

1. As magnitudes são **comparáveis entre features**, que é justamente o objetivo da padronização.
2. Elas **não** são interpretáveis em unidades clínicas diretamente. "Razão de chances de 1,45 por
   desvio-padrão de PAS" exige saber quanto vale um desvio-padrão de PAS no dataset para ter
   significado clínico.

Por isso o relatório apresenta **as duas escalas**: o coeficiente padronizado (para ranquear) e o
coeficiente reconvertido para a unidade original, `coef_i / σ_i` (para ler clinicamente).

**Explicação local — contribuição linear:**

```
contribuição_i = coef_i × valor_padronizado_i
logit = intercepto + Σ contribuições
p = sigmoide(logit)
```

Esta decomposição é **exata por definição**: ela não é uma aproximação do modelo, é a aritmética do
modelo reescrita termo a termo. A reconciliação de §6 é, para a LogReg, uma identidade algébrica —
e verificá-la numericamente testa a implementação, não o método.

> **Observação sobre SHAP aplicado à LogReg.** Seria possível usar `LinearExplainer`. Não o faremos
> como método primário: para um modelo linear com features independentes, os valores SHAP coincidem
> com `coef × (valor − média)`, ou seja, com a contribuição linear a menos da centragem. Introduzir
> uma dependência externa para obter o que o próprio modelo já fornece adicionaria um ponto de
> falha sem ganho — o oposto do que a ADR-008 busca.

### 2.4 `permutation_importance` como fallback global

**Quando é usado:** quando `shap` não está disponível — Python 3.13 sem *wheel* compatível,
perfil Docker enxuto, ou falha de importação (ADR-008).

**Como funciona:** embaralha uma feature de cada vez no conjunto de validação e mede a queda da
métrica. A queda é a importância.

```python
permutation_importance(
    pipeline, X_val, y_val,
    scoring='average_precision',
    n_repeats=10,
    random_state=42,
    n_jobs=-1,
)
```

**Por que `average_precision` como métrica de referência:** é a mesma métrica usada para selecionar
hiperparâmetros (`ESTRATEGIA_TREINO_TESTE.md` §5.3). Usar a acurácia aqui produziria importâncias
que refletem o desempenho na classe majoritária.

**Por que na validação e não no treino:** a importância medida no treino reflete o que o modelo
memorizou; na validação, reflete o que generaliza.

### 2.5 A lacuna do fallback — e como é preenchida

`permutation_importance` é **global**. Ela responde "quais features o modelo usa em geral", não
"por que **esta** gestante foi classificada assim". Se o fallback fosse apenas ela, a explicação
local desapareceria exatamente quando mais se precisa dela.

A ADR-008 resolve isso: **o fallback local é a contribuição linear da Regressão Logística.**

| Cenário | Explicação global | Explicação local |
|---|---|---|
| `shap` disponível + modelo RF | SHAP (média dos \|valores\|) | **SHAP** |
| `shap` **indisponível** + modelo RF | `permutation_importance` | **Contribuição linear da LogReg** |
| Modelo LogReg (qualquer cenário) | Coeficientes / razões de chance | **Contribuição linear** |
| Modelo baseline por regra | Frequência de disparo por critério | **Critérios disparados** |

A linha 2 é a que exige atenção e é a mais fácil de comunicar errado: quando o RF está em uso e o
SHAP não está disponível, a explicação local vem de **outro modelo** — a LogReg treinada no mesmo
dataset. É uma aproximação legítima (ambos aprenderam do mesmo processo gerador) e é **explicitamente
declarada** no payload como `metodo='logreg_proxy'`, com aviso textual ao usuário.

> **Apresentar a contribuição da LogReg como se fosse a explicação do Random Forest, sem declarar,
> seria mentir sobre a origem do número.** É precisamente o que a §5 deste documento impede.

---

## 3. Explicabilidade global

### 3.1 O que é produzido

| Artefato | Conteúdo | Origem |
|---|---|---|
| `artifacts/explainability/<modelo>_importancia_global.json` | Ranking das 24 features com valor de importância | SHAP médio \|·\| ou `permutation_importance` |
| `artifacts/explainability/<modelo>_shap_summary.png` | *Beeswarm* SHAP (RF) | `shap.summary_plot` |
| `artifacts/explainability/<modelo>_shap_bar.png` | Barras de importância média | `shap.summary_plot(plot_type='bar')` |
| `artifacts/explainability/logreg_coeficientes.json` | Coeficientes padronizados, em unidade original, e razões de chance | `modelo.coef_` |
| `artifacts/explainability/<modelo>_dependencia_<feature>.png` | Gráficos de dependência para as 5 principais | `shap.dependence_plot` |

**Estado (2026-09-18):** `artifacts/explainability/importancia_global.json` gerado por `permutation_importance` no Random Forest, amostra de validação (200 linhas, 2 repeats, `scoring=average_precision`). SHAP beeswarm **não** gerado (`shap` ausente). Contribuição negativa na permutação significa que embaralhar a feature **aumentou** AP nesta amostra — ruído, não efeito causal.

### 3.2 Tabela de importância global — Random Forest (permutação)

Cópia dos `top_features` de `importancia_global.json` (arredondamento só na coluna Importância; o JSON permanece a fonte).

| Posição | Feature | Importância | Direção (API) | β do gerador (especificação) | Sinal concorda? |
|---|---|---|---|---|---|
| 1 | pad_mmhg | 0,0436 | aumenta | `(pad−75)/10` +0,32 | sim (magnitude da permutação, não do β) |
| 2 | pas_mmhg | 0,0430 | aumenta | `(pas−120)/10` +0,38 | sim |
| 3 | has_cronica | 0,0429 | aumenta | +1,60 | sim |
| 4 | imc_pre_gestacional | 0,0415 | aumenta | `(imc−24)/5` +0,34 | sim |
| 5 | glicemia_jejum_mg_dl | −0,0359 | reduz | `glicemia≥92` +0,55 | **não nesta amostra** (importância média negativa) |
| 6 | diabetes_previo | −0,0293 | reduz | +1,45 | **não nesta amostra** |
| 7 | cardiopatia | 0,0137 | aumenta | +1,90 | sim |
| 8 | pre_eclampsia_previa | 0,0104 | aumenta | +1,70 | sim |

A coluna "β do gerador" permite a verificação de sanidade descrita em §6.3. Ela é preenchida a
partir de `ESTRATEGIA_DE_ROTULAGEM.md` §2, que é especificação e não resultado; a comparação com a
importância medida é análise **pós-treino** e legítima (`RISCOS_DE_VAZAMENTO.md` **VAZ-07**).

### 3.3 O que NÃO será usado como importância global

**`RandomForestClassifier.feature_importances_`** (importância por impureza) **não** será a medida
principal. Ela é enviesada para variáveis contínuas e de alta cardinalidade: `idade` (38 valores
possíveis) e `pas_mmhg` (121) oferecem muito mais pontos de corte que `cardiopatia` (2), e acumulam
redução de impureza por isso, não por serem mais informativas.

Com 10 binárias entre as 24 features, o viés seria sistemático e direcional: as comorbidades — que
têm os maiores β do gerador — apareceriam subestimadas. Ela pode ser reportada como diagnóstico
complementar, sempre rotulada como *importância por impureza (enviesada)*.

---

## 4. Explicabilidade local

### 4.1 O que acompanha cada predição

Por `ARQUITETURA_ALVO.md` §5.2, o payload carrega:

```json
{
  "top_features": [
    { "feature": "...", "value": null, "contribution": null, "direction": "aumenta|reduz" }
  ],
  "metodo_explicacao": "shap_tree|coef_linear|logreg_proxy|permutacao|regra",
  "valor_base": null,
  "soma_contribuicoes": null,
  "reconciliacao_ok": null,
  "dados_imputados": []
}
```

### 4.2 Quantas features exibir

**Decisão: as 5 de maior contribuição absoluta**, com o restante agregado em "demais variáveis".

Exibir as 24 tornaria a explicação ilegível na consulta; exibir 3 omitiria contribuições
relevantes. O agregado "demais" é obrigatório e não decorativo: sem ele, a soma exibida não fecharia
com a saída do modelo, e o usuário não teria como perceber que está vendo uma explicação truncada.

### 4.3 Direção, não apenas magnitude

Cada contribuição carrega `direction`: `aumenta` se positiva, `reduz` se negativa.

Isso importa clinicamente. Uma explicação que lista apenas "as variáveis mais importantes" não
distingue um fator que **elevou** o risco de um que o **reduziu** — e `escolaridade_anos` tem β
negativo no gerador, então contribuições negativas são esperadas e precisam ser legíveis.

### 4.4 Features imputadas são marcadas

Se uma feature entre as 5 principais teve o valor **imputado**, isso é sinalizado na própria linha
da explicação. Uma contribuição calculada sobre uma mediana populacional não tem o mesmo estatuto
de uma calculada sobre um valor medido na paciente, e apresentá-las com a mesma aparência seria
apagar uma distinção que muda a leitura.

Detalhamento da comunicação em `INTERPRETACAO_DAS_PREDICOES.md` §5.

---

## 5. Registro do método efetivamente usado

Exigência direta da ADR-008: *"registra no payload qual método foi usado, para que a explicação
nunca seja apresentada como SHAP quando não for"*.

### 5.1 Detecção em tempo de importação

```python
# lib/ml/explain.py
try:
    import shap
    SHAP_DISPONIVEL = True
    SHAP_VERSAO = shap.__version__
except ImportError:
    SHAP_DISPONIVEL = False
    SHAP_VERSAO = None
```

A detecção é por importação real, não por leitura de `requirements.txt` — só a importação prova
disponibilidade no ambiente de execução.

### 5.2 Valores possíveis de `metodo_explicacao`

| Valor | Significado | Escopo | Exato? |
|---|---|---|---|
| `shap_tree` | `TreeExplainer` sobre modelo de árvore | Local + global | Sim |
| `coef_linear` | `coef × valor_padronizado` da LogReg | Local + global | Sim |
| `logreg_proxy` | **Contribuição da LogReg usada para explicar o RF** (fallback) | Local | **Aproximado — é outro modelo** |
| `permutacao` | `permutation_importance` | **Global apenas** | Aproximado |
| `regra` | Critérios disparados pelo baseline | Local | Sim |
| `indisponivel` | Nenhum método pôde ser aplicado | — | — |

### 5.3 Onde o método é registrado

| Destino | Campo |
|---|---|
| Payload para o LLM | `metodo_explicacao` |
| Interface Gradio | Texto visível: *"Método de explicação: ..."* |
| Auditoria (`predicoes_ml`) | Dentro de `top_features` (JSON) |
| Log estruturado | Campo do evento de predição |

### 5.4 Regras de linguagem vinculadas ao método

| Método | Frase permitida | Frase **proibida** |
|---|---|---|
| `shap_tree` | "Contribuições calculadas por SHAP (TreeExplainer)" | — |
| `coef_linear` | "Contribuições calculadas a partir dos coeficientes do modelo" | **"calculadas por SHAP"** |
| `logreg_proxy` | "SHAP indisponível. Contribuições estimadas por um modelo linear auxiliar treinado no mesmo conjunto — **são uma aproximação** e podem divergir do modelo em uso" | **"por SHAP"**, **"do Random Forest"** |
| `permutacao` | "Importância global por permutação. **Não há explicação específica para este caso**" | Qualquer frase que sugira explicação local |
| `indisponivel` | "Explicação indisponível para esta predição" | Qualquer explicação |

A linha `logreg_proxy` é a de maior risco de comunicação enganosa e, por isso, é a que carrega a
ressalva mais longa. A linha `permutacao` é a segunda: apresentar uma importância global como se
explicasse um caso individual é um erro sutil e comum.

### 5.5 Teste que garante o registro

**`tests/unit/test_metodo_explicacao_declarado.py`:**

| Assertiva | Conteúdo |
|---|---|
| Campo obrigatório | `metodo_explicacao` presente em todo payload, nunca `None` nem ausente |
| Domínio fechado | Valor ∈ {`shap_tree`, `coef_linear`, `logreg_proxy`, `permutacao`, `regra`, `indisponivel`} |
| Coerência com o ambiente | Com `shap` simulado como indisponível (`monkeypatch` de `SHAP_DISPONIVEL`), o método **nunca** é `shap_tree` |
| Coerência textual | Se o método não é `shap_tree`, a palavra "SHAP" **não aparece** no texto de explicação, exceto na frase de indisponibilidade |
| Ausência de explicação local em `permutacao` | `top_features` vazio ou marcado como global |

---

## 6. Validação de que a explicação corresponde à predição real

Esta é a seção que separa explicabilidade de decoração. Uma explicação que não reconcilia com a
saída do modelo é um gráfico bonito ao lado de um número — e nada garante que tenham relação.

### 6.1 A propriedade verificada

Pela aditividade local do SHAP (e por identidade algébrica no caso linear):

```
valor_base + Σ(contribuições de todas as 24 features) ≈ saída do modelo
```

| Modelo | Espaço em que a identidade vale | `valor_base` |
|---|---|---|
| `LogisticRegression` | **Logit** (log-odds) | Intercepto |
| `RandomForestClassifier` | **Probabilidade** (saída do `TreeExplainer`) | `explainer.expected_value` |

**Cuidado técnico obrigatório:** a verificação precisa ser feita **no espaço correto de cada
modelo**. Para a LogReg, a soma reconcilia com o **logit**, não com a probabilidade — a sigmoide é
não-linear e a soma das contribuições não é igual a `p`. Aplicar a sigmoide antes de comparar
produziria falha em uma reconciliação que está correta, e é um erro fácil de cometer.

### 6.2 O teste

**`tests/unit/test_explicabilidade_reconcilia.py`** — nomeado como exigido.

| Item | Definição |
|---|---|
| **Entrada** | Amostra fixa de ≥ 50 registros do conjunto de **validação**, semente 42 |
| **Procedimento** | Para cada registro: calcular a explicação completa (24 features, sem truncar em 5), somar as contribuições, adicionar `valor_base`, comparar com a saída real do modelo |
| **Tolerância — LogReg** | \|soma + intercepto − logit\| < **1e-9** (identidade algébrica; só erro de ponto flutuante) |
| **Tolerância — RF com `shap_tree`** | \|soma + valor_base − p̂\| < **1e-6** (`TreeExplainer` é exato; a folga é numérica) |
| **Falha** | Qualquer registro fora da tolerância **reprova o teste** |
| **Cobertura de fallback** | O teste roda também com `SHAP_DISPONIVEL = False`, verificando que `logreg_proxy` reconcilia **com a LogReg** (e registrando que **não** reconcilia com o RF — que é o motivo de ser declarado como aproximação) |

**Por que tolerâncias tão estreitas.** Ambos os métodos são **exatos**, não aproximados. Uma
tolerância frouxa (1e-2, por exemplo) esconderia bugs reais — ordem de features trocada,
escalonamento aplicado duas vezes, `expected_value` da classe errada em problema binário. Se a
reconciliação exigir folga, há erro de implementação, não imprecisão do método.

### 6.3 Verificação de sanidade clínica (complementar)

Distinta da reconciliação: a reconciliação testa a **implementação**; esta testa a
**plausibilidade**.

**`tests/unit/test_explicacao_sanidade.py`:**

| Assertiva | Racional |
|---|---|
| Em caso com `pre_eclampsia_previa = 1`, esta feature está entre as 5 principais, com direção `aumenta` | β = +1,70, o maior entre os antecedentes. Se não aparecer, a suspeita recai sobre o explicador ou o treino |
| Em caso com `cardiopatia = 1`, idem | β = +1,90, o maior coeficiente absoluto |
| Nenhuma contribuição é `NaN` ou infinita | Higiene numérica |
| `direction` coerente com o sinal da contribuição | Consistência interna |
| Features com valor **imputado** estão marcadas | Requisito de §4.4 |
| A soma das 5 exibidas + "demais" == soma total | A explicação truncada não perde massa |

> **Esta verificação usa os β do gerador para validar o explicador, não para treinar o modelo.**
> É uso pós-treino e legítimo (`RISCOS_DE_VAZAMENTO.md` **VAZ-07**). A fronteira é temporal: os β
> podem informar a **interpretação** e a **verificação**, nunca o **ajuste**.

### 6.4 Verificação em tempo de execução

Além dos testes, `lib/ml/explain.py` verifica a reconciliação **a cada predição em produção** e
grava o resultado no payload:

| Campo | Conteúdo |
|---|---|
| `soma_contribuicoes` | Valor calculado |
| `valor_base` | Valor base do explicador |
| `reconciliacao_ok` | `true` / `false` |
| `reconciliacao_delta` | Diferença absoluta observada |

**Se `reconciliacao_ok == false`:** a explicação **não é exibida**. Em seu lugar, aparece a
mensagem *"Explicação indisponível para esta predição (falha de verificação interna)"*, e o evento
é registrado na auditoria. A predição e a probabilidade continuam sendo apresentadas — o que falhou
foi a explicação, não o modelo.

Esta é a aplicação do princípio de falha explícita de `ARQUITETURA_ALVO.md` §8: *falha é explícita;
modo degradado é declarado ao usuário, nunca silencioso.* Exibir uma explicação que não reconcilia
seria pior que não exibir nenhuma, porque pareceria correta.

---

## 7. Limitações da explicabilidade

### 7.1 SHAP assume independência entre features

**O problema.** A formulação de valor esperado condicional do SHAP exige decidir como avaliar o
modelo quando um subconjunto de features está "ausente". `tree_path_dependent` usa a estrutura das
árvores, o que equivale a uma suposição sobre a distribuição das features ausentes. Quando as
features são correlacionadas, a atribuição de crédito entre elas torna-se ambígua: parte do crédito
de uma pode migrar para a outra, dependendo da formulação.

**Por que é agudo neste dataset.** As dependências foram impostas deliberadamente
(`DICIONARIO_DE_DADOS.md` §6.2):

| Dependência | Consequência para a explicação |
|---|---|
| `idade`, `imc` → `has_cronica` | O crédito por risco associado à idade pode aparecer em `has_cronica` e vice-versa |
| `has_cronica` → `pas_mmhg` (+18 mmHg) | **A mais problemática.** PAS é parcialmente consequência de HAS crônica. A explicação pode atribuir a PAS elevada um crédito que "pertence" à HAS, e a leitura clínica ficaria invertida |
| `imc` → `diabetes_previo` | Idem entre obesidade e disglicemia |
| `diabetes_previo` → `glicemia_jejum` (+25 mg/dL) | Idem |

**Consequência prática:** quando duas features correlacionadas aparecem entre as principais, suas
contribuições individuais **não** devem ser lidas como efeitos separáveis. A divisão do crédito
entre elas é, em parte, artefato do método.

**Ironia a registrar:** como as correlações aqui são **mais esparsas** que em dado real (§2.4 de
`LIMITACOES_DO_MODELO.md`), as explicações deste sistema são **mais limpas do que seriam** com
dados reais. A limitação é subestimada por este experimento.

### 7.2 Importância não é causalidade

**A limitação mais importante do documento**, e a que tem maior potencial de dano clínico.

SHAP, coeficientes e importância por permutação medem **associação dentro do modelo** — quanto a
saída muda quando a feature muda, dado o que o modelo aprendeu. Nenhum deles estabelece relação
causal.

Três formas em que isso se manifesta concretamente:

| Situação | Leitura errada | Leitura correta |
|---|---|---|
| `escolaridade_anos` com contribuição negativa | "Mais escolaridade **reduz** o risco gestacional" | É um **proxy socioeconômico** de acesso a serviços e informação. Nada no modelo indica que educar reduziria risco |
| `pas_mmhg` elevada com grande contribuição | "A pressão alta **causou** o risco" | A PAS é, neste gerador, parcialmente **consequência** de `has_cronica`. A direção causal não é recuperável do modelo |
| `proteinuria ≥ 1+` com grande contribuição | "A proteinúria **causou** o alto risco" | Proteinúria é **manifestação** de um processo, não sua causa |

Consequência direta: a política de linguagem de `INTERPRETACAO_DAS_PREDICOES.md` §2 **proíbe**
formulações causais. Frases como *"Esta variável causou o risco"* são vedadas; a forma obrigatória é
*"As variáveis que mais contribuíram para esta classificação foram..."*.

### 7.3 Instabilidade em florestas pequenas

Com `n_estimators=200` (o menor valor do grid) e `min_samples_leaf=1`, as folhas são pequenas e a
estrutura das árvores é sensível à amostragem. Dois registros quase idênticos podem receber
atribuições visivelmente diferentes, e a mesma explicação recalculada após retreino com semente
diferente pode reordenar as features.

**Mitigações:**

| Mitigação | Efeito |
|---|---|
| `random_state=42` fixo | Explicações **reprodutíveis** para um mesmo modelo — mas não estáveis entre modelos |
| `min_samples_leaf ∈ {1, 5, 20}` no grid | Valores maiores produzem explicações mais estáveis; o grid permite que a CV escolha |
| `feature_perturbation='tree_path_dependent'` | Elimina a variabilidade do *background set* |
| Exibir 5 features, não 24 | A ordenação entre as principais é mais estável que a cauda |

**Não mitigado:** a instabilidade intrínseca da estrutura. Ela é declarada, não resolvida.

### 7.4 A explicação explica o modelo, não a paciente

A explicação mostra o que **o modelo** usou. Se o modelo estiver errado, a explicação descreverá com
clareza um raciocínio errado.

Isto é contraintuitivo e precisa ser dito: **uma boa explicação de uma predição ruim é pior que
nenhuma explicação**, porque adiciona credibilidade ao erro. A explicação não valida a predição — e
a clareza da apresentação não é evidência de correção.

### 7.5 Explicação global não explica caso individual

`permutation_importance` responde "quais features o modelo usa em geral". Ela **não** responde "por
que esta gestante foi classificada assim". Quando o fallback global estiver em uso sem o
`logreg_proxy`, a interface deve dizer explicitamente que **não há explicação para este caso**, em
vez de exibir o ranking global ao lado da predição individual — justaposição que o usuário leria
naturalmente como explicação local.

### 7.6 Limitações herdadas dos dados

Toda limitação de `LIMITACOES_DO_MODELO.md` §2 propaga para a explicação. Em particular: as
contribuições refletem os **β que nós escolhemos**. Quando `pre_eclampsia_previa` aparecer no topo
de uma explicação, isso reflete `β = +1,70` — um número que escrevemos —, não um achado sobre
gestação.

---

## 8. Política de linguagem

Resumo; o tratamento completo, com tabela de proibido/permitido e exemplos, está em
`INTERPRETACAO_DAS_PREDICOES.md` §2.

### 8.1 Princípios

| # | Princípio |
|---|---|
| 1 | **Nunca causal.** "Contribuiu para", nunca "causou", "provocou" ou "levou a" |
| 2 | **Sempre atribuída ao modelo.** "O modelo considerou", não "a paciente tem risco porque" |
| 3 | **Sempre com o método declarado.** O nome da técnica acompanha a explicação |
| 4 | **Sempre com o aviso de dados sintéticos.** Campo obrigatório do payload |
| 5 | **Imputação sempre declarada.** Contribuição sobre valor imputado é marcada |
| 6 | **Nunca prescritiva.** A explicação não sugere conduta |
| 7 | **Incerteza visível.** Probabilidade com limiar, nunca rótulo isolado |

### 8.2 Fórmula obrigatória

> **"As variáveis que mais contribuíram para esta classificação foram: ..."**

### 8.3 Aplicação ao LLM

O LLM recebe as contribuições no payload sob contrato somente-leitura (ADR-007) e **não pode
alterá-las**. A verificação pós-geração extrai os numerais do texto e confere contra o payload; em
divergência, o texto é descartado e a resposta estruturada é entregue.

`tests/unit/test_linguagem_nao_causal.py` verifica a ausência de verbos causais na saída renderizada
e nos templates.

---

## 9. Estrutura de código planejada

```python
# lib/ml/explain.py — NÃO IMPLEMENTADO

SHAP_DISPONIVEL: bool
SHAP_VERSAO: str | None

class ResultadoExplicacao(TypedDict):
    top_features: list[dict]        # 5 principais + agregado "demais"
    todas_contribuicoes: list[dict] # 24, para a reconciliação
    metodo_explicacao: str          # domínio fechado de §5.2
    valor_base: float
    soma_contribuicoes: float
    reconciliacao_ok: bool
    reconciliacao_delta: float
    escopo: str                     # 'local' | 'global'
    aviso: str | None               # ressalva do método (§5.4)


def explicar_local(pipeline, X_linha, dados_imputados) -> ResultadoExplicacao:
    """Explicação local com seleção automática de método e verificação
    de reconciliação. NUNCA devolve explicação sem reconciliar."""


def explicar_global(pipeline, X_val, y_val) -> ResultadoExplicacao:
    """Importância global: SHAP médio, coeficientes ou permutação."""


def _reconciliar(contribuicoes, valor_base, saida_modelo, espaco) -> tuple[bool, float]:
    """Verifica aditividade no espaço correto ('logit' ou 'probabilidade')."""
```

---

## 10. Testes associados

| Teste | Verifica | Existe? |
|---|---|---|
| `tests/unit/test_explicabilidade_reconcilia.py` | **Aditividade local** — soma + base ≈ saída, no espaço correto, para ≥ 50 registros | **Não** |
| `tests/unit/test_metodo_explicacao_declarado.py` | `metodo_explicacao` presente, no domínio, coerente com o ambiente e com o texto | **Não** |
| `tests/unit/test_explicacao_sanidade.py` | Fatores de β alto aparecem entre os principais; sem `NaN`; direção coerente | **Não** |
| `tests/unit/test_linguagem_nao_causal.py` | Ausência de verbos causais na saída e nos templates | **Não** |
| `tests/unit/test_explicacao_fallback.py` | Com `shap` indisponível, o fallback ativa, declara-se e reconcilia com a LogReg | **Não** |
| `tests/integration/test_payload_explicabilidade.py` | Payload completo com todos os campos de §4.1 | **Não** |

---

## 11. Estado atual

| Item | Estado |
|---|---|
| `lib/ml/explain.py` | **Não implementado** |
| `shap` instalado e verificado | **Não verificado** |
| Modelos treinados | **0 de 4** |
| Valores SHAP calculados | **Nenhum** |
| Importância global calculada | **Nenhuma** |
| Explicações locais geradas | **Nenhuma** |
| Reconciliação executada | **Nunca** |
| `artifacts/explainability/` | **Não existe** |
| Testes escritos | **0 de 6** |

> **Confirmação explícita:** este documento **não contém nenhuma importância de variável, nenhum
> valor SHAP e nenhum ranking medido**. Os coeficientes β citados (+1,70 para
> `pre_eclampsia_previa`, +1,90 para `cardiopatia`) são **especificação do gerador**, publicada em
> `ESTRATEGIA_DE_ROTULAGEM.md` §2, e aparecem aqui apenas como base das verificações de sanidade.
> **Nenhum número deste documento é um resultado de execução.**
