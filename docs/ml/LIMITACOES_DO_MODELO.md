> **Limitações empíricas (teste, LogReg):** 11 FN / 655 FP no split de teste com limiar de recall. Precisão positiva 0,265 — a operação privilegia sensibilidade. Subgrupos em `artifacts/metrics/analise_erros.json`. Baseline regra com limiar 0,0 é inútil como escore. Dados 100 % sintéticos.

# Limitações do Modelo


**Agente responsável:** `MachineLearningAgent`
**Status:** Limitações estruturais declaradas — **nenhum modelo treinado; limitações empíricas ainda não mensuráveis**
**Base normativa:** `DEFINICAO_DO_PROBLEMA.md` §7, `ESTRATEGIA_DE_ROTULAGEM.md` §6, `QUALIDADE_DOS_DADOS.md` §7

---

> ## ⚠ DUAS CATEGORIAS DE LIMITAÇÃO, E A DIFERENÇA IMPORTA
>
> **Limitações estruturais** decorrem do desenho do projeto e são conhecidas **antes** de qualquer
> treino: os dados são sintéticos, a prevalência é uma escolha nossa, não há validação clínica.
> Estas estão integralmente documentadas aqui e **não dependem de nenhum resultado**.
>
> **Limitações empíricas** só podem ser medidas depois do treino: desempenho desigual por subgrupo,
> qualidade da calibração, magnitude do sobreajuste. Estas aparecem como `— _PENDENTE_` e serão
> preenchidas a partir de `artifacts/metrics/`.
>
> **Nenhum modelo foi treinado.** Nenhuma limitação empírica foi medida. A ausência de números nas
> seções 3.4 a 3.6 não é omissão: é o estado correto do projeto.

---

## 1. A limitação que subordina todas as outras

> **O modelo é treinado em dados 100 % sintéticos, gerados por um processo estatístico que nós
> mesmos definimos.**
>
> Qualquer métrica obtida mede **a capacidade do modelo de recuperar o nosso próprio gerador**.
> Nada além disso.

Isso não é uma ressalva de rodapé — é o enquadramento de tudo o que segue. As seções 2 a 6 detalham
limitações específicas, mas nenhuma delas seria removida se fosse corrigida isoladamente. Um modelo
com desempenho excelente, calibração perfeita e explicabilidade impecável **sobre este dataset**
continuaria sem nenhuma evidência de utilidade clínica.

A origem da situação está documentada e não é uma escolha de conveniência: não existe dataset
tabular rotulado neste projeto (`00_INVENTARIO_PROJETO.md` §5, `CONTRATO_DE_DADOS.md` §1). O
`hospital.db` tem 50 pacientes, nenhum sinal vital, nenhum laboratório numérico, nenhuma comorbidade
estruturada e nenhuma variável alvo. A geração sintética é o procedimento previsto pelo prompt
mestre §5.4 para exatamente este caso — e o que ela permite demonstrar é **o pipeline**, não a
hipótese clínica.

---

## 2. Limitações dos dados

### 2.1 São sintéticos — e sintéticos de um tipo específico

`CONTRATO_DE_DADOS.md` §2 faz uma distinção de três níveis que costuma ser colapsada e não deveria:

| Categoria | Presente? |
|---|---|
| Dados **reais** de pacientes | **Não.** Nenhum |
| Dados **sintéticos** (processo estatístico definido por nós) | **Sim — 100 %** |
| Dados **simulados a partir de distribuições reais publicadas** | **Não** |

A terceira linha é a que mais se omite. As **faixas** de valores são clinicamente plausíveis (PAS
entre 80 e 200 mmHg, hemoglobina entre 5 e 16 g/dL), mas as **frequências** com que cada valor
ocorre foram escolhidas por nós para produzir um problema de aprendizado interessante. Elas não
foram medidas em população brasileira nem ajustadas a nenhuma publicação.

Dizer "dados sintéticos baseados em distribuições da literatura" seria falso. O correto é: **dados
sintéticos com faixas plausíveis e frequências arbitradas**.

### 2.2 A estrutura de dependência é a que nós escolhemos

Os modelos aprendem exatamente as relações que inserimos no gerador: 23 coeficientes β, 3
interações, e as dependências impostas entre `imc` → `diabetes_previo`, `idade`/`imc` →
`has_cronica`, `has_cronica` → `pas_mmhg`.

Isso valida o **pipeline** — validação, treino, comparação, explicabilidade, integração, auditoria.
Não valida a **hipótese clínica** de que essas variáveis, nessas magnitudes, predizem risco
gestacional.

Um exemplo concreto do que isso significa: `pre_eclampsia_previa` tem β = +1,70, o maior entre os
antecedentes. Se o modelo a destacar nas explicações, isso **não é uma descoberta** — é aritmética
sobre um número que escrevemos. Confundir as duas coisas seria apresentar nossa própria decisão como
achado empírico.

### 2.3 A prevalência de 22 % é uma escolha de projeto

Não é medida epidemiológica brasileira. Foi calibrada pelo intercepto β₀ = −3,10 para produzir
desbalanceamento moderado — suficiente para tornar a acurácia enganosa e exercitar `class_weight`,
sem ser extremo a ponto de inviabilizar o aprendizado.

**Consequência técnica direta e frequentemente ignorada:** VPP e VPN **dependem da prevalência**,
enquanto sensibilidade e especificidade não. Um VPP medido a 22 % de prevalência não transfere para
um serviço com 10 % — nem em ordem de grandeza. Como a nossa prevalência é arbitrada, **VPP e VPN
deste experimento não têm interpretação clínica alguma**, e a ressalva é obrigatória sempre que
forem citados (`METRICAS_E_RESULTADOS.md` §7).

### 2.4 Correlações entre features são simplificadas

Apenas três dependências foram impostas. As seis comorbidades restantes (`cardiopatia`,
`nefropatia`, `tev_previo`, `gemelaridade`, `tabagismo`, `infeccao_sexual_ativa`) são geradas
**independentemente entre si**.

No mundo real, cardiopatia e nefropatia coocorrem; tabagismo associa-se a escolaridade e a
infecções; trombofilia associa-se a antecedentes obstétricos. A rede de dependências é muito mais
densa.

Consequência sobre a explicabilidade: a atribuição SHAP é sensível à correlação entre features
(`EXPLICABILIDADE.md` §7). Com correlações artificialmente esparsas, **as explicações aqui são mais
limpas do que seriam em dado real** — a partição de crédito entre variáveis é mais fácil quando as
variáveis são independentes. É uma limitação que faz o sistema parecer melhor do que é.

### 2.5 Não há viés de seleção

Todos os 8 000 registros "compareceram à consulta" e "foram registrados". Não há mecanismo de
seleção algum.

Em dado real, quem chega ao pré-natal é uma amostra selecionada: gestantes que acessaram o serviço,
compareceram e tiveram os dados registrados. As que não aparecem são sistematicamente diferentes —
e frequentemente as de maior risco. O desempenho medido aqui é, por isso, um **limite superior
otimista** em relação a qualquer implantação.

### 2.6 Não há viés de aferição além de ruído gaussiano mínimo

O único erro de medida é `N(0, 4)` sobre `pas_mmhg` e `pad_mmhg` — gaussiano, centrado em zero,
independente de tudo. É a forma mais benigna que erro de medida pode ter.

Ausentes, todos eles listados em `QUALIDADE_DOS_DADOS.md` §7.3: manguito inadequado em paciente
obesa (erro **correlacionado com o IMC**), arredondamento de PA para múltiplos de 10, hipertensão do
avental branco, viés por equipamento, glicemia sem jejum adequado, e — o mais sério —
**subnotificação de comorbidade correlacionada com acesso ao serviço**.

O último é o que produz desempenho desigual entre populações no mundo real. Como não existe aqui, a
análise de subgrupo planejada só pode detectar desigualdade originada no **modelo ou na amostragem**,
nunca a originada em viés de aferição.

### 2.7 Não há efeito de centro nem estrutura temporal

Sem variável de unidade, município, profissional ou equipamento. Sem data de coleta, sem janela de
observação, sem deriva.

Duas consequências:

1. A divisão aleatória simples é **válida aqui** e seria **otimista** em dado real
   (`ESTRATEGIA_TREINO_TESTE.md` §3).
2. **Não é possível avaliar estabilidade temporal**, que é validação mínima antes de qualquer
   implantação.

### 2.8 O tamanho de 8 000 registros é uma escolha, não um cálculo de poder

Não houve cálculo formal de tamanho de amostra. 8 000 foi escolhido por ser suficiente para treinar
os modelos com folga, produzir um teste com ≈ 264 positivos, e gerar em segundos numa CPU.

Consequência concreta e antecipada: subgrupos com prevalência entre 1,2 % e 2,0 % (`cardiopatia`,
`nefropatia`, `gemelaridade`, `tev_previo`) terão poucas dezenas de casos no teste, e sua análise
será **inconclusiva por tamanho de amostra** (`METRICAS_E_RESULTADOS.md` §10.4). Isso está declarado
antes da execução, não depois.

### 2.9 O que `hospital.db` não resolve

Poderia parecer que o banco existente mitiga parte do problema. Não mitiga. Das 24 features, apenas
**5 são deriváveis** dele, e **6 das 11 obrigatórias estão ausentes** — incluindo pressão arterial,
IMC e todas as comorbidades (`DICIONARIO_DE_DADOS.md` §9).

Consequência arquitetural: qualquer paciente real do banco cai no caminho
`dados_incompletos → human-in-the-loop`. Isso torna a demonstração genuína, mas **não** aproxima o
treinamento de dados reais.

---

## 3. Limitações do modelo

### 3.1 O que o modelo NÃO prediz

Declaração obrigatória, replicada em toda saída do sistema (`DEFINICAO_DO_PROBLEMA.md` §2.1):

| O modelo **não** prediz | Explicação |
|---|---|
| Desfecho materno | Não estima mortalidade, morbidade grave nem internação em UTI |
| Desfecho fetal ou neonatal | Não estima prematuridade, baixo peso, óbito fetal nem Apgar |
| Complicação específica | Não prediz pré-eclâmpsia, DMG, HELLP, descolamento nem TPP |
| Momento de ocorrência | Não há horizonte temporal — é classificação de **estado atual** |
| Evolução | Não prediz se a gestação vai piorar ou melhorar |
| Conduta | Não indica medicação, via de parto nem momento de interrupção |

O alvo `alto_risco` é uma **categoria de estratificação assistencial** do Ministério da Saúde — a
gestante deve ser acompanhada no pré-natal de alto risco. Não é uma doença, não é um diagnóstico, e
não é um prognóstico.

### 3.2 Não há validade temporal

Sem dimensão temporal nos dados, não há como avaliar se o modelo se mantém estável ao longo do
tempo. Em dado real, mudanças de protocolo, de população, de prática de registro e de critérios
diagnósticos degradam modelos continuamente — é a causa mais comum de falha na implantação, e é
invisível neste experimento.

**Não há plano de monitoramento de deriva** porque não há dado real a monitorar. Se algum dia
houver, o plano é pré-requisito, não opcional (§6).

### 3.3 Não há garantia de calibração fora da distribuição sintética

Mesmo que a calibração dentro do teste seja boa — o que ainda não foi medido —, ela vale para a
distribuição que geramos. Em qualquer população com composição diferente, as probabilidades ficam
sistematicamente deslocadas.

Agravante específico do Random Forest: é conhecido por produzir probabilidades mal calibradas
(`MODELOS_AVALIADOS.md` §5), porque a saída é a fração de árvores que votaram na classe. Se ele for
o modelo escolhido, a interface deve tratar a probabilidade com ressalva explícita
(`COMPARACAO_MODELOS.md` §6.4).

### 3.4 Desempenho por subgrupo — **não medido**

| Subgrupo | Recall | Precisão | Desempenho desigual? |
|---|---|---|---|
| Faixa etária < 16 | — | — | — |
| Faixa etária 16–19 | — | — | — |
| Faixa etária 20–34 | — | — | — |
| Faixa etária 35–39 | — | — | — |
| Faixa etária ≥ 40 | — | — | — |
| 1º trimestre | — | — | — |
| 2º trimestre | — | — | — |
| 3º trimestre | — | — | — |
| Com campos imputados | — | — | — |

_PENDENTE — `artifacts/metrics/<modelo>_subgrupos.json`_

> **Até que estes números existam, a afirmação correta é: "o desempenho por subgrupo é
> desconhecido".** Não é "presumivelmente uniforme". Desempenho desigual é a regra, não a exceção,
> em modelos clínicos — e o ônus é de demonstrar ausência de disparidade, não de presumi-la.

### 3.5 Magnitude do sobreajuste — **não medida**

| Modelo | PR-AUC treino | PR-AUC teste | Lacuna | Sobreajuste relevante? |
|---|---|---|---|---|
| #2 `LogisticRegression` | — | — | — | — |
| #3 `RandomForestClassifier` | — | — | — | — |

_PENDENTE — `artifacts/metrics/<modelo>_{treino,teste}.json`_

### 3.6 Distância até o teto teórico — **não medida**

O rótulo é amostrado de `Bernoulli(p)`, o que cria **erro de Bayes irredutível**: nem o próprio
processo gerador, conhecendo `p` exatamente, prevê o rótulo com certeza. Nenhum modelo pode atingir
ROC-AUC = 1,00.

| Item | Valor |
|---|---|
| Erro de Bayes do gerador | — |
| PR-AUC do classificador oráculo | — |
| % do teto atingida pelo modelo escolhido | — |

_PENDENTE — `artifacts/metrics/teto_teorico.json`_

### 3.7 Limitações herdadas de cada família

| Modelo | Limitação estrutural |
|---|---|
| `LogisticRegression` | Não captura as 3 interações do gerador sem engenharia manual (proibida por **VAZ-07**); não captura efeitos de degrau (`abortos ≥ 2`, `glicemia ≥ 92`); não captura a forma em banheira de `idade`; sensível a multicolinearidade |
| `RandomForestClassifier` | Probabilidades tipicamente mal calibradas; `feature_importances_` por impureza é enviesada para variáveis contínuas; não extrapola fora da faixa de treino; explicação local instável em floresta pequena |
| Baseline por regra | Sem probabilidade; sem limiar ajustável; ignora magnitude; sem interações; pesos iguais para critérios de gravidade muito diferente; opera com 13 de 15 critérios |

### 3.8 O modelo não sabe que não sabe

Não há detecção de *out-of-distribution*. Uma entrada com combinação de valores nunca vista no
treino recebe uma probabilidade com a mesma aparência de confiança que um caso típico.

Mitigação parcial — e é parcial de propósito: a validação Pydantic rejeita valores fora do domínio
do contrato (`CONTRATO_DE_DADOS.md` §5) e campos obrigatórios ausentes não são imputados. Isso
bloqueia entradas **inválidas**, mas não entradas **atípicas dentro do domínio válido**. Uma
gestante de 44 anos, IMC 48, com cardiopatia e nefropatia simultâneas está dentro de todos os
domínios e é provavelmente rara ou ausente no treino — e o modelo não sinalizará isso.

---

## 4. Limitações de uso

### 4.1 Proibições absolutas

| Proibido | Motivo |
|---|---|
| **Uso em paciente real, sob qualquer circunstância** | Modelo treinado em dados sintéticos, sem validação clínica, sem aprovação ética, sem trajetória regulatória |
| **Apresentar como diagnóstico** | "Alto risco" é categoria de estratificação assistencial, não doença |
| **Substituir a avaliação do obstetra** | É camada de apoio à decisão |
| **Decidir conduta automaticamente** | Não há decisão automática em nenhum ponto do fluxo |
| **Citar as métricas como evidência clínica** | Medem recuperação de um gerador que definimos |
| **Usar para alocação de recursos, priorização de fila ou auditoria de profissionais** | Fora do escopo; efeitos adversos previsíveis e não avaliados |

### 4.2 Usos legítimos

| Legítimo | Condição |
|---|---|
| Demonstrar que o pipeline de ML está construído corretamente | Com o aviso de dados sintéticos visível |
| Demonstrar integração ML + RAG + LLM + regras + auditoria | Idem |
| Exercitar os caminhos de exceção (dados incompletos, bypass, modo degradado) | Idem |
| Servir de base metodológica para um estudo com dados reais | Com o protocolo de §6 cumprido |

### 4.3 A regra determinística precede e anula o ML

Não é limitação do modelo, mas define seu lugar e por isso entra aqui. Por ADR-006, se
`SINAIS_ALARME_OBST` detecta sinal de emergência — cefaleia intensa com escotomas e epigastralgia,
crise convulsiva, sangramento —, o encaminhamento é **imediato**, independentemente da probabilidade
do modelo.

> **Uma probabilidade de 0,12 nunca rebaixa "crise convulsiva em gestante".**

A auditoria registra `modo='bypass_regra'` nesses casos, e o modelo simplesmente não roda. Inferência
probabilística não sobrepõe regra determinística de segurança.

### 4.4 O LLM não pode alterar os números

Por ADR-007, o LLM recebe o payload sob contrato **somente-leitura**. Depois da geração, todos os
numerais do texto são extraídos e conferidos contra o payload; havendo número não justificado ou
contradição de rótulo, o texto é **descartado** e a resposta estruturada determinística é entregue.

Limitação a declarar: **a taxa de descarte será medida e reportada**, e pode ser alta num modelo de
3B com tendência documentada a loops repetitivos. Uma taxa alta é degradação declarada, não falha
silenciosa — mas é degradação.

---

## 5. Limitações de explicabilidade

Tratamento completo em `EXPLICABILIDADE.md`. Resumo do que limita a confiança na explicação:

| Limitação | Descrição |
|---|---|
| **SHAP assume independência entre features** | O dataset tem dependências impostas (`idade`/`imc` → `has_cronica` → `pas_mmhg`). Com features correlacionadas, a atribuição de crédito entre elas é ambígua, e o SHAP pode produzir valores que refletem a correlação, não a contribuição |
| **Importância não é causalidade** | Nenhum método de explicabilidade estabelece causa. É a limitação com maior potencial de dano clínico, e origina a política de linguagem de `INTERPRETACAO_DAS_PREDICOES.md` §2 |
| **Instabilidade em floresta pequena** | Com `n_estimators=200` e `min_samples_leaf=1`, registros quase idênticos podem receber atribuições visivelmente diferentes |
| **O método varia** | SHAP quando disponível; contribuição linear ou permutação no fallback (ADR-008). A qualidade da explicação varia com o método, e o método usado é registrado no payload para que a explicação nunca seja apresentada como SHAP quando não é |
| **Explicação global ≠ local** | `permutation_importance` é global e não explica um caso individual |
| **A explicação explica o modelo, não a paciente** | Ela mostra o que **o modelo** usou. Se o modelo estiver errado, a explicação explicará com clareza um raciocínio errado — e a clareza pode aumentar a confiança indevida |

A última linha é a mais perigosa e a menos intuitiva: **uma boa explicação de uma predição ruim é
pior que nenhuma explicação**, porque adiciona credibilidade a um erro.

---

## 6. Riscos de viés de automação

Risco sobre o **uso**, não sobre a técnica — e, num sistema de apoio à decisão clínica, é o que mais
provavelmente causaria dano real.

### 6.1 Os mecanismos

| Mecanismo | Como se manifesta neste sistema |
|---|---|
| **Excesso de confiança na probabilidade** | "0,87" parece mais preciso e mais objetivo que "parece de risco". A precisão decimal sugere uma exatidão que não existe — e que é especialmente ilusória aqui, onde o número vem de dados sintéticos |
| **Erro de omissão** | O profissional deixa de identificar risco que identificaria sozinho, porque o modelo disse "habitual". É o mecanismo mais perigoso, porque o falso negativo do modelo se converte em falso negativo do sistema inteiro |
| **Erro de comissão** | O profissional encaminha contra o próprio julgamento porque o modelo disse "alto risco" |
| **Diluição de responsabilidade** | "O sistema classificou assim" como justificativa de conduta |
| **Autoridade da explicação** | Uma explicação bem formatada, com contribuições e barras, aumenta a confiança independentemente de a predição estar certa |
| **Deriva de uso** | Ferramenta introduzida como apoio passa gradualmente a ser tratada como decisão, sem que nenhuma decisão explícita de mudança seja tomada |

### 6.2 Mitigações desenhadas no sistema

| Mitigação | Onde |
|---|---|
| Probabilidade **sempre** exibida com o limiar, nunca o rótulo isolado | `INTERPRETACAO_DAS_PREDICOES.md` §4 |
| Aviso de dados sintéticos como campo **obrigatório** do payload | `ARQUITETURA_ALVO.md` §5.2 |
| Campos imputados declarados explicitamente na saída | `INTERPRETACAO_DAS_PREDICOES.md` §5 |
| Linguagem não-causal obrigatória | `INTERPRETACAO_DAS_PREDICOES.md` §2 |
| Regra determinística precede e anula o ML | ADR-006 |
| Campo obrigatório ausente **não é imputado** — vai para human-in-the-loop | `CONTRATO_DE_DADOS.md` §5 |
| Modo degradado **declarado**, nunca silencioso | `ARQUITETURA_ALVO.md` §4 |
| Auditoria de toda predição em `predicoes_ml` | ADR-007, ADR-012 |

### 6.3 O que as mitigações NÃO resolvem

Nenhuma delas impede um profissional apressado de ler o rótulo e ignorar o resto. Avisos de
interface têm eficácia decrescente com a exposição — quem vê o mesmo alerta cem vezes para de vê-lo.

**Mitigação real exigiria** treinamento da equipe, governança clínica com revisão periódica dos
casos discordantes, e medição do efeito do sistema sobre a decisão humana. Nada disso é possível
num projeto sem uso real, e fingir que os avisos de interface resolvem o problema seria
precisamente o tipo de otimismo que este documento existe para evitar.

---

## 7. O que seria necessário para uso real

Sequência mínima. Nenhuma etapa é dispensável e a ordem importa — várias são pré-requisito das
seguintes.

### 7.1 Etapas

| # | Etapa | O que envolve | Estado |
|---|---|---|---|
| 1 | **Coorte real** | Dados de gestantes reais com as variáveis medidas e desfecho de estratificação registrado. Tamanho definido por **cálculo de poder**, não por conveniência | **Não iniciado** |
| 2 | **Aprovação ética** | Submissão ao CEP (e à CONEP, conforme o caso), TCLE ou dispensa justificada, plano de proteção de dados conforme a LGPD | **Não iniciado** |
| 3 | **Definição de desfecho auditada** | Critério de "alto risco" validado por especialistas, com concordância interobservador medida. Sem isso, o rótulo é ruído | **Não iniciado** |
| 4 | **Avaliação de qualidade e viés** | Completude, viés de seleção, viés de aferição, efeito de centro — todas as dimensões que `QUALIDADE_DOS_DADOS.md` §7 declara **não avaliáveis** aqui | **Não iniciado** |
| 5 | **Retreinamento e validação interna** | Divisão **por paciente** e **temporal**; validação cruzada agrupada (`ESTRATEGIA_TREINO_TESTE.md` §3.5) | **Não iniciado** |
| 6 | **Validação externa** | Coorte de **outro serviço**, outra região, outro período. É o teste que separa modelo útil de modelo que aprendeu o centro | **Não iniciado** |
| 7 | **Avaliação de equidade** | Desempenho por raça/cor, renda, escolaridade, região, acesso. Disparidade documentada e mitigada antes de qualquer uso | **Não iniciado** |
| 8 | **Calibração no contexto de uso** | Recalibração para a prevalência local; VPP e VPN recalculados no serviço real | **Não iniciado** |
| 9 | **Estudo prospectivo** | Uso em paralelo, sem influenciar conduta, medindo concordância com a decisão clínica e desfechos | **Não iniciado** |
| 10 | **Avaliação de impacto clínico** | O modelo melhora desfechos, ou apenas prediz bem? São perguntas diferentes, e a segunda não implica a primeira. Idealmente ensaio clínico randomizado por *cluster* | **Não iniciado** |
| 11 | **Trajetória regulatória** | Software como Dispositivo Médico (SaMD) — enquadramento, classe de risco e registro na ANVISA | **Não iniciado** |
| 12 | **Governança clínica** | Responsável técnico; protocolo de uso; treinamento; canal de contestação; revisão periódica; plano de descontinuação | **Não iniciado** |
| 13 | **Monitoramento contínuo** | Deriva de distribuição, deriva de desempenho, monitoramento de equidade, gatilhos de retreinamento e de desligamento | **Não iniciado** |

### 7.2 A etapa mais frequentemente omitida

A **10**. Um modelo pode ter excelente desempenho preditivo e **não melhorar desfecho algum** — por
exemplo, se identifica casos que a equipe já identificava, se a informação chega tarde demais para
mudar conduta, ou se o serviço de alto risco não tem capacidade para absorver os encaminhamentos
adicionais.

Predizer bem e ajudar são coisas diferentes. Só a etapa 10 responde a segunda.

### 7.3 Estado consolidado

> **Nenhuma das 13 etapas foi iniciada.** O projeto está integralmente na fase de demonstração
> técnica sobre dados sintéticos.
>
> A distância entre o estado atual e o uso clínico **não é de ajuste fino** — é de todo o percurso
> de validação, e esse percurso é medido em anos, não em iterações de código.

---

## 8. Declaração consolidada

> Este modelo **não foi validado clinicamente** e **não pode ser usado em pacientes reais**.
>
> Ele foi treinado em dados **sintéticos**, gerados por um processo estatístico que nós mesmos
> definimos, com prevalência arbitrada e sem qualquer viés de seleção, de aferição ou de centro.
>
> As métricas que ele produzir medem a capacidade de recuperar **esse processo gerador** — não de
> identificar risco gestacional em gestantes reais.
>
> O sistema é uma **demonstração de arquitetura de ML aplicada à saúde**: mostra que o pipeline de
> validação, treino, comparação, explicabilidade, integração e auditoria está construído
> corretamente. Nada além disso deve ser afirmado, na documentação, na interface ou na apresentação.

---

## 9. Estado atual

| Item | Estado |
|---|---|
| Limitações estruturais documentadas | **Sim — seções 1, 2, 4, 5, 6, 7** |
| Limitações empíricas medidas | **Nenhuma** — seções 3.4, 3.5, 3.6 pendentes |
| Modelos treinados | **0 de 4** |
| Desempenho por subgrupo | **Desconhecido** |
| Calibração | **Não medida** |
| Sobreajuste | **Não medido** |
| Distância até o teto de Bayes | **Não medida** |
| Etapas para uso real concluídas | **0 de 13** |

**Este documento não contém nenhum resultado.** As limitações estruturais são consequência do
desenho e independem de execução; as empíricas aguardam `artifacts/metrics/`.

---

## 10. Documentos relacionados

| Documento | Relação |
|---|---|
| `DEFINICAO_DO_PROBLEMA.md` §7 | Aviso central sobre a natureza dos dados |
| `ESTRATEGIA_DE_ROTULAGEM.md` §6 | Limitações da estratégia de rotulagem |
| `QUALIDADE_DOS_DADOS.md` §7 | Dimensões de qualidade não avaliáveis |
| `EXPLICABILIDADE.md` | Detalhamento das limitações de explicabilidade |
| `INTERPRETACAO_DAS_PREDICOES.md` | Política de linguagem que decorre destas limitações |
| `METRICAS_E_RESULTADOS.md` | Receberá as limitações empíricas |
| `COMPARACAO_MODELOS.md` §5 | Ressalvas de comparabilidade entre modelos |
