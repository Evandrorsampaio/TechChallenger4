> **Status (2026-09-18):** comparação preenchida a partir de `artifacts/metrics/comparacao.json`.

**Vencedor por PR-AUC no teste:** `logistic_regression` (0,590) vs RF (0,557) vs regra (0,263) vs dummy (0,206).

O ML **supera** a regra em PR-AUC. O ganho LogReg−RF em PR-AUC (≈0,03) está dentro da sobreposição aproximada dos IC (LogReg [0,527; 0,652], RF [0,494; 0,619]) — a escolha da logística é pelo ponto, não por exclusão estatística forte.

# Comparação de Modelos


**Agente responsável:** `MachineLearningAgent`
**Status:** **MODELO DE COMPARAÇÃO VAZIO** — nenhum modelo treinado, nenhuma comparação realizada
**Base normativa:** `DEFINICAO_DO_PROBLEMA.md` §5, `MODELOS_AVALIADOS.md`, `ESTRATEGIA_TREINO_TESTE.md` §7

---

> # ⛔ NENHUM MODELO FOI TREINADO. NENHUMA COMPARAÇÃO FOI FEITA.
>
> Este documento é uma **estrutura de comparação vazia**. Todas as células de resultado contêm `—`.
>
> Toda célula será preenchida **exclusivamente** a partir de
> `artifacts/metrics/comparacao.json` e `artifacts/metrics/<modelo>_bootstrap.json`, produzidos por
> `python scripts/evaluate.py`.
>
> **Estado atual:** `artifacts/` não existe. `scripts/evaluate.py` não existe. Nenhum dos quatro
> modelos foi ajustado. O conjunto de teste **nunca foi aberto**.
>
> A **§4 deste documento — o critério de decisão — é a única seção substantiva agora, e é
> deliberado.** Ela existe para ser escrita *antes* de qualquer resultado. Um critério de escolha
> redigido depois de ver as métricas não é critério: é justificativa.

---

## 1. O que esta comparação precisa responder

Três perguntas, em ordem de importância, e só a terceira é sobre métrica.

| # | Pergunta | Por que importa |
|---|---|---|
| 1 | **O ML supera a regra determinística que o sistema já usa?** | Se não superar, não há justificativa para acrescentar um modelo a um sistema que funciona. É a pergunta que a ADR-002 faz |
| 2 | **O ganho é maior que a incerteza da medida?** | Uma diferença dentro do intervalo de confiança não é uma diferença. Sem isso, a comparação é ruído apresentado como conclusão |
| 3 | Entre os modelos de ML, qual é melhor? | Só faz sentido depois das duas primeiras |

A pergunta 1 é o motivo de o baseline determinístico (`CRITERIOS_ALTO_RISCO`) estar no catálogo. É
possível que a resposta seja **não** — e esse desfecho está previsto em §4.4.

---

## 2. Tabela comparativa — métricas primárias

Conjunto de **teste**, cada modelo em seu limiar operacional (modelos #0 e #1 em seu ponto fixo).

### 2.1 Métricas de decisão

| Modelo | Limiar | **Recall** | **Precisão** | F1 | Especificidade | VPN | PR-AUC | Brier |
|---|---|---|---|---|---|---|---|---|
| #0 `DummyClassifier` | n/a | — | indefinida | — | — | — | — | — |
| #1 Baseline por regra | n/a | — | — | — | — | — | — ⚠ | — |
| #2 `LogisticRegression` | — | — | — | — | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — | — | — | — | — |

⚠ A PR-AUC do modelo #1 não é comparável às demais — ele produz apenas dois valores de
probabilidade e sua curva tem um único ponto (`MODELOS_AVALIADOS.md` §3).

### 2.2 Erros absolutos no teste

A tabela que traduz a métrica em consequência. Cada unidade na coluna **FN** é uma gestante de alto
risco que não seria encaminhada.

| Modelo | VP | **FN** | FP | VN | Encaminhamentos gerados | Alto risco não detectado |
|---|---|---|---|---|---|---|
| #0 `DummyClassifier` | — | — | — | — | — | — |
| #1 Baseline por regra | — | — | — | — | — | — |
| #2 `LogisticRegression` | — | — | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — | — | — |

### 2.3 A comparação que responde à pergunta 1

Com o **recall fixado em ≥ 0,90 para todos os modelos ajustáveis**, a diferença de desempenho
aparece inteiramente na **precisão** — isto é, em quantos encaminhamentos desnecessários cada
modelo gera para capturar a mesma proporção de casos de alto risco.

| Comparação | Δ Recall | Δ Precisão | Δ FP (absoluto) | Δ FN (absoluto) |
|---|---|---|---|---|
| #2 LogReg **vs.** #1 Baseline | — | — | — | — |
| #3 RF **vs.** #1 Baseline | — | — | — | — |
| #3 RF **vs.** #2 LogReg | — | — | — | — |
| Modelo escolhido **vs.** #1 Baseline | — | — | — | — |

> **Hipótese pré-registrada** (`ESTRATEGIA_DE_ROTULAGEM.md` §3): *os modelos de ML conseguem manter
> o recall do baseline determinístico enquanto melhoram substancialmente a precisão.*
>
> **Esta hipótese pode falhar, e se falhar será reportada como falha.** O resultado real será
> confrontado com ela em §7.

_PENDENTE — `artifacts/metrics/comparacao.json`_

---

## 3. Comparação com intervalo de confiança e teste estatístico

Comparar dois pontos sem incerteza não é comparação. Dois procedimentos, com finalidades distintas.

### 3.1 Bootstrap pareado — para diferenças de métricas contínuas

| Item | Definição |
|---|---|
| Procedimento | 1 000 reamostragens com reposição do conjunto de teste, estratificadas pelo alvo |
| **Pareamento** | As **mesmas reamostras** para todos os modelos. Em cada reamostra *b*, calcula-se a diferença `métrica(A) − métrica(B)` |
| Estatística | Distribuição empírica das 1 000 diferenças |
| Intervalo | Percentis 2,5 e 97,5 |
| Critério | Se o **IC 95 % da diferença não contiver zero**, a diferença é considerada estatisticamente consistente |
| Semente | 42 |

**Por que pareado.** Os modelos são avaliados sobre **os mesmos registros**, então seus erros são
correlacionados — quando um caso é difícil, tende a ser difícil para todos. Reamostrar
independentemente ignoraria essa correlação e produziria um intervalo **inflado** para a diferença,
tornando mais difícil detectar uma diferença real. O bootstrap pareado estima a variabilidade da
**diferença**, que é a quantidade de interesse.

**Diferenças pareadas — recall:**

| Comparação (A vs. B) | Δ pontual | IC 95 % inf. | IC 95 % sup. | IC contém 0? | Conclusão |
|---|---|---|---|---|---|
| #2 LogReg vs. #1 Baseline | — | — | — | — | — |
| #3 RF vs. #1 Baseline | — | — | — | — | — |
| #3 RF vs. #2 LogReg | — | — | — | — | — |

**Diferenças pareadas — precisão:**

| Comparação (A vs. B) | Δ pontual | IC 95 % inf. | IC 95 % sup. | IC contém 0? | Conclusão |
|---|---|---|---|---|---|
| #2 LogReg vs. #1 Baseline | — | — | — | — | — |
| #3 RF vs. #1 Baseline | — | — | — | — | — |
| #3 RF vs. #2 LogReg | — | — | — | — | — |

**Diferenças pareadas — PR-AUC** (apenas entre #2 e #3; o baseline não é comparável em AUC):

| Comparação (A vs. B) | Δ pontual | IC 95 % inf. | IC 95 % sup. | IC contém 0? | Conclusão |
|---|---|---|---|---|---|
| #3 RF vs. #2 LogReg | — | — | — | — | — |

### 3.2 Teste de McNemar — para discordância de classificação

| Item | Definição |
|---|---|
| Aplicação | Dois classificadores, **mesmo conjunto de teste**, rótulos binários no limiar operacional |
| Hipótese nula | Os dois modelos têm a mesma taxa de erro — isto é, `b = c` na tabela de discordância |
| Estatística | McNemar com correção de continuidade; **exato binomial** se `b + c < 25` |
| Nível | α = 0,05 |
| Implementação | `statsmodels.stats.contingency_tables.mcnemar` |

**Por que McNemar e não um teste t entre acurácias.** As duas amostras não são independentes — são
o mesmo conjunto de registros classificado duas vezes. McNemar é o teste correto para dados
pareados binários, e usa exatamente a informação que interessa: **os casos em que os dois modelos
discordam**. Os casos em que ambos acertam ou ambos erram não carregam informação sobre qual é
melhor, e o teste corretamente os ignora.

**Tabelas de discordância:**

**#3 RF vs. #2 LogReg:**

| | LogReg acertou | LogReg errou |
|---|---|---|
| **RF acertou** | — (a) | — (b) |
| **RF errou** | — (c) | — (d) |

| Item | Valor |
|---|---|
| Estatística de McNemar | — |
| Valor-p | — |
| Teste usado (χ² corrigido / exato) | — |
| Conclusão | — |

**Modelo escolhido vs. #1 Baseline determinístico:**

| | Baseline acertou | Baseline errou |
|---|---|---|
| **Escolhido acertou** | — (a) | — (b) |
| **Escolhido errou** | — (c) | — (d) |

| Item | Valor |
|---|---|
| Estatística de McNemar | — |
| Valor-p | — |
| Teste usado | — |
| Conclusão | — |

**McNemar restrito aos falsos negativos** — a comparação clinicamente decisiva:

| | Baseline capturou | Baseline perdeu |
|---|---|---|
| **Escolhido capturou** | — | — |
| **Escolhido perdeu** | — | — |

| Item | Valor |
|---|---|
| Casos de alto risco capturados **só** pelo modelo escolhido | — |
| Casos de alto risco capturados **só** pelo baseline | — |
| Valor-p | — |

A célula "capturados só pelo baseline" merece atenção especial quando preenchida: são casos de alto
risco que o sistema atual detecta e o modelo novo perderia. Mesmo que o modelo seja melhor no
agregado, cada caso dessa célula é uma regressão clínica concreta e deve ser analisado
individualmente em `METRICAS_E_RESULTADOS.md` §9.1.

### 3.3 Correção para múltiplas comparações

Com quatro modelos, há seis comparações par a par possíveis. Testar todas a α = 0,05 infla a
probabilidade de ao menos um falso positivo.

**Decisão pré-registrada:** serão realizados **apenas os três testes de McNemar listados em §3.2**,
declarados antes da execução. Com três testes planejados, aplica-se correção de **Bonferroni**:
α ajustado = 0,05 / 3 ≈ **0,0167**.

Comparações adicionais que venham a ser feitas por curiosidade serão marcadas explicitamente como
**exploratórias**, e seus valores-p **não** sustentarão conclusão.

### 3.4 Limitação declarada dos testes estatísticos aqui

> Estes testes avaliam se as diferenças observadas são maiores que a variabilidade amostral **deste
> conjunto de teste sintético**. Eles **não** avaliam se a diferença se manteria em dados reais, em
> outra população ou em outro serviço.
>
> Um valor-p pequeno aqui significa: "a diferença não é ruído amostral **dentro da distribuição que
> nós mesmos geramos**". Não significa "o modelo A é melhor que o modelo B para gestantes".
>
> A distinção não é preciosismo. Significância estatística sobre dados sintéticos é uma afirmação
> sobre o nosso gerador, não sobre o mundo.

_PENDENTE — `artifacts/metrics/comparacao.json`, chaves `bootstrap_pareado` e `mcnemar`_

---

## 4. Critério de decisão — PRÉ-REGISTRADO

> **Esta seção foi escrita antes de qualquer modelo ser treinado.** Seu propósito é fixar a regra
> de escolha enquanto nenhum resultado é conhecido, de modo que a decisão final seja **aplicação de
> um critério** e não **racionalização de uma preferência**.

### 4.1 A regra

> **O modelo escolhido será aquele com a MAIOR PRECISÃO entre os que atingem RECALL ≥ 0,90 no
> CONJUNTO DE VALIDAÇÃO.**
>
> **Empate dentro do intervalo de confiança resolve-se pelo MODELO MAIS INTERPRETÁVEL.**

### 4.2 Desdobramento operacional

| Passo | Regra |
|---|---|
| 1 | Para cada modelo ajustável (#2, #3), selecionar o **menor limiar** com recall ≥ 0,90 na **validação** (`ESTRATEGIA_TREINO_TESTE.md` §6) |
| 2 | Formar o conjunto de **candidatos elegíveis**: os que atingem recall ≥ 0,90 na validação |
| 3 | Entre os elegíveis, ordenar por **precisão na validação**, decrescente |
| 4 | Se a diferença de precisão entre o 1º e o 2º **não for consistente** — IC 95 % da diferença pareada contendo zero — declarar **empate** |
| 5 | Em caso de empate, escolher o **mais interpretável**, pela ordem de precedência de §4.3 |
| 6 | Registrar a decisão, o critério aplicado e o passo que a determinou |

**A comparação dos passos 3 e 4 é feita sobre a VALIDAÇÃO, não sobre o teste.** Escolher o modelo
olhando o teste seria seleção sobre o teste (`RISCOS_DE_VAZAMENTO.md` **VAZ-04**). O teste só é
aberto depois que o vencedor está congelado.

### 4.3 Ordem de interpretabilidade — declarada a priori

Do mais para o menos interpretável:

| Ordem | Modelo | Justificativa |
|---|---|---|
| 1º | #1 Baseline determinístico | A explicação é a lista literal dos critérios disparados. Totalmente auditável, sem aproximação |
| 2º | #2 `LogisticRegression` | Coeficientes e razões de chance; contribuição local exata `coef × valor_padronizado` |
| 3º | #3 `RandomForestClassifier` | Sem coeficientes; depende de SHAP `TreeExplainer` (exato para árvores, mas indireto) ou de importância por permutação |
| — | #0 `DummyClassifier` | Trivialmente interpretável, mas **inelegível** — não usa `X` |

O Dummy é interpretável e inútil, o que demonstra que interpretabilidade só é critério de desempate
**entre modelos que já satisfizeram a restrição de recall**. Ela nunca substitui desempenho.

### 4.4 Casos de contorno — decididos antes

Cada linha é uma situação que poderia tentar a reinterpretação do critério depois do fato.

| Situação | Decisão pré-registrada |
|---|---|
| **Nenhum modelo atinge recall ≥ 0,90 na validação** | Reportar a falha explicitamente. Apresentar o recall máximo de cada modelo e a precisão correspondente. **Não** relaxar o alvo para 0,85. A decisão de aceitar um recall menor é clínica e operacional, e é registrada como tal — não como um ajuste estatístico |
| **Só o baseline #1 atinge recall ≥ 0,90** | **O baseline vence.** O ML não se justifica. Reportar como o achado principal do experimento: o sistema atual é adequado e a substituição não é recomendada |
| **Baseline e um modelo de ML empatam em precisão** (IC da diferença contém zero) | **O baseline vence** por ser mais interpretável (§4.3, 1º lugar) e por já estar implantado. Acrescentar um modelo de ML sem ganho consistente é acrescentar complexidade, risco de manutenção e uma nova superfície de falha |
| **#2 e #3 empatam** | **`LogisticRegression` vence** — mais interpretável (2º vs. 3º) |
| **Um modelo tem precisão maior mas Brier muito pior** | A regra de §4.1 decide pela precisão. **Porém**, a má calibração é reportada com destaque, e a interface passa a exibir a faixa de probabilidade com ressalva explícita de calibração (`INTERPRETACAO_DAS_PREDICOES.md` §4). Má calibração não desqualifica pelo critério, mas **muda como o resultado é comunicado** |
| **Um modelo tem desempenho muito desigual entre subgrupos** | Não altera a escolha pelo critério de §4.1, mas é registrado como **limitação bloqueante para uso real** em `LIMITACOES_DO_MODELO.md` §3, e aparece no parecer de §8 |
| **O modelo escolhido perde casos de alto risco que o baseline captura** | Cada caso é analisado individualmente (`METRICAS_E_RESULTADOS.md` §9.1). Se houver caso com fator de risco **maior** presente perdido pelo modelo e capturado pelo baseline, isso é reportado como **regressão clínica**, independentemente do agregado |
| **Desempenho no teste muito pior que na validação** | Reportar ambos. **Não** trocar o modelo. Trocar o vencedor depois de ver o teste é seleção sobre o teste (**VAZ-04**) — e a discrepância entre validação e teste é, ela própria, um resultado a comunicar |

A terceira linha é a mais contraintuitiva e a mais importante: **empate com o baseline significa
derrota do ML**. Ela está escrita aqui, antes dos resultados, precisamente porque depois seria
tentador tratar o empate como sucesso ("o modelo é tão bom quanto a regra, e além disso dá
probabilidade").

### 4.5 O que NÃO será usado como critério

| Métrica | Por que não |
|---|---|
| **Acurácia** | Proibida como critério isolado. Com 22 % de positivos, prever sempre "habitual" já entrega ≈ 78 % (`DEFINICAO_DO_PROBLEMA.md` §5.3) |
| **ROC-AUC** | Pouco sensível a aumentos absolutos de falsos positivos com classe desbalanceada. Reportada, não decisiva |
| **F1** | Trata FN e FP como igualmente custosos, o que é falso neste domínio (`DEFINICAO_DO_PROBLEMA.md` §5.1) |
| Desempenho no **teste** | O teste não seleciona. Só reporta |
| Preferência por "modelo mais moderno" | Não é critério técnico |
| Tempo de treino | Irrelevante nesta escala |

---

## 5. Ressalvas de comparabilidade

Três assimetrias que a tabela de §2 não mostra e sem as quais ela é mal lida. Reproduzidas de
`MODELOS_AVALIADOS.md` §6.

| # | Assimetria | A favor de quem | Consequência na leitura |
|---|---|---|---|
| 1 | Modelos #0 e #1 **não têm limiar ajustável** | A favor de #2 e #3 | A comparação é entre um ponto fixo e um ponto **escolhido** para atingir recall ≥ 0,90. Parte da vantagem do ML vem da capacidade de ajustar o limiar, que é uma vantagem real — mas é de natureza diferente de "aprender melhor" |
| 2 | O baseline #1 opera com **13 dos 15 critérios** MS/FEBRASGO (malformação fetal prévia e isoimunização Rh não têm feature correspondente) | A favor de #2 e #3 | O baseline está ligeiramente subestimado |
| 3 | A **LogReg é o modelo corretamente especificado** para a parte linear do gerador | A favor de #2 | O rótulo vem de um modelo latente **logístico**. Os termos lineares da LogReg têm exatamente a forma funcional do gerador — vantagem estrutural que **não existiria em dados reais**, onde a forma funcional verdadeira é desconhecida |

A ressalva 3 muda a interpretação de **qualquer** resultado:

- **Se a LogReg vencer**, parte do mérito é do nosso gerador, não do modelo. O resultado **não**
  sustenta "regressão logística é melhor para risco gestacional".
- **Se o RF vencer** apesar dessa desvantagem estrutural, o achado é **mais forte** do que a
  diferença numérica sugere — significa que as interações e os efeitos de degrau pesam o bastante
  para superar a especificação correta da parte linear.

Ambas as leituras precisam estar escritas **antes** de o resultado ser conhecido, para que a que
sair não seja construída em cima dele.

---

## 6. Trade-off entre interpretabilidade e desempenho

### 6.1 Eixo dos quatro modelos

| Modelo | Interpretabilidade | Método de explicação | Local? | Exato? | Dependência externa |
|---|---|---|---|---|---|
| #0 `DummyClassifier` | Trivial (e vazia) | "Prevê sempre a classe majoritária" | n/a | Sim | Nenhuma |
| #1 Baseline por regra | **Máxima** | Lista literal dos critérios disparados | Sim | Sim | Nenhuma |
| #2 `LogisticRegression` | **Alta** | Coeficientes / razão de chances; `coef × valor_padronizado` | Sim | Sim | Nenhuma |
| #3 `RandomForestClassifier` | **Média** | SHAP `TreeExplainer`; `permutation_importance` | Sim | Sim (para árvores) | **`shap`** (com fallback obrigatório — ADR-008) |

### 6.2 Tabela de decisão preenchida

| Dimensão | #1 Baseline | #2 LogReg | #3 RF | Diferença observada |
|---|---|---|---|---|
| Recall | — | — | — | — |
| Precisão | — | — | — | — |
| PR-AUC | — | — | — | — |
| Brier (calibração) | — | — | — | — |
| Interpretabilidade | Máxima | Alta | Média | — |
| Probabilidade calibrada | **Não produz** | Sim | A verificar | — |
| Limiar ajustável | **Não** | Sim | Sim | — |
| Captura interações | **Não** | **Não** | Sim | — |
| Dependência externa para explicar | Nenhuma | Nenhuma | `shap` (com fallback) | — |
| Custo computacional | Desprezível | Baixo | Moderado | — |

### 6.3 Como o trade-off será resolvido

O critério de §4.1 já embute a resolução, e o embute numa ordem específica: **desempenho primeiro
(restrição de recall), depois precisão, e interpretabilidade apenas como desempate**.

Isso reflete uma posição defensável e que deve ficar explícita: num sistema de **apoio à decisão**
— não de decisão automática — a explicação existe para que o profissional possa **discordar do
modelo com fundamento**. Se o modelo mais interpretável perde casos de alto risco de forma
consistente, sua interpretabilidade não compensa: uma explicação clara de uma predição errada não
ajuda a gestante.

Mas há um limite, e ele é declarado aqui: **nenhum modelo cuja explicação não possa ser validada
contra a predição real será colocado em produção**, qualquer que seja seu desempenho. A validação
de reconciliação (`EXPLICABILIDADE.md` §6 — soma das contribuições locais mais valor base deve
bater com a saída do modelo, dentro de tolerância) é requisito de entrada, não item de comparação.
Um modelo que falhe nela está fora antes da tabela.

### 6.4 O papel específico da calibração neste trade-off

`RandomForestClassifier` tende a produzir probabilidades mal calibradas
(`MODELOS_AVALIADOS.md` §5). Isso interage com o trade-off de um jeito particular neste sistema:

A probabilidade não é consumida apenas pelo profissional — ela é entregue ao LLM sob contrato
somente-leitura (ADR-007) e exibida na interface. Uma probabilidade mal calibrada, comunicada como
"probabilidade de alto risco: 0,75", é **desinformação travestida de número**
(`DEFINICAO_DO_PROBLEMA.md` §5.2).

Portanto, se o RF vencer pelo critério mas apresentar calibração ruim, duas consequências
obrigatórias, ambas pré-registradas:

1. A interface exibe a **faixa** de probabilidade com ressalva explícita de calibração, em vez do
   valor pontual isolado.
2. A recalibração (*isotonic* ou Platt, ajustada na **validação**) entra como item de trabalho
   futuro em `LIMITACOES_DO_MODELO.md` §3 — **não** é aplicada retroativamente nesta comparação,
   porque adicionar uma etapa de calibração depois de ver o resultado alteraria o modelo comparado.

---

## 7. Confronto com a hipótese pré-registrada

`ESTRATEGIA_DE_ROTULAGEM.md` §3 registra a hipótese que este experimento testa:

> *Os modelos de ML conseguem manter o recall do baseline determinístico enquanto melhoram
> substancialmente a precisão.*

| Item | Resultado |
|---|---|
| Recall do baseline #1 | — |
| Recall do modelo escolhido | — |
| O recall foi **mantido**? | — |
| Precisão do baseline #1 | — |
| Precisão do modelo escolhido | — |
| A precisão **melhorou**? | — |
| A melhora é consistente (IC não contém zero)? | — |
| **Hipótese confirmada, refutada ou inconclusiva?** | — |

**Interpretação a registrar conforme o desfecho** (escrita antes, para que não seja construída
depois):

| Desfecho | Leitura |
|---|---|
| **Confirmada** | O pipeline de ML funciona **sobre este gerador**. Não é evidência de utilidade clínica |
| **Refutada** | Achado legítimo e publicável: a regra determinística é competitiva, e o ML não se justifica neste desenho. Reportar sem atenuação |
| **Inconclusiva** (IC contém zero) | Não há base para escolher. Reportar como inconclusivo e recomendar manter o sistema atual |

---

## 8. Justificativa do modelo escolhido

> **_PENDENTE — nenhum modelo foi escolhido porque nenhum modelo foi treinado._**

A ser preenchida **após** a execução, seguindo esta estrutura:

| Campo | Conteúdo |
|---|---|
| **Modelo escolhido** | — |
| Limiar operacional | — |
| Recall na validação | — |
| Precisão na validação | — |
| **Passo do critério §4.2 que determinou a escolha** | — |
| Houve empate? Qual regra de desempate se aplicou? | — |
| Recall no teste | — |
| Precisão no teste | — |
| Diferença validação → teste | — |
| Supera o baseline #1 de forma consistente? | — |
| Valor-p de McNemar vs. baseline | — |
| Calibração aceitável? (Brier, ECE) | — |
| Desempenho desigual em algum subgrupo? | — |
| Perde algum caso de alto risco que o baseline captura? | — |
| Limitações específicas deste modelo | — |
| Ressalvas de comparabilidade (§5) aplicáveis | — |

**Texto da justificativa:** _PENDENTE_

### 8.1 Declaração obrigatória a acompanhar a escolha

Qualquer que seja o modelo escolhido, o parecer deve conter, sem atenuação:

> O modelo foi escolhido com base em desempenho medido sobre um conjunto de teste **100 %
> sintético**, gerado por um processo estatístico que nós mesmos definimos. A escolha indica qual
> modelo recupera melhor **esse processo gerador**.
>
> Ela **não** indica qual modelo teria melhor desempenho em gestantes reais, em qualquer serviço
> de pré-natal. Esse experimento não foi feito e não pode ser feito com os dados disponíveis neste
> projeto.

---

## 9. Procedimento de preenchimento

| Regra | Detalhe |
|---|---|
| Origem única | `artifacts/metrics/comparacao.json` e `artifacts/metrics/<modelo>_bootstrap.json` |
| Sem digitação manual | Preenchimento por script de renderização |
| Ordem obrigatória | §4 (critério) é fixada **antes**; §§2, 3, 6.2, 7, 8 são preenchidas **depois** |
| Imutabilidade do critério | Se §4 precisar ser alterada depois da execução, a alteração é registrada com data, justificativa e a versão anterior preservada. Um critério alterado após os resultados **invalida a pré-registração** e isso é declarado |
| Verificação | `tests/unit/test_documentos_sem_metrica_orfa.py` (**VAZ-12**) |

A linha "imutabilidade do critério" é o que dá valor a este documento. A pré-registração só
significa alguma coisa se a alteração posterior for visível — e, como o arquivo é versionado no
git, qualquer mudança em §4 aparece no diff com autor e data.

---

## 10. Estado atual

| Item | Estado |
|---|---|
| Modelos treinados | **0 de 4** |
| Modelos comparados | **0** |
| Bootstrap pareado executado | **Não** |
| Testes de McNemar executados | **Não** |
| **Modelo escolhido** | **NENHUM** |
| Limiar operacional definido | **Não** |
| Hipótese testada | **Não** |
| Conjunto de teste aberto | **NUNCA** |
| `artifacts/metrics/comparacao.json` | **Não existe** |
| Células de resultado preenchidas | **Zero** |

> **Confirmação explícita:** este documento **não contém nenhum resultado**. Os únicos números que
> nele aparecem são parâmetros de projeto pré-declarados — recall ≥ 0,90, 1 000 reamostragens,
> α = 0,05, Bonferroni 0,0167, semente 42, IC 95 %. **Nenhum é uma medida.**
>
> A seção 4 — o critério de decisão — está completa e é vinculante a partir desta data.
