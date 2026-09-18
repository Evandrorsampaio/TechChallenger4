> **Status (2026-09-18):** predições reais existem (`artifacts/demo/`, `exemplo_local_logreg.json`). Usar os números do JSON, não os exemplos fictícios da §8 sem o rótulo de formato.

Frase obrigatória na UI: “As variáveis que mais contribuíram para esta classificação foram…”.

# Interpretação e Comunicação das Predições


**Agente responsável:** `ExplainabilityAgent`
**Status:** Política definida — **nenhuma predição foi gerada; nenhum modelo foi treinado**
**Base normativa:** ADR-007 (contrato somente-leitura), ADR-008 (SHAP com fallback), `EXPLICABILIDADE.md`
**Implementação alvo:** `lib/ml/llm_contract.py`, `lib/ui.py`, `lib/validacao.py`

---

> ## ⚠ NENHUMA PREDIÇÃO FOI GERADA
>
> Nenhum modelo foi treinado. Nenhuma probabilidade foi calculada. Nenhuma explicação foi produzida.
>
> Os três exemplos da §8 são **modelos de formato com valores fictícios**, rotulados como tais. Eles
> demonstram a **estrutura** da comunicação, não a saída de nenhum modelo. Nenhum número neles
> corresponde a qualquer execução.

---

## 1. O problema que esta política resolve

O modelo produz três coisas: uma probabilidade, um rótulo e um conjunto de contribuições por
variável. Nenhuma das três é autoexplicativa, e cada uma pode ser comunicada de forma que induza
conclusão errada sem que nada de falso seja dito.

| Saída bruta | Risco de comunicação | Consequência |
|---|---|---|
| `0.87` | Parece medida objetiva, com precisão de duas casas | Confiança desproporcional a um número vindo de dados sintéticos |
| `alto_risco` | Parece diagnóstico | Categoria assistencial lida como doença |
| `has_cronica: +0.31` | Parece efeito causal | *"A hipertensão causou o alto risco"* |

O sistema existe para apoiar a decisão de um profissional. Uma comunicação que leve à conclusão
errada anula o benefício e adiciona risco — e esse risco não seria visível em nenhuma métrica.

---

## 2. Política de linguagem — PROIBIDO e PERMITIDO

### 2.1 A fórmula obrigatória

> **"As variáveis que mais contribuíram para esta classificação foram: ..."**

Três propriedades desta formulação, todas deliberadas:

| Propriedade | Efeito |
|---|---|
| **"contribuíram"** | Associação dentro do modelo, não causa no organismo |
| **"para esta classificação"** | Explica a saída **do modelo**, não o estado da paciente |
| **"as variáveis"** | Trata os campos como dados de entrada, não como fatos clínicos estabelecidos |

### 2.2 Proibição central

> **É PROIBIDO afirmar causalidade.** Formulações como *"Esta variável causou o risco"* são
> vedadas em qualquer ponto do sistema: interface, saída do LLM, payload, logs, relatório.

Fundamento em `EXPLICABILIDADE.md` §7.2: SHAP, coeficientes e importância por permutação medem
**associação dentro do modelo**. Nenhum estabelece causa. E neste dataset, ao menos duas relações
são **inversas** à leitura causal ingênua — `pas_mmhg` é parcialmente consequência de `has_cronica`,
e `proteinuria_fita` é manifestação de processo, não sua causa.

### 2.3 Tabela de formulações

#### Sobre a contribuição das variáveis

| ❌ PROIBIDO | ✅ PERMITIDO |
|---|---|
| "A hipertensão crônica **causou** o alto risco" | "**Hipertensão crônica** foi a variável que mais contribuiu para esta classificação" |
| "O IMC elevado **provocou** o aumento do risco" | "O IMC informado **contribuiu para aumentar** a probabilidade estimada pelo modelo" |
| "A idade **é responsável por** 30 % do risco" | "A idade respondeu por **30 % da contribuição total** calculada pelo modelo" |
| "Esses fatores **levaram a** gestação a ser de alto risco" | "Estas foram as variáveis de **maior peso na classificação** do modelo" |
| "A pressão alta **está causando** risco ao bebê" | "A pressão arterial informada **foi um dos fatores considerados** pelo modelo" |
| "A baixa escolaridade **aumenta** o risco gestacional" | "A escolaridade informada contribuiu na direção de **aumentar** a probabilidade estimada. É uma variável **socioeconômica de contexto**, não um fator clínico" |
| "O modelo **descobriu** que a proteinúria é importante" | "A proteinúria esteve entre as variáveis de maior contribuição **neste caso**" |

#### Sobre o resultado

| ❌ PROIBIDO | ✅ PERMITIDO |
|---|---|
| "**Diagnóstico**: gestação de alto risco" | "**Classificação sugerida** pelo modelo: alto risco (estratificação assistencial MS/FEBRASGO)" |
| "A paciente **tem** alto risco" | "O modelo **classificou** este caso como alto risco" |
| "A gestação **é** de alto risco" | "As informações fornecidas **são compatíveis** com a categoria de alto risco, segundo o modelo" |
| "Risco de complicação: 87 %" | "Probabilidade estimada pelo modelo de a gestação **se enquadrar na categoria de alto risco**: 0,87" |
| "87 % de chance de o bebê ter problemas" | *(nenhuma reformulação — o modelo não prediz desfecho fetal)* |
| "**Confirmado** alto risco" | "Classificação sugerida, **pendente de avaliação do obstetra**" |
| "Resultado **negativo**" | "O modelo **não classificou** este caso como alto risco no limiar operacional de 0,31" |

A quinta linha não tem coluna de reformulação: não existe modo correto de dizê-la, porque o modelo
não prediz desfecho fetal (`LIMITACOES_DO_MODELO.md` §3.1). A célula vazia é a resposta.

#### Sobre conduta

| ❌ PROIBIDO | ✅ PERMITIDO |
|---|---|
| "**Encaminhe** a paciente ao pré-natal de alto risco" | "A classificação sugerida é compatível com **avaliação para encaminhamento** ao pré-natal de alto risco" |
| "**Solicite** proteinúria de 24 h" | "Protocolos do MS para esta categoria preveem investigação complementar — **ver protocolo anexo**" |
| "**Inicie** profilaxia com AAS" | *(nenhuma reformulação — o sistema não prescreve)* |
| "A conduta **deve ser** consulta em 7 dias" | "Para a categoria de alto risco, a periodicidade **prevista no protocolo** é de 7 a 14 dias, conforme a IG" |

#### Sobre a natureza do sistema

| ❌ PROIBIDO | ✅ PERMITIDO |
|---|---|
| "Sistema de diagnóstico de risco gestacional" | "Sistema de **apoio à decisão** para estratificação de risco gestacional" |
| "IA médica **validada**" | "Modelo treinado em **dados sintéticos**, **sem validação clínica**" |
| "Precisão de 92 % em risco gestacional" | "Métricas obtidas em **conjunto de teste sintético**. Não representam desempenho em população real" |
| "Modelo treinado com dados de gestantes" | "Modelo treinado com **dados sintéticos gerados programaticamente**. Zero dados de pessoas reais" |
| "O sistema **decide** a classificação" | "O sistema **sugere** uma classificação. A decisão é do profissional" |

#### Sobre incerteza

| ❌ PROIBIDO | ✅ PERMITIDO |
|---|---|
| "**Certamente** alto risco" | "Probabilidade estimada de 0,87, **acima** do limiar operacional de 0,31" |
| "Risco **baixo**, pode ficar tranquila" | "Probabilidade estimada de 0,12, **abaixo** do limiar. **Não exclui** risco — o modelo apenas não o identificou com as variáveis fornecidas" |
| "O modelo **tem certeza**" | "O modelo não expressa certeza. A probabilidade é uma estimativa com incerteza não quantificada individualmente" |
| "Probabilidade **exata** de 0,8712" | "Probabilidade estimada: **0,87**" *(duas casas; ver §4.3)* |

### 2.4 Verbos proibidos — lista fechada para verificação automática

`tests/unit/test_linguagem_nao_causal.py` procura, na saída renderizada e nos templates, as formas
flexionadas de:

| Categoria | Termos |
|---|---|
| Causais diretos | causar, provocar, produzir, gerar, originar, desencadear, acarretar, ocasionar |
| Causais indiretos | levar a, resultar em, ser responsável por, dever-se a, decorrer de |
| Diagnósticos | diagnosticar, confirmar, constatar, comprovar, atestar |
| Prescritivos | prescrever, receitar, indicar (uso de medicamento), administrar |
| Certeza | certamente, com certeza, sem dúvida, garantidamente, definitivamente |

O teste é **por lista de proibição**, o que é reconhecidamente incompleto — uma formulação causal
com outro verbo passaria. É controle de piso, não de teto. A revisão humana dos templates continua
necessária, e isso está registrado para que o teste não gere falsa segurança.

---

## 3. Anatomia de uma explicação comunicada

Sete blocos, em ordem fixa. A ordem não é estética: ela determina o que o leitor apressado vê
primeiro, e a probabilidade precisa vir antes do rótulo.

| # | Bloco | Obrigatório | Conteúdo |
|---|---|---|---|
| 1 | **Aviso de natureza** | **Sim** | Dados sintéticos; sem validação clínica |
| 2 | **Probabilidade e limiar** | **Sim** | Valor estimado, limiar operacional, relação entre os dois |
| 3 | **Classificação sugerida** | **Sim** | Rótulo, sempre subordinado ao bloco 2 |
| 4 | **Variáveis que mais contribuíram** | Sim, se houver explicação local | 5 principais + agregado, com direção |
| 5 | **Método de explicação** | **Sim** | Um dos valores de `EXPLICABILIDADE.md` §5.2 |
| 6 | **Dados imputados** | **Sim**, se houver | Lista dos campos estimados |
| 7 | **Avisos de segurança e limitações** | **Sim** | Não é diagnóstico; não substitui o obstetra |

Blocos 1, 2, 3, 5 e 7 são **sempre** exibidos. O bloco 4 é omitido quando não há explicação local
(método `permutacao` ou `indisponivel`), e nesse caso o bloco 5 declara explicitamente a ausência.

---

## 4. Como a probabilidade é comunicada

### 4.1 Sempre com o limiar

> **Nunca** exibir o rótulo sozinho. **Nunca** exibir a probabilidade sozinha.

Razão: o limiar deste sistema **não é 0,5**. Ele é o menor limiar que atinge recall ≥ 0,90 na
validação (`ESTRATEGIA_TREINO_TESTE.md` §6), portanto é **baixo** — deliberadamente calibrado para
errar na direção segura, capturando mais casos ao custo de mais falsos positivos.

Um profissional que veja "probabilidade 0,35 → alto risco" sem o limiar concluirá que o sistema é
excessivamente sensível, ou que há erro. Vendo "0,35, acima do limiar operacional de 0,31, calibrado
para priorizar a captura de casos de alto risco", a informação fica completa e a decisão
fundamentada.

**Formato obrigatório:**

```
Probabilidade estimada de alto risco: 0,XX
Limiar operacional: 0,YY  (calibrado para recall >= 0,90 no conjunto de validação)
Classificação sugerida: [alto_risco | habitual]
```

### 4.2 Proximidade ao limiar é informação, não ruído

Um caso a 0,32 com limiar 0,31 é qualitativamente diferente de um caso a 0,91. Ambos recebem o
mesmo rótulo, e essa é justamente a informação que a binarização destrói.

| Faixa relativa ao limiar | Texto complementar obrigatório |
|---|---|
| Dentro de ± 0,05 do limiar | "**Resultado próximo ao limiar de decisão.** Pequenas variações nas informações fornecidas poderiam alterar a classificação sugerida" |
| Acima de limiar + 0,30 | "Probabilidade estimada substancialmente acima do limiar" |
| Abaixo de limiar − 0,20 | "Probabilidade estimada consideravelmente abaixo do limiar. **Não exclui risco** — ver limitações" |

A faixa de ± 0,05 devolve, em linguagem, parte da granularidade que a decisão binária removeu — e é
coerente com a ADR-003, que optou por classificação binária mas previu a exibição da faixa de
probabilidade na interface.

### 4.3 Precisão numérica: duas casas decimais

`0,87`, nunca `0,8712`.

Quatro casas sugerem uma exatidão que não existe. A probabilidade vem de um modelo treinado em dados
sintéticos, cuja calibração ainda não foi verificada. O terceiro e o quarto dígitos não carregam
informação — carregam aparência de informação.

---

## 5. Como a incerteza é comunicada

### 5.1 Quatro fontes distintas de incerteza

Elas são diferentes e não devem ser fundidas num único aviso genérico:

| Fonte | Comunicação |
|---|---|
| **Incerteza da estimativa** | Implícita na probabilidade; não há intervalo por predição individual — e isso é declarado |
| **Incerteza da calibração** | Aviso quando o modelo escolhido tem calibração ruim (`COMPARACAO_MODELOS.md` §6.4) |
| **Incerteza por dados imputados** | Lista explícita dos campos estimados (§6) |
| **Incerteza de domínio** | O aviso de dados sintéticos — a maior de todas |

### 5.2 O que NÃO é prometido

> O sistema **não** fornece intervalo de confiança por predição individual.

Os intervalos de `METRICAS_E_RESULTADOS.md` §8 são sobre **métricas agregadas** no conjunto de
teste (recall, precisão, PR-AUC), obtidos por bootstrap. Não são intervalos sobre a probabilidade de
uma gestante específica.

A distinção é técnica e importante: "o recall do modelo está entre 0,88 e 0,94 com 95 % de
confiança" e "a probabilidade desta paciente está entre X e Y" são afirmações de naturezas
diferentes, e só a primeira este sistema sustenta. Apresentar um intervalo agregado ao lado de uma
predição individual seria induzir a segunda leitura.

### 5.3 Texto padrão de incerteza

```
Esta é uma estimativa probabilística, não uma medida. Ela reflete o padrão aprendido
pelo modelo a partir de dados sintéticos e não quantifica a incerteza específica
deste caso.
```

---

## 6. Como os campos imputados são declarados

### 6.1 A regra

> Todo campo cujo valor foi **imputado** é declarado explicitamente na saída, **sempre**, mesmo
> quando não está entre as variáveis de maior contribuição.

Fundamento no contrato (`CONTRATO_DE_DADOS.md` §5): campo **opcional** ausente é imputado e
**registrado na auditoria**; campo **obrigatório** ausente **não é imputado** — levanta
`DadosIncompletosError` e o fluxo vai para human-in-the-loop.

Logo, quando há imputação, ela é sempre de campo opcional — e ainda assim precisa ser declarada,
porque o profissional precisa saber que aquela contribuição foi calculada sobre uma **mediana
populacional**, não sobre um valor medido na paciente.

### 6.2 Formato

```
Dados estimados (não informados):
  • Hemoglobina — valor estimado pela mediana do conjunto de treino
  • Escolaridade — valor estimado pela mediana do conjunto de treino

Estes valores NÃO foram medidos nesta paciente. A estimativa do modelo
para este caso é menos informada do que seria com os dados completos.
```

### 6.3 Marcação dentro da explicação

Quando uma feature imputada está entre as 5 principais, a marcação aparece na própria linha:

```
3. Hemoglobina (valor ESTIMADO, não medido) .......... reduz a probabilidade
```

Sem isso, o profissional leria uma contribuição de hemoglobina como se derivasse de um hemograma da
paciente. O sublinhado da distinção não é redundante com o bloco 6.2: ali é uma lista à parte, que
o leitor pode não conectar às linhas da explicação.

### 6.4 Campos obrigatórios ausentes — não há predição

Quando falta campo obrigatório, **não há probabilidade a comunicar**. A saída é:

```
PREDIÇÃO NÃO REALIZADA — dados obrigatórios ausentes

Campos necessários e não informados:
  • Pressão arterial sistólica
  • Pressão arterial diastólica
  • IMC pré-gestacional

O modelo NÃO estima estes valores. Complete as informações para obter
uma classificação.
```

A recusa em imputar é deliberada (`CONTRATO_DE_DADOS.md` §5): imputar a pressão arterial de uma
gestante pela mediana da população e devolver uma probabilidade como se fosse medida é o tipo de
silêncio perigoso que este sistema deve evitar.

**Nota operacional relevante:** como `hospital.db` não possui 6 das 11 features obrigatórias
(`DICIONARIO_DE_DADOS.md` §9.4), **este é o caminho padrão para qualquer paciente real do banco** —
não um cenário excepcional.

---

## 7. Como o aviso de dados sintéticos é anexado

### 7.1 Campo obrigatório do payload

Por `ARQUITETURA_ALVO.md` §5.2, `aviso_dados_sinteticos` é campo **obrigatório**. Não há caminho de
saída sem ele.

### 7.2 Texto padrão

```
⚠ Modelo treinado em dados SINTÉTICOS. Sem validação clínica.
   Este resultado não constitui evidência de desempenho em população real
   e não deve orientar conduta em pacientes.
```

### 7.3 Onde aparece

| Local | Forma |
|---|---|
| Payload JSON | Campo `aviso_dados_sinteticos` |
| Interface Gradio | Banner fixo **no topo** da aba, sempre visível — não em rodapé, não recolhível |
| Texto do LLM | Primeiro parágrafo, antes de qualquer número |
| Auditoria | Implícito em `dataset_versao` |
| Relatório técnico | Seção destacada |
| Apresentação / vídeo | Declarado verbalmente |

### 7.4 Limite honesto deste controle

Avisos de interface perdem eficácia com a exposição — quem vê o mesmo banner cem vezes para de vê-lo
(`LIMITACOES_DO_MODELO.md` §6.3). O aviso é necessário e **não é suficiente**. Ele não substitui
treinamento da equipe nem governança clínica, e registrar isso evita a falsa sensação de que o
problema do viés de automação foi resolvido por um banner.

---

## 8. Exemplos ilustrativos de formato

> # 🔴 EXEMPLO ILUSTRATIVO DE FORMATO — valores fictícios, nenhum modelo foi treinado
>
> **Os três exemplos abaixo demonstram a ESTRUTURA da comunicação.** Todos os números são
> **inventados para ilustrar o formato**. Nenhum modelo foi treinado, nenhuma probabilidade foi
> calculada, nenhuma explicação foi gerada.
>
> **Nenhum valor abaixo corresponde a qualquer execução deste sistema.**

### 8.1 Exemplo A — classificação de alto risco, dados completos

```
════════════════════════════════════════════════════════════════════
EXEMPLO ILUSTRATIVO DE FORMATO — valores fictícios,
nenhum modelo foi treinado
════════════════════════════════════════════════════════════════════

⚠ Modelo treinado em dados SINTÉTICOS. Sem validação clínica.
  Este resultado não constitui evidência de desempenho em população
  real e não deve orientar conduta em pacientes.

────────────────────────────────────────────────────────────────────
PROBABILIDADE ESTIMADA
────────────────────────────────────────────────────────────────────
  Probabilidade de alto risco ....... 0,XX   [valor fictício]
  Limiar operacional ................ 0,YY   [valor fictício]
                                      (calibrado para recall >= 0,90
                                       no conjunto de validação)

  Probabilidade estimada substancialmente acima do limiar.

────────────────────────────────────────────────────────────────────
CLASSIFICAÇÃO SUGERIDA
────────────────────────────────────────────────────────────────────
  ALTO RISCO
  (categoria de estratificação assistencial MS/FEBRASGO —
   não é diagnóstico de doença)

────────────────────────────────────────────────────────────────────
AS VARIÁVEIS QUE MAIS CONTRIBUÍRAM PARA ESTA CLASSIFICAÇÃO FORAM
────────────────────────────────────────────────────────────────────
  1. Pré-eclâmpsia em gestação anterior ...... aumenta   [+0,XX]
  2. Hipertensão arterial crônica ............ aumenta   [+0,XX]
  3. Pressão arterial sistólica .............. aumenta   [+0,XX]
  4. IMC pré-gestacional ..................... aumenta   [+0,XX]
  5. Idade ................................... aumenta   [+0,XX]
     Demais 19 variáveis (agregado) .......... reduz     [−0,XX]

  [todos os valores acima são fictícios]

  Observação: hipertensão crônica e pressão arterial sistólica são
  variáveis relacionadas entre si. A divisão da contribuição entre
  elas deve ser lida com cautela.

────────────────────────────────────────────────────────────────────
MÉTODO DE EXPLICAÇÃO
────────────────────────────────────────────────────────────────────
  Contribuições calculadas por SHAP (TreeExplainer).
  Verificação de consistência com a predição: OK.

────────────────────────────────────────────────────────────────────
DADOS ESTIMADOS
────────────────────────────────────────────────────────────────────
  Nenhum. Todas as variáveis foram informadas.

────────────────────────────────────────────────────────────────────
AVISOS
────────────────────────────────────────────────────────────────────
  • Este resultado NÃO é um diagnóstico.
  • NÃO substitui a avaliação do obstetra.
  • As variáveis listadas CONTRIBUÍRAM para a classificação do
    modelo. Isso NÃO significa que causaram o risco.
  • Modelo treinado em dados sintéticos, sem validação clínica.
════════════════════════════════════════════════════════════════════
```

### 8.2 Exemplo B — próximo ao limiar, com dados imputados e fallback de explicação

```
════════════════════════════════════════════════════════════════════
EXEMPLO ILUSTRATIVO DE FORMATO — valores fictícios,
nenhum modelo foi treinado
════════════════════════════════════════════════════════════════════

⚠ Modelo treinado em dados SINTÉTICOS. Sem validação clínica.

────────────────────────────────────────────────────────────────────
PROBABILIDADE ESTIMADA
────────────────────────────────────────────────────────────────────
  Probabilidade de alto risco ....... 0,XX   [valor fictício]
  Limiar operacional ................ 0,YY   [valor fictício]

  ⚠ RESULTADO PRÓXIMO AO LIMIAR DE DECISÃO.
    Pequenas variações nas informações fornecidas poderiam alterar
    a classificação sugerida.

────────────────────────────────────────────────────────────────────
CLASSIFICAÇÃO SUGERIDA
────────────────────────────────────────────────────────────────────
  ALTO RISCO  (marginal — ver observação acima)

────────────────────────────────────────────────────────────────────
AS VARIÁVEIS QUE MAIS CONTRIBUÍRAM PARA ESTA CLASSIFICAÇÃO FORAM
────────────────────────────────────────────────────────────────────
  1. Abortos anteriores ...................... aumenta   [+0,XX]
  2. Cesarianas anteriores ................... aumenta   [+0,XX]
  3. Hemoglobina (valor ESTIMADO, não medido)  aumenta   [+0,XX]
  4. Tabagismo ............................... aumenta   [+0,XX]
  5. Escolaridade (valor ESTIMADO) ........... reduz     [−0,XX]
     Demais 19 variáveis (agregado) .......... reduz     [−0,XX]

  [todos os valores acima são fictícios]

────────────────────────────────────────────────────────────────────
MÉTODO DE EXPLICAÇÃO
────────────────────────────────────────────────────────────────────
  ⚠ SHAP indisponível neste ambiente.
    Contribuições estimadas por um modelo linear auxiliar treinado
    no mesmo conjunto de dados. SÃO UMA APROXIMAÇÃO e podem
    divergir do modelo efetivamente usado na predição.
    Verificação de consistência com o modelo auxiliar: OK.

────────────────────────────────────────────────────────────────────
DADOS ESTIMADOS
────────────────────────────────────────────────────────────────────
  • Hemoglobina — estimada pela mediana do conjunto de treino
  • Escolaridade — estimada pela mediana do conjunto de treino

  Estes valores NÃO foram medidos nesta paciente. A estimativa do
  modelo é menos informada do que seria com os dados completos.

────────────────────────────────────────────────────────────────────
AVISOS
────────────────────────────────────────────────────────────────────
  • Este resultado NÃO é um diagnóstico.
  • NÃO substitui a avaliação do obstetra.
  • Duas das cinco variáveis de maior contribuição foram ESTIMADAS.
  • A explicação apresentada é uma APROXIMAÇÃO — ver método acima.
  • Modelo treinado em dados sintéticos, sem validação clínica.
════════════════════════════════════════════════════════════════════
```

### 8.3 Exemplo C — dados obrigatórios ausentes (sem predição)

```
════════════════════════════════════════════════════════════════════
EXEMPLO ILUSTRATIVO DE FORMATO — nenhum modelo foi treinado
════════════════════════════════════════════════════════════════════

⚠ Modelo treinado em dados SINTÉTICOS. Sem validação clínica.

────────────────────────────────────────────────────────────────────
PREDIÇÃO NÃO REALIZADA
────────────────────────────────────────────────────────────────────
  Dados obrigatórios ausentes.

  Campos necessários e não informados:
    • Pressão arterial sistólica (pas_mmhg)
    • Pressão arterial diastólica (pad_mmhg)
    • IMC pré-gestacional (imc_pre_gestacional)
    • Hipertensão arterial crônica (has_cronica)
    • Diabetes prévio (diabetes_previo)
    • Gemelaridade (gemelaridade)

  O modelo NÃO estima estes valores. Imputar pressão arterial pela
  mediana da população e devolver uma probabilidade como se fosse
  medida produziria um número sem correspondência com esta paciente.

────────────────────────────────────────────────────────────────────
PRÓXIMO PASSO
────────────────────────────────────────────────────────────────────
  Complete as informações acima para obter uma classificação.

  Observação: estes campos não existem no prontuário eletrônico
  desta demonstração (hospital.db não possui sinais vitais, dados
  antropométricos nem comorbidades estruturadas). O preenchimento
  manual pelo profissional é parte prevista do fluxo.

────────────────────────────────────────────────────────────────────
DADOS DISPONÍVEIS E VALIDADOS
────────────────────────────────────────────────────────────────────
  • Idade ...................... [derivada da data de nascimento]
  • Idade gestacional .......... [derivada da DUM]
  • Gestações / Partos / Abortos [derivados do G_P_A]

────────────────────────────────────────────────────────────────────
AVISOS
────────────────────────────────────────────────────────────────────
  • Nenhuma classificação foi gerada.
  • A ausência de classificação NÃO indica ausência de risco.
  • A avaliação clínica do obstetra permanece necessária e
    independe deste sistema.
════════════════════════════════════════════════════════════════════
```

> **Reiteração:** os três exemplos acima são **modelos de formato**. Os marcadores `0,XX`, `[+0,XX]`
> e `[valor fictício]` estão no lugar de números que **não existem**, porque nenhum modelo foi
> treinado. Quando o sistema estiver implementado, os valores reais virão de
> `artifacts/models/` e de `lib/ml/explain.py` — nunca deste documento.

---

## 9. Interação com o LLM

### 9.1 O LLM não pode alterar os números

Por ADR-007, o LLM recebe o payload sob contrato **somente-leitura**. `prediction`, `probabilities`,
`threshold` e `contribution` são gerados exclusivamente pelas camadas de ML e explicabilidade.

Após a geração, `lib/validacao.py` extrai **todos os numerais** do texto e confere contra o payload,
com tolerância de arredondamento. Havendo número não justificado ou contradição de rótulo, o texto é
**descartado** e a resposta estruturada determinística é entregue.

### 9.2 O LLM também não pode alterar a linguagem

A política de §2 vale para a saída do LLM. O prompt de síntese inclui as proibições explicitamente,
e `tests/unit/test_linguagem_nao_causal.py` roda sobre a saída renderizada, não apenas sobre os
templates.

**Limitação declarada:** o prompt é um pedido, não um controle (ADR-007). A verificação
pós-geração é o controle. Para a **linguagem**, porém, a verificação é por lista de termos
proibidos — incompleta por natureza (§2.4). O caminho seguro é o descarte: **em dúvida, entrega-se
a resposta estruturada**, que é gerada por template e não por modelo generativo.

### 9.3 Degradação declarada

Quando o texto do LLM é descartado, a interface diz:

```
Síntese em linguagem natural indisponível para este caso
(verificação de consistência numérica não aprovada).
Resultado estruturado apresentado abaixo.
```

Nunca silenciosamente. A taxa de descarte será medida e reportada (`LIMITACOES_DO_MODELO.md` §4.4),
e pode ser alta num modelo de 3B.

---

## 10. Testes associados

| Teste | Verifica | Existe? |
|---|---|---|
| `tests/unit/test_linguagem_nao_causal.py` | Ausência dos termos de §2.4 na saída renderizada e nos templates | **Não** |
| `tests/unit/test_payload_campos_obrigatorios.py` | `aviso_dados_sinteticos`, `threshold`, `metodo_explicacao` e `dados_imputados` sempre presentes | **Não** |
| `tests/unit/test_probabilidade_com_limiar.py` | A saída nunca exibe rótulo sem probabilidade e limiar | **Não** |
| `tests/unit/test_imputacao_declarada.py` | Todo campo imputado aparece na saída e é marcado nas linhas da explicação | **Não** |
| `tests/unit/test_dados_incompletos_sem_predicao.py` | Campo obrigatório ausente ⇒ `DadosIncompletosError`, sem probabilidade na saída | **Não** |
| `tests/integration/test_llm_nao_altera_numeros.py` | Número divergente no texto ⇒ descarte e entrega da resposta estruturada | **Não** |
| `tests/unit/test_precisao_duas_casas.py` | Probabilidades formatadas com 2 casas decimais | **Não** |

---

## 11. Estado atual

| Item | Estado |
|---|---|
| Modelos treinados | **0 de 4** |
| Predições geradas | **Nenhuma** |
| Explicações geradas | **Nenhuma** |
| `lib/ml/llm_contract.py` | **Não implementado** |
| `lib/validacao.py` | **Não implementado** |
| Aba "Risco Gestacional (ML)" na UI | **Não implementada** |
| Testes escritos | **0 de 7** |
| Exemplos com valores reais | **Nenhum** — os três da §8 são formatos fictícios |

> **Confirmação explícita:** este documento **não contém nenhuma predição, probabilidade ou
> contribuição real**. Os três exemplos da §8 são **modelos de formato com marcadores fictícios**,
> rotulados como tais em cada bloco. **Nenhum número deste documento é resultado de execução.**

---

## 12. Documentos relacionados

| Documento | Relação |
|---|---|
| `EXPLICABILIDADE.md` | Define como as contribuições são calculadas e validadas |
| `LIMITACOES_DO_MODELO.md` | Fundamenta as proibições de linguagem e os avisos |
| `METRICAS_E_RESULTADOS.md` | Receberá as métricas que contextualizam as predições |
| `COMPARACAO_MODELOS.md` | Define o modelo e o limiar que serão comunicados |
| `docs/arquitetura/DECISOES_ARQUITETURAIS.md` | ADR-003 (binário), ADR-006 (regra precede ML), ADR-007 (contrato do LLM), ADR-008 (fallback) |
| `docs/arquitetura/ARQUITETURA_ALVO.md` §5.2 | Estrutura do payload |
| `CONTRATO_DE_DADOS.md` §5 | Regras de campo obrigatório ausente e de imputação |
