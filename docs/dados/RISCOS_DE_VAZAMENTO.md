# Registro de Riscos de Vazamento de Dados

**Agente responsável:** `DataEngineeringAgent` (em coordenação com `MachineLearningAgent`)
**Status:** Registro de riscos aberto — **nenhum controle implementado, nenhum teste executado**
**Base normativa:** `CONTRATO_DE_DADOS.md` §3.6, `DEFINICAO_DO_PROBLEMA.md` §6, `ESTRATEGIA_TREINO_TESTE.md` §8
**Implementação alvo:** `lib/ml/dataset.py`, `lib/ml/features.py`, `lib/ml/train.py`, `tests/`

---

> ## ⚠ ESTE É UM REGISTRO DE RISCOS, NÃO UM RELATÓRIO DE CONFORMIDADE
>
> Nenhum controle descrito aqui está implementado. Nenhum teste foi escrito nem executado. A
> coluna "Situação" de todas as tabelas de verificação está vazia.
>
> Este documento existe para que os controles sejam **projetados antes do código**, e para que
> cada risco tenha um teste nomeado que o detecte. Um risco sem teste associado é uma intenção,
> não um controle — e por isso a coluna "Teste que detecta" é obrigatória em todas as linhas.

---

## 1. O que é vazamento, neste projeto

Vazamento (*data leakage*) é qualquer situação em que informação **indisponível no momento real da
predição** influencia o treino, a seleção ou a avaliação do modelo. O efeito é sempre o mesmo:
métricas otimistas que não se reproduzem em uso.

Em um projeto com dados sintéticos e um alvo gerado por nós, o vazamento é **mais fácil de
acontecer e mais difícil de perceber** do que em um projeto com dados reais. A razão é direta:
conhecemos o processo gerador. A probabilidade verdadeira de cada registro está escrita numa coluna
do Parquet, e os coeficientes que a produziram estão escritos num documento versionado. As duas
coisas mais perigosas que se pode vazar estão ao alcance da mão.

Por isso este registro trata explicitamente de duas categorias que não apareceriam num projeto com
dado real: **VAZ-01** (a coluna `risco_latente`) e **VAZ-07** (os coeficientes do gerador usados
como conhecimento do modelador).

---

## 2. Escala de severidade

| Nível | Significado | Consequência se ocorrer |
|---|---|---|
| **Crítico** | Invalida completamente o experimento. As métricas passam a medir o próprio rótulo | Descartar modelo e métricas. Regerar e retreinar |
| **Alto** | Viés de otimismo substancial e não quantificável | Descartar as métricas afetadas. Repetir a etapa |
| **Médio** | Viés de otimismo mensurável ou limitado a parte do relatório | Corrigir e reexecutar; registrar a correção |
| **Baixo** | Efeito pequeno, mas compromete a auditabilidade | Corrigir; registrar |

---

## 3. Registro de riscos

### VAZ-01 — `risco_latente` como feature

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-01 |
| **Tipo** | Vazamento do alvo (*target leakage*) — forma direta |
| **Descrição** | Uma coluna que é função determinística do alvo, ou o próprio alvo transformado, entra na matriz de features |
| **Como ocorreria neste projeto** | `risco_latente` é literalmente `P(alto_risco = 1)` do processo gerador. Ela vive no mesmo Parquet, ao lado das 24 features. Bastaria um `X = df.drop(columns=['alto_risco'])` — o idioma mais comum de pandas para separar `X` de `y` — para incluí-la. O modelo aprenderia a mapear `risco_latente` em `alto_risco`, que é a única relação que ele **não** deveria ter que aprender |
| **Severidade** | **Crítico** |
| **Por que é o mais perigoso** | Não produz erro, não produz aviso, não produz métrica estranha. Produz métricas **excelentes** — e excelência é o sinal que ninguém investiga. Seria reportado como sucesso |
| **Controle preventivo** | Três camadas: **(1) Allow-list.** `lib/ml/dataset.py::carregar_features()` seleciona `X = df[list(FEATURES)]`, onde `FEATURES` é uma tupla fechada. Colunas não declaradas ficam de fora por omissão, não por exclusão. **(2) `drop` proibido.** O idioma `df.drop(columns=[ALVO])` é vedado no código de ML e verificado por busca textual no CI. **(3) Auditoria de correlação.** Antes do treino, toda feature com \|corr\| > 0,95 com o alvo dispara investigação (`DEFINICAO_DO_PROBLEMA.md` §6) |
| **Teste que detecta** | **`tests/unit/test_dataset_sem_vazamento.py`** — assere que `set(X.columns) == set(FEATURES)` e que nenhuma das quatro colunas de rastreabilidade aparece em `X`, para os três splits |

**Nota sobre allow-list vs. deny-list.** A diferença parece estilística e não é. Com deny-list
(`drop`), qualquer coluna nova acrescentada ao gerador entra na matriz de features **por padrão** —
o modo de falha é incluir. Com allow-list, ela fica de fora até ser explicitamente declarada — o
modo de falha é excluir. Num registro de riscos, a pergunta certa não é "qual é mais elegante", é
"o que acontece quando alguém esquecer". Excluir uma feature legítima causa uma queda de métrica
que se investiga; incluir `risco_latente` causa uma alta de métrica que se comemora.

---

### VAZ-02 — Pré-processamento ajustado sobre o dataset completo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-02 |
| **Tipo** | Vazamento por pré-processamento (*preprocessing leakage*) |
| **Descrição** | Transformações que aprendem parâmetros dos dados (`StandardScaler`, `SimpleImputer`, `OrdinalEncoder`) são ajustadas antes da divisão, ou sobre treino + validação + teste |
| **Como ocorreria neste projeto** | O caminho mais provável é ergonômico: é *mais cômodo* escrever `X_todo = scaler.fit_transform(df[FEATURES])` uma vez e depois fatiar por split. A média e o desvio usados para padronizar passariam a conter informação do teste. O mesmo vale para a **mediana** do `SimpleImputer` — e, como 12 % de `hemoglobina_g_dl`, 15 % de `glicemia_jejum_mg_dl` e 20 % de `escolaridade_anos` são imputados, a mediana não é um detalhe: ela é o valor efetivamente entregue ao modelo em quase um quinto dos casos de uma das colunas |
| **Severidade** | **Alto** |
| **Magnitude esperada** | Pequena em valor absoluto com n = 8 000 (a média do treino e a do total praticamente coincidem), mas **não quantificável** e, sobretudo, **não transferível**: em produção só existe a estatística do treino. Um pipeline que dependa da estatística global é um pipeline que não pode ser implantado |
| **Controle preventivo** | **Todo** o pré-processamento vive dentro de um `Pipeline` sklearn cujo `fit` recebe exclusivamente `X_treino`. Nenhum `fit_transform` é chamado fora do `Pipeline`. O objeto serializado em `artifacts/models/` contém o pré-processamento **junto** com o estimador, de modo que treino e inferência não possam divergir (`DEFINICAO_DO_PROBLEMA.md` §6) |
| **Teste que detecta** | **`tests/unit/test_pipeline_fit_apenas_treino.py`** — ajusta o `Pipeline` no treino e verifica que os parâmetros aprendidos (`scaler.mean_`, `imputer.statistics_`) são iguais aos calculados **apenas** sobre o treino, e **diferentes** dos calculados sobre o dataset completo. A assertiva de diferença é a parte essencial: sem ela, o teste passaria mesmo com vazamento |

---

### VAZ-03 — Limiar operacional escolhido no conjunto de teste

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-03 |
| **Tipo** | Vazamento por seleção de hiperparâmetro de decisão |
| **Descrição** | O limiar que converte probabilidade em rótulo é escolhido observando o desempenho no teste |
| **Como ocorreria neste projeto** | O limiar é o parâmetro com maior influência sobre a métrica primária do projeto. Varrer `t` no teste até que o recall passe de 0,90 e depois reportar "recall de 0,90 no teste" é uma afirmação circular: o recall foi **construído** no mesmo conjunto em que é reportado. O risco é agravado pela regra de recall ≥ 0,90 ser um alvo explícito — há um número que se quer atingir, e o teste é onde ele é medido |
| **Severidade** | **Alto** |
| **Controle preventivo** | O limiar é escolhido **exclusivamente** sobre as probabilidades do conjunto de **validação** (`ESTRATEGIA_TREINO_TESTE.md` §6), gravado em `model_card.json` **antes** de qualquer execução sobre o teste, e aplicado ao teste sem alteração. Se nenhum limiar atingir 0,90 na validação, a falha é **reportada**, não contornada baixando o alvo |
| **Teste que detecta** | **`tests/unit/test_limiar_origem_validacao.py`** — recalcula o limiar a partir das probabilidades de validação gravadas em `artifacts/metrics/` e assere que bate com o `threshold` do `model_card.json`. Se o limiar tivesse sido ajustado olhando o teste, deixaria de ser reproduzível pela validação e o teste falharia |

Este é o teste mais valioso do conjunto, porque converte uma promessa de processo ("escolhemos o
limiar na validação") em uma propriedade verificável por execução.

---

### VAZ-04 — Múltiplas consultas ao conjunto de teste

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-04 |
| **Tipo** | Vazamento por seleção adaptativa (*adaptive overfitting* / repeated peeking) |
| **Descrição** | O teste é consultado várias vezes e as decisões subsequentes são influenciadas pelo que foi visto — mesmo sem nenhum ajuste explícito |
| **Como ocorreria neste projeto** | É o vazamento mais **insidioso** porque não exige má-fé nem nenhum ato identificável. São quatro modelos; avaliar os quatro no teste e reportar o melhor já é seleção sobre o teste. Pior: mesmo olhando uma vez, a decisão seguinte ("vou tentar `max_depth` maior") é tomada por um humano que viu o resultado. O viés é introduzido pelo **analista**, e nenhum controle de código o elimina inteiramente |
| **Severidade** | **Alto** |
| **Controle preventivo** | **(1)** Seleção de modelo e de limiar ocorre integralmente na **validação** (`ESTRATEGIA_TREINO_TESTE.md` §7). **(2)** Apenas `scripts/evaluate.py` carrega `split='teste'` — nenhum outro módulo. **(3)** Cada execução que toca o teste acrescenta uma entrada a `artifacts/metrics/registro_avaliacoes.jsonl`, com `motivo` obrigatório e `split_sha256`. **(4)** Se houver mais de uma entrada, **todas** aparecem no relatório final, com os motivos |
| **Teste que detecta** | **`tests/integration/test_avaliacao_uma_vez.py`** — (a) busca textual: nenhum módulo fora de `scripts/evaluate.py` referencia `split='teste'`; (b) espião sobre `carregar_features` durante `tests/integration/test_treino_completo.py`, assertando que o treino completo roda **sem nenhuma** chamada com `split='teste'` |

**Honestidade sobre o limite deste controle:** o registro de avaliações não impede a segunda
consulta ao teste. Ele a torna **visível** — o arquivo é versionado, então uma segunda entrada
aparece como diff no git, com autor e data. É um controle de auditoria, não de prevenção. A
prevenção real depende da disciplina de quem executa, e fingir o contrário seria criar uma falsa
sensação de segurança.

---

### VAZ-05 — Codificação de features dependente do alvo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-05 |
| **Tipo** | Vazamento por codificação (*target encoding leakage*) |
| **Descrição** | Uma feature é transformada usando estatísticas da variável alvo — média do alvo por categoria, WOE, contagem por classe |
| **Como ocorreria neste projeto** | `proteinuria_fita` é a única feature categórica, e *target encoding* é uma técnica popular para categóricas. Substituí-la pela média de `alto_risco` em cada categoria injetaria o alvo diretamente na feature. Com apenas 5 níveis e sem validação cruzada interna, a média de cada categoria seria calculada sobre observações que incluem as próprias linhas codificadas — vazamento dentro da própria linha. Uma variante mais sutil: **binning de uma numérica com cortes escolhidos por maximizar separação do alvo** (ex.: discretizar `pas_mmhg` no ponto que melhor separa as classes) tem o mesmo problema, sem parecer target encoding |
| **Severidade** | **Médio** — limitado a uma feature, mas contamina o pipeline inteiro pelo `Pipeline` compartilhado |
| **Controle preventivo** | **Target encoding é proibido na v1.0.0.** `proteinuria_fita` usa `OrdinalEncoder` com **ordem fixada a priori** por semântica clínica (`ausente < traços < 1+ < 2+ < 3+`), não por relação com o alvo. Nenhuma numérica é discretizada; os modelos recebem os valores contínuos. A proibição é registrada aqui e em `DICIONARIO_DE_DADOS.md` §5.5 |
| **Teste que detecta** | **`tests/unit/test_features_sem_target_encoding.py`** — (a) assere que o `ColumnTransformer` não contém `TargetEncoder` nem transformador customizado que receba `y` em `fit`; (b) assere que o mapeamento do `OrdinalEncoder` é **exatamente** o literal `['ausente','traços','1+','2+','3+']`, independentemente dos dados; (c) ajusta o pipeline com `y` **embaralhado** e verifica que os parâmetros do pré-processamento não mudam |

A verificação (c) é a mais geral das três: **se o pré-processamento não olha o alvo, embaralhar o
alvo não pode mudar nada nele.** Ela pega qualquer forma de dependência do alvo, inclusive as que
ninguém antecipou ao escrever o teste.

---

### VAZ-06 — Registros duplicados entre splits

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-06 |
| **Tipo** | Vazamento por duplicação (*duplicate leakage*) |
| **Descrição** | O mesmo registro, ou um registro efetivamente idêntico, aparece no treino e no teste. O modelo memoriza e a métrica de teste mede memorização |
| **Como ocorreria neste projeto** | Duas formas, com naturezas muito diferentes. **(a) Mesmo `registro_id` em dois splits** — só ocorreria por bug na função `dividir()` (ex.: concatenar os índices em vez de particioná-los). É erro de código, e é **fatal**. **(b) Registros distintos com features idênticas** em splits diferentes — isto é **matematicamente inevitável** com 10 features binárias e contagens pequenas, e **não é defeito**: os dois registros podem inclusive ter rótulos opostos, por causa da amostragem de Bernoulli |
| **Severidade** | **Crítico** para (a); **Baixo e esperado** para (b) |
| **Controle preventivo** | **(a)** `dividir()` particiona o índice por `train_test_split` em dois passos, sem possibilidade de sobreposição; o manifesto grava `split_sha256`. **(b)** Nenhum controle — é propriedade do espaço de features. A contagem é **reportada** em `QUALIDADE_DOS_DADOS.md` §4.5 e entra no cálculo do teto teórico de desempenho em `METRICAS_E_RESULTADOS.md` §11 |
| **Teste que detecta** | **`tests/unit/test_dataset_sem_vazamento.py`** — interseção de `registro_id` entre os três splits deve ser **vazia**, duas a duas. Para (b), `tests/unit/test_qualidade_dataset.py` apenas **conta e reporta**, sem assertiva de zero |

A distinção entre (a) e (b) é o que impede dois erros opostos: tratar (b) como vazamento levaria a
"deduplicar" um dataset onde a duplicação é informação legítima sobre o erro de Bayes; tratar (a)
como aceitável invalidaria todo o teste.

---

### VAZ-07 — Coeficientes do gerador reutilizados como conhecimento do modelo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-07 |
| **Tipo** | Vazamento do processo gerador para o modelador (*researcher degrees of freedom* / vazamento por projeto) |
| **Descrição** | Conhecimento sobre **como os rótulos foram gerados** é incorporado ao modelo ou às decisões de modelagem, em vez de ser aprendido dos dados |
| **Como ocorreria neste projeto** | Este é o risco mais sutil do registro, porque **não passa pelos dados** — passa por nós. `ESTRATEGIA_DE_ROTULAGEM.md` §2 publica os 23 coeficientes β exatos e as 3 interações. Quem escreve `lib/ml/train.py` conhece todos eles. Formas concretas em que isso vaza: <br>**(a)** Inicializar a Regressão Logística com os β do gerador como `coef_` ou como prior. <br>**(b)** Criar features de engenharia que são **exatamente** os termos do gerador — `idade_ge_35_x_has_cronica`, `imc_ge_30_x_diabetes`, `gemelaridade_x_pas_centrada`. O modelo receberia de graça a estrutura não-linear que o experimento existe para testar se ele consegue descobrir. <br>**(c)** Fixar `max_depth=3` no Random Forest "porque sabemos que há 3 interações". <br>**(d)** Centrar `pas_mmhg` em 120, `pad_mmhg` em 75 e `imc` em 24 — os **mesmos centros** do gerador — em vez de usar a média do treino. <br>**(e)** Escolher o grid de hiperparâmetros por tentativa até que os coeficientes estimados se aproximem dos β conhecidos |
| **Severidade** | **Alto** — e invisível a qualquer auditoria dos dados, porque os dados estão corretos |
| **Por que importa tanto aqui** | `ESTRATEGIA_DE_ROTULAGEM.md` §2 declara que as interações existem justamente para "dar ao Random Forest algo que a Regressão Logística não captura sem engenharia manual". Se fizermos a engenharia manual, destruímos a única diferença que torna a comparação entre os dois modelos informativa. O experimento continuaria rodando e produziria um empate perfeito — que seria reportado como "os modelos são equivalentes", uma conclusão falsa gerada por uma decisão nossa |
| **Controle preventivo** | **(1)** Nenhuma feature de engenharia na v1.0.0 — as 24 colunas do contrato entram cruas. **(2)** Nenhum modelo recebe `coef_`, `init`, prior ou *warm start* derivado dos β. **(3)** Centragem e escala **exclusivamente** por `StandardScaler` ajustado no treino; nenhum centro literal no código. **(4)** O grid de hiperparâmetros é declarado em `MODELOS_AVALIADOS.md` §3 **antes** do primeiro treino e não é alterado depois de ver resultados; alteração exige registro com justificativa. **(5)** Quem implementa `lib/ml/train.py` não consulta os β para tomar decisão de modelagem — apenas para a verificação de sanidade **pós-treino** descrita abaixo |
| **Teste que detecta** | **`tests/unit/test_sem_engenharia_de_features.py`** — assere que `set(FEATURES)` é exatamente o conjunto de colunas do contrato, sem nenhuma coluna derivada de produto, indicador de corte ou centragem literal; busca textual por constantes suspeitas (`120`, `75`, `24`, `28`) no código de features; assere que `LogisticRegression` é instanciada sem `coef_` pré-definido e com `warm_start=False` |

**A distinção que salva o uso legítimo.** Comparar os coeficientes **estimados** com os β do
gerador **depois** do treino é análise válida e desejável — é uma verificação de recuperação de
parâmetros, e entra em `METRICAS_E_RESULTADOS.md` §11 como insumo do teto teórico. O que é vedado
é usar os β **antes ou durante** para orientar a modelagem. A fronteira é temporal e direcional: os
β podem informar a **interpretação**, nunca o **ajuste**.

---

### VAZ-08 — Padrão de ausência correlacionado com o alvo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-08 |
| **Tipo** | Vazamento pelo mecanismo de ausência (MNAR não declarado) |
| **Descrição** | A ausência de uma feature depende do alvo. O indicador de ausência passa a ser, ele próprio, preditor do rótulo — e por um caminho que não existiria em produção |
| **Como ocorreria neste projeto** | O gerador especifica MCAR para `hemoglobina_g_dl`, `glicemia_jejum_mg_dl` e `escolaridade_anos`, e MAR (dependente de `ig_semanas`) para `proteinuria_fita`. Se a implementação aplicasse a máscara **depois** de ordenar por risco, ou usasse o mesmo `rng` já consumido pela amostragem de Bernoulli de um jeito que correlacionasse os dois fluxos, a ausência passaria a carregar informação do alvo. O modelo aprenderia "exame faltando ⇒ risco maior" — uma relação que **nós** criamos por acidente e que não tem contrapartida no mundo. É um erro de implementação que não viola nenhuma restrição de domínio e não aparece em nenhuma verificação de consistência |
| **Severidade** | **Médio** |
| **Controle preventivo** | **(1)** A ordem vinculante de operações (`DICIONARIO_DE_DADOS.md` §7.2) determina que as máscaras são aplicadas **depois** da amostragem do rótulo, em passo separado, a partir de um fluxo de `rng` próprio. **(2)** A distinção entre ausência **estrutural** (`intervalo_interpartal_meses` em nulíparas) e ausência por **não-coleta** é preservada por coluna indicadora, para que o modelo não confunda "não se aplica" com "não medido" |
| **Teste que detecta** | **`tests/unit/test_qualidade_dataset.py`** — verificação MAR-não-MNAR da dimensão D1 (`QUALIDADE_DOS_DADOS.md` §4.2): a taxa de ausência de cada coluna, **condicional ao alvo e dentro de cada faixa de `ig_semanas`**, deve ser estatisticamente indistinguível entre `alto_risco = 0` e `alto_risco = 1` |

---

### VAZ-09 — Ordem do dataset correlacionada com o alvo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-09 |
| **Tipo** | Vazamento por ordenação |
| **Descrição** | O índice ou a ordem física das linhas carrega informação sobre o alvo, e a divisão ou a validação cruzada herda essa estrutura |
| **Como ocorreria neste projeto** | Se o gerador produzisse primeiro todos os casos de alto risco e depois os demais (ex.: por *rejection sampling* para atingir a prevalência-alvo), uma divisão sem embaralhamento concentraria positivos em um split. O erro correlato mais provável: usar `KFold(shuffle=False)` na validação cruzada |
| **Severidade** | **Médio** |
| **Controle preventivo** | **(1)** O gerador produz cada registro a partir do seu índice, independentemente, sem rejeição nem reordenação (`ESTRATEGIA_DE_ROTULAGEM.md` §5). **(2)** `train_test_split(..., shuffle=True, stratify=y, random_state=42)`. **(3)** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` — `shuffle=True` explícito, nunca o padrão |
| **Teste que detecta** | **`tests/unit/test_split_estratificado.py`** — correlação entre o índice posicional e o alvo próxima de zero; prevalência por split dentro de ± 1 pp do global; assertiva explícita de que o objeto de CV usado tem `shuffle == True` |

---

### VAZ-10 — Divergência entre o pipeline de treino e o de inferência

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-10 |
| **Tipo** | *Training-serving skew* — tecnicamente não é vazamento, mas produz o mesmo sintoma |
| **Descrição** | A transformação aplicada em inferência difere da aplicada em treino. As métricas de teste descrevem um pipeline que não é o que roda em produção |
| **Como ocorreria neste projeto** | Caminhos concretos: **(a)** `lib/ml/predict.py` reimplementa a imputação em vez de usar o `Pipeline` serializado; **(b)** a ordem das colunas do `DataFrame` de 1 linha montado a partir de `GestanteFeatures` difere da ordem do treino — sklearn com `ColumnTransformer` por nome é robusto a isso, mas por posição não é; **(c)** um booleano chega como `True`/`False` no treino e como `1`/`0` ou `'sim'` na inferência; **(d)** o limiar não é carregado e a inferência usa 0,5 por padrão |
| **Severidade** | **Alto** — as métricas reportadas deixam de descrever o sistema real |
| **Controle preventivo** | **(1)** O `Pipeline` serializado contém pré-processamento **e** estimador; `predict.py` só chama `pipeline.predict_proba`. Não há caminho de transformação paralelo. **(2)** O `DataFrame` de inferência é montado a partir de `FEATURES` na ordem canônica, por uma única função compartilhada entre treino e inferência. **(3)** `GestanteFeatures` (Pydantic) normaliza os tipos na fronteira, e `extra='forbid'` impede que um campo renomeado passe em silêncio (`CONTRATO_DE_DADOS.md` §5). **(4)** O limiar vem do `model_card.json`; não existe `0.5` literal no caminho de inferência |
| **Teste que detecta** | **`tests/regression/test_predicao_estavel.py`** — um conjunto fixo de casos de entrada percorre (a) o pipeline de treino aplicado ao `DataFrame` e (b) `lib/ml/predict.py` a partir do payload Pydantic, e as probabilidades devem coincidir até tolerância numérica. Complementado por busca textual proibindo `0.5` como limiar em `predict.py` |

---

### VAZ-11 — Contaminação pela regra determinística usada como rótulo

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-11 |
| **Tipo** | Circularidade experimental |
| **Descrição** | O rótulo é gerado pela mesma regra que um dos modelos comparados implementa. O baseline acerta 100 % por construção e os modelos de ML não têm nada a superar |
| **Como ocorreria neste projeto** | Se `alto_risco` fosse gerado por `CRITERIOS_ALTO_RISCO` (`obstetrico.py:50-66`), o baseline determinístico — que é o modelo #1 do catálogo — teria acurácia perfeita. A comparação inteira perderia o sentido |
| **Severidade** | **Crítico** (se ocorresse) |
| **Estado** | **Mitigado por projeto.** A ADR-004 rejeita explicitamente a rotulagem por regra booleana e adota o modelo latente logístico com interações e amostragem de Bernoulli. A justificativa completa está em `ESTRATEGIA_DE_ROTULAGEM.md` §§1-3 |
| **Controle preventivo** | O gerador não importa `CRITERIOS_ALTO_RISCO` nem replica sua lógica. As diferenças estruturais entre os dois processos — contínuo vs. dicotomizado, com vs. sem interações, estocástico vs. determinístico, pesos diferenciados vs. pesos iguais — estão tabuladas em `ESTRATEGIA_DE_ROTULAGEM.md` §3 |
| **Teste que detecta** | **`tests/unit/test_baseline_regra.py`** — assere que o baseline determinístico, aplicado ao dataset gerado, **não** atinge acurácia perfeita e **não** atinge recall 1,00 com precisão 1,00. Um baseline perfeito seria prova de circularidade. Complementado por busca textual: `lib/ml/dataset.py` não importa de `lib.workflows.obstetrico` |

**Nota sobre o que este teste não pode afirmar.** Ele verifica que o baseline **não é perfeito** —
o que refuta a circularidade total. Ele **não** estabelece qual será o desempenho do baseline, e
nenhum valor esperado é declarado aqui. `ESTRATEGIA_DE_ROTULAGEM.md` §3 antecipa um padrão
qualitativo ("alto recall, baixa precisão"), e essa antecipação é uma **hipótese a testar**, não um
resultado. Se o baseline tiver alta precisão, isso será reportado como achado contrário à
expectativa, não ajustado.

---

### VAZ-12 — Documentação preenchida por número não rastreável

| Campo | Conteúdo |
|---|---|
| **ID** | VAZ-12 |
| **Tipo** | Vazamento de credibilidade (não é vazamento estatístico) |
| **Descrição** | Um número aparece num documento de resultados sem corresponder a um artefato de execução |
| **Como ocorreria neste projeto** | Preencher `METRICAS_E_RESULTADOS.md` com valores plausíveis "para ver como fica a tabela"; copiar um número de uma execução antiga após mudar o pipeline; arredondar um valor à mão e perder a correspondência com o JSON; escrever um valor esperado num teste (`assert recall == 0.91`) que depois é lido como resultado |
| **Severidade** | **Crítico** para a integridade do projeto — é a violação direta das regras 4, 5 e 7 da §11 do prompt mestre e do critério de aceite **ML-AC-07** |
| **Controle preventivo** | **(1)** Documentos de resultado nascem como **templates com `—`** e banner de ausência de treino (é o estado atual de `METRICAS_E_RESULTADOS.md` e `COMPARACAO_MODELOS.md`). **(2)** Todo número publicado tem de existir em `artifacts/metrics/*.json`, produzido por `scripts/evaluate.py`. **(3)** Preenchimento por **script de renderização**, não à mão — o que torna estruturalmente impossível publicar um valor ausente do JSON. **(4)** Testes asserem **faixas e propriedades**, nunca valores literais de métrica (`QUALIDADE_DOS_DADOS.md` §3.3) |
| **Teste que detecta** | **`tests/unit/test_documentos_sem_metrica_orfa.py`** — varre `docs/ml/METRICAS_E_RESULTADOS.md` e `docs/ml/COMPARACAO_MODELOS.md` procurando padrões numéricos em células de tabela de resultado; para cada um, exige chave correspondente em `artifacts/metrics/*.json`. Enquanto os documentos forem templates com `—`, o teste passa trivialmente — e **volta a ter dentes** no instante em que o primeiro número for escrito |

---

## 4. Matriz consolidada

| ID | Tipo | Severidade | Controle principal | Teste que detecta | Situação |
|---|---|---|---|---|---|
| VAZ-01 | `risco_latente` como feature | **Crítico** | Allow-list de features | `tests/unit/test_dataset_sem_vazamento.py` | — |
| VAZ-02 | Pré-processamento no dataset todo | Alto | `Pipeline` com `fit` só no treino | `tests/unit/test_pipeline_fit_apenas_treino.py` | — |
| VAZ-03 | Limiar escolhido no teste | Alto | Limiar da validação, gravado antes | `tests/unit/test_limiar_origem_validacao.py` | — |
| VAZ-04 | Consultas repetidas ao teste | Alto | Acesso concentrado em `evaluate.py` + registro | `tests/integration/test_avaliacao_uma_vez.py` | — |
| VAZ-05 | Codificação dependente do alvo | Médio | Target encoding proibido; ordinal fixo | `tests/unit/test_features_sem_target_encoding.py` | — |
| VAZ-06 | Duplicatas entre splits | **Crítico** (a) / Baixo (b) | Partição de índice + `split_sha256` | `tests/unit/test_dataset_sem_vazamento.py` | — |
| VAZ-07 | β do gerador como prior do modelo | Alto | Sem engenharia de features; sem prior | `tests/unit/test_sem_engenharia_de_features.py` | — |
| VAZ-08 | Ausência correlacionada ao alvo | Médio | Máscara depois do rótulo, `rng` próprio | `tests/unit/test_qualidade_dataset.py` | — |
| VAZ-09 | Ordem correlacionada ao alvo | Médio | `shuffle=True` explícito em tudo | `tests/unit/test_split_estratificado.py` | — |
| VAZ-10 | Divergência treino ↔ inferência | Alto | `Pipeline` único serializado | `tests/regression/test_predicao_estavel.py` | — |
| VAZ-11 | Rótulo gerado pela regra do baseline | **Crítico** | Modelo latente ≠ regra (ADR-004) | `tests/unit/test_baseline_regra.py` | — |
| VAZ-12 | Número não rastreável em documento | **Crítico** | Templates + renderização a partir de JSON | `tests/unit/test_documentos_sem_metrica_orfa.py` | — |

**Situação:** vazia em todas as linhas. Nenhum teste existe; nenhum foi executado.

---

## 5. Cobertura por arquivo de teste

| Arquivo de teste | Riscos cobertos | Existe? |
|---|---|---|
| `tests/unit/test_dataset_sem_vazamento.py` | VAZ-01, VAZ-06 | **Não** |
| `tests/unit/test_pipeline_fit_apenas_treino.py` | VAZ-02 | **Não** |
| `tests/unit/test_limiar_origem_validacao.py` | VAZ-03 | **Não** |
| `tests/unit/test_features_sem_target_encoding.py` | VAZ-05 | **Não** |
| `tests/unit/test_sem_engenharia_de_features.py` | VAZ-07 | **Não** |
| `tests/unit/test_qualidade_dataset.py` | VAZ-08 | **Não** |
| `tests/unit/test_split_estratificado.py` | VAZ-09 | **Não** |
| `tests/unit/test_baseline_regra.py` | VAZ-11 | **Não** |
| `tests/unit/test_documentos_sem_metrica_orfa.py` | VAZ-12 | **Não** |
| `tests/integration/test_avaliacao_uma_vez.py` | VAZ-04 | **Não** |
| `tests/integration/test_treino_completo.py` | VAZ-04 (espião) | **Não** |
| `tests/regression/test_predicao_estavel.py` | VAZ-10 | **Não** |

Todos os 12 riscos têm ao menos um teste nomeado. **Nenhum dos 12 arquivos existe.**

---

## 6. Riscos que NÃO se aplicam a este projeto

Registrados para que a ausência seja deliberada e não pareça esquecimento — e, sobretudo, para que
não sejam esquecidos se o projeto algum dia usar dados reais.

| Risco clássico | Por que não se aplica aqui | Quando voltaria a valer |
|---|---|---|
| Vazamento temporal (feature do futuro) | Sem dimensão temporal; classificação de estado atual, não predição de evento futuro (`DEFINICAO_DO_PROBLEMA.md` §2) | Qualquer coorte real com datas de coleta e desfecho |
| Vazamento por paciente repetido | Uma linha = uma gestação = uma paciente; não há `paciente_id` no dataset (`ESTRATEGIA_TREINO_TESTE.md` §3.2) | Dado real com múltiplas consultas de pré-natal por gestante |
| Vazamento por centro / unidade | Não há variável de centro (`QUALIDADE_DOS_DADOS.md` §7.4) | Dado multicêntrico — exigiria validação externa por sítio |
| Vazamento por identificador com sinal | `registro_id` é UUID determinístico, fora de `X` | ID sequencial por data de atendimento ou por setor |
| Vazamento por feature pós-desfecho | Todas as 24 features são observáveis na consulta, antes de qualquer classificação | Variáveis registradas após o encaminhamento (ex.: "nº de consultas no pré-natal de alto risco") |
| Vazamento por deduplicação incorreta | Não há duplicatas de cadastro; os registros são gerados, não coletados | Prontuários com cadastro duplicado da mesma paciente |

A quinta linha merece destaque porque é a mais fácil de introduzir sem perceber numa evolução do
projeto: uma feature como "encaminhada ao pré-natal de alto risco" ou "periodicidade de consulta
definida" é **consequência** da classificação, não insumo dela. Se o dataset algum dia for
enriquecido a partir de `hospital.db` ou de uma coorte real, esta é a verificação a fazer primeiro.

---

## 7. Estado atual

| Item | Estado |
|---|---|
| Riscos identificados | **12** |
| Riscos com controle **projetado** | 12 |
| Riscos com controle **implementado** | **0** |
| Testes nomeados | 12 arquivos |
| Testes **escritos** | **0** |
| Testes **executados** | **0** |
| Dataset gerado | **Não** |
| Modelo treinado | **Não** |
| Conjunto de teste aberto | **Nunca** |

**Nenhuma verificação de vazamento foi executada. Este documento é um plano de controles, não uma
declaração de conformidade.**
