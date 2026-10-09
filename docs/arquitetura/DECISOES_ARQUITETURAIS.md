# Decisões Arquiteturais (ADRs)

**Agente responsável:** `ArchitectureAgent`
**Formato:** Contexto · Problema · Alternativas · Decisão · Justificativa · Consequências · Status

Status possíveis: `Proposta` · `Aceita` · `Rejeitada` · `Substituída` · `Revisar após evidência`

---

## ADR-001 — Evolução aditiva em vez de reescrita

**Contexto.** O projeto tem 14 módulos Python e 10 notebooks funcionais, com LLM fine-tuned, RAG,
4 workflows LangGraph e UI Gradio. A nova fase exige ML supervisionado, explicabilidade, Docker e
testes.

**Problema.** Adicionar uma camada de ML a um sistema orientado a LLM pode justificar uma
reorganização ampla. Vale reescrever?

**Alternativas.**
1. Reescrever como aplicação em camadas com FastAPI e ML no núcleo.
2. Evolução aditiva: criar `lib/ml/`, estender pontos de integração, não remover nada.
3. Projeto paralelo que importa o atual como biblioteca.

**Decisão.** Alternativa 2.

**Justificativa.** A regra §11.2/§11.3 do prompt mestre proíbe apagar funcionalidade e substituir a
arquitetura sem necessidade. Não há necessidade técnica: os pontos de extensão existem e são
limpos — `build_langchain_tools` devolve uma lista, `build_ui` aceita um dicionário de workflows,
`StateGraph` aceita nós novos. Reescrever destruiria a rastreabilidade com a Fase 3, que é parte da
avaliação.

**Consequências.**
- (+) Notebooks 05–10 continuam funcionando; verificado por teste de regressão.
- (+) Diff pequeno e revisável.
- (−) Convive-se com dívidas existentes (caminhos Colab, `TODAY` congelado em três arquivos).
- (−) `lib/` fica maior; mitigado pelo subpacote `lib/ml/`.

**Status.** Aceita.

---

## ADR-002 — Risco gestacional como problema de ML

**Contexto.** É preciso escolher um problema supervisionado clinicamente defensável.

**Problema.** Qual predição adicionar sem que pareça ML enxertado para cumprir requisito?

**Alternativas.**
1. Risco gestacional (`habitual` / `alto_risco`).
2. Risco de não adesão ao rastreamento preventivo.
3. Classificação de urgência na triagem (4 classes).
4. Escore de suspeita de violência.

**Decisão.** Alternativa 1.

**Justificativa.** É a única em que o ML **substitui uma decisão que hoje o LLM toma**. Em
`lib/workflows/obstetrico.py:124-144`, `_avaliar_risco_gestacional` delega a classificação ao LLM
de 3B, passando critérios como texto, sem probabilidade e com `default='habitual'` em caso de falha
de parse — isto é, a falha silenciosa produz falso negativo. Há um problema real a resolver, não um
espaço vazio a preencher.

A alternativa 4 foi descartada por razão ética: transformar detecção de violência doméstica em
escore probabilístico de caixa-preta, com dados sintéticos, é irresponsável. A matriz determinística
existente em `lib/alertas.py` é auditável e deve permanecer determinística.

A alternativa 3 é viável e fica registrada como extensão futura.

**Consequências.**
- (+) Justificativa técnica verificável no código.
- (+) Falsos negativos têm significado clínico claro → sustenta a escolha de recall como métrica.
- (−) Exige dataset sintético, já que não há dados obstétricos estruturados.
- (−) Sobreposição com `CRITERIOS_ALTO_RISCO`; tratada pela ADR-004.

**Status.** Aceita.

---

## ADR-003 — Classificação binária, não ternária

**Contexto.** O prompt mestre §5.7 exemplifica payload com três classes
(`baixo_risco`/`medio_risco`/`alto_risco`).

**Problema.** Seguir o exemplo literalmente ou a estratificação clínica real?

**Alternativas.** (1) Ternário como no exemplo. (2) Binário `habitual`/`alto_risco`. (3) Binário
internamente, ternário na exibição por faixa de probabilidade.

**Decisão.** Alternativa 2, preservando o **formato** do contrato (dicionário `probabilities`
nomeado por classe).

**Justificativa.** A estratificação MS/FEBRASGO é binária, e `ObstetricoState.classificacao_risco`
já usa esse vocabulário (`obstetrico.py:76`). Uma classe "médio risco" seria uma fronteira
arbitrária num dataset que nós mesmos geramos — inventar granularidade que não existe no domínio
para imitar um exemplo de payload seria priorizar a forma sobre o conteúdo. O formato do contrato
é respeitado; apenas a cardinalidade segue a clínica.

**Consequências.**
- (+) Compatível com a UI e o estado existentes.
- (+) Métricas binárias mais simples de auditar.
- (−) Desvio literal do exemplo do enunciado; registrado aqui e em `DEFINICAO_DO_PROBLEMA.md` §3.
- (~) A faixa de probabilidade é exibida na UI, entregando parte da granularidade sem inventar classe.

**Status.** Aceita.

---

## ADR-004 — Rótulo por modelo latente estocástico, não por regra

**Contexto.** O dataset é sintético; a rotulagem precisa ser definida por nós.

**Problema.** Se o rótulo vier de `CRITERIOS_ALTO_RISCO`, o experimento é circular e as métricas
não significam nada.

**Alternativas.**
1. Rótulo = regra booleana dos critérios MS/FEBRASGO.
2. Escore latente logístico + interações + amostragem de Bernoulli.
3. Rotulagem manual de casos.
4. Dataset público real de risco gestacional.

**Decisão.** Alternativa 2.

**Justificativa.** A alternativa 1 é circular: um Random Forest recupera uma disjunção booleana com
F1 ≈ 1,00 e o baseline determinístico acertaria 100 %, deixando o ML sem nada a superar. A
alternativa 3 não escala para 8 000 registros nem temos competência clínica para fazê-la. A
alternativa 4 foi investigada e descartada: os datasets públicos conhecidos de risco materno têm
poucas centenas de registros, features incompatíveis com os protocolos brasileiros e licenças
ambíguas — e usar dado real exigiria discussão ética que o prazo não comporta.

A amostragem de Bernoulli é o elemento decisivo: ela cria erro de Bayes irredutível, impede
desempenho perfeito e torna a comparação entre modelos informativa.

**Consequências.**
- (+) Baseline determinístico e modelos de ML se tornam genuinamente comparáveis.
- (+) Probabilidades podem ser avaliadas quanto à calibração contra `risco_latente`.
- (−) Os coeficientes são de plausibilidade clínica, não estimados de dados — declarado em
  `ESTRATEGIA_DE_ROTULAGEM.md` §2.
- (−) As métricas **não** são validação clínica. Precisa ser dito em todo lugar, inclusive na UI.

**Status.** Aceita.

---

## ADR-005 — Perfis de execução e imagem Docker sem GPU

**Contexto.** Todo o sistema atual depende de Colab + Drive + GPU. O requisito exige Dockerfile
**funcional e comprovadamente testado**.

**Problema.** Uma imagem com PyTorch CUDA, `bitsandbytes` e os pesos do Llama 3B passa de 8 GB,
exige GPU e não pode ser validada na máquina de desenvolvimento (Windows + Docker 29.3.1, sem GPU
confirmada). Declarar Docker funcional sem rodar o build viola a regra §11.6.

**Alternativas.**
1. Imagem única com tudo, validada apenas por `docker build`.
2. Perfis de execução: `ml-only`, `demo-cpu` (LLM stub), `full-gpu`.
3. Sem Docker; documentar apenas execução local.

**Decisão.** Alternativa 2.

**Justificativa.** A camada de ML — que é o núcleo da nova fase — é inteiramente CPU. Separar os
requisitos em `requirements.txt`, `requirements-ml.txt` e `requirements-llm.txt` permite uma imagem
de algumas centenas de MB que roda o pipeline completo (validação → ML → explicabilidade → regras →
RAG → síntese → auditoria) com um `FakeChatModel` determinístico no lugar do Llama. Essa imagem
pode ser construída e **executada** localmente, o que transforma "Dockerfile funcional" de
afirmação em evidência. O perfil `full-gpu` continua documentado para o Colab.

**Consequências.**
- (+) `docker build` e `docker run` verificáveis, com log anexado como evidência.
- (+) Testes e2e viáveis sem GPU.
- (−) A demonstração em Docker usa LLM stub; precisa ser dito com todas as letras no
  `GUIA_DEMO.md` e no roteiro de vídeo.
- (−) Três arquivos de requisitos para manter.

**Status.** Aceita — **pendente de validação por execução real do build.** Nenhum documento pode
afirmar que o Docker funciona antes do log de `docker build` + `docker run` estar anexado em
`docs/deploy/EXECUCAO_DOCKER.md`.

---

## ADR-006 — Regra determinística precede e anula o ML

**Contexto.** Coexistem regras determinísticas de segurança (`SINAIS_ALARME_OBST`, `alertas.py`) e
um classificador probabilístico.

**Problema.** Quem decide quando discordam?

**Alternativas.** (1) ML decide, regra vira feature. (2) Regra executa antes e pode anular o ML.
(3) Combinação ponderada.

**Decisão.** Alternativa 2.

**Justificativa.** Regras de alarme obstétrico codificam sinais de emergência — eclâmpsia iminente,
HELLP, descolamento. Elas têm alta especificidade para condições catastróficas. Permitir que uma
probabilidade de 0,12 rebaixe "crise convulsiva em gestante" é inaceitável, e a alternativa 3
esconderia essa decisão dentro de um peso. A alternativa 2 também é o padrão já usado no projeto:
`triagem.py:127-136` checa `SINAIS_EMERGENCIA` antes de consultar o LLM.

**Consequências.**
- (+) Comportamento em emergência é determinístico e testável.
- (+) Atende à exigência §11.11 de não misturar regra e inferência sem documentação.
- (−) O ML não roda em casos de emergência; a auditoria registra `modo='bypass_regra'`.

**Status.** Aceita.

---

## ADR-007 — LLM sob contrato somente-leitura dos números

**Contexto.** O LLM precisa comunicar o resultado do ML em linguagem clínica.

**Problema.** Um Llama 3B com tendência documentada a loops repetitivos (`README.md`, limitações
conhecidas) pode reescrever ou inventar probabilidades.

**Alternativas.** (1) Confiar no prompt. (2) Prompt estruturado + verificação pós-geração +
descarte em divergência. (3) Não usar LLM; só template.

**Decisão.** Alternativa 2.

**Justificativa.** Prompt sozinho não é controle — é pedido. A verificação extrai todos os numerais
do texto gerado e confere se cada um aparece no payload (com tolerância de arredondamento); se
houver número não justificado ou contradição de rótulo, o texto é **descartado** e a resposta
estruturada determinística é entregue. A alternativa 3 elimina o risco mas também o valor do LLM,
que é reunir predição, explicação e protocolo num texto coerente.

**Consequências.**
- (+) Impossível o LLM inventar um número e ele chegar ao usuário.
- (+) Degradação graciosa e declarada.
- (−) Latência extra da verificação (baixa — é regex, não segunda chamada ao LLM).
- (−) Respostas podem ser descartadas com frequência num modelo 3B; a taxa será medida e reportada.

**Status.** Aceita.

---

## ADR-008 — SHAP com fallback obrigatório

**Contexto.** Explicabilidade é requisito. O ambiente local é Python 3.13.

**Problema.** `shap` tem dependências compiladas e histórico de atraso no suporte a versões novas
do Python. Tornar a explicabilidade dependente dele é um ponto único de falha.

**Alternativas.** (1) Só SHAP. (2) SHAP com fallback para importância por permutação. (3) Só
coeficientes e `feature_importances_`.

**Decisão.** Alternativa 2.

**Justificativa.** O prompt mestre §5.6 admite "SHAP **ou técnica equivalente quando viável**".
`TreeExplainer` é exato e rápido para Random Forest e é a melhor opção quando disponível. Mas
importância por permutação (`sklearn.inspection.permutation_importance`) é global e não local —
então o fallback local é a contribuição linear `coef × valor_padronizado` para a Regressão
Logística. `lib/ml/explain.py` detecta a disponibilidade em tempo de importação e **registra no
payload qual método foi usado**, para que a explicação nunca seja apresentada como SHAP quando não
for.

**Consequências.**
- (+) Explicabilidade nunca fica indisponível.
- (+) O método usado é auditável no payload e na auditoria.
- (−) Qualidade da explicação varia conforme o método; documentado em `EXPLICABILIDADE.md`.

**Status.** Aceita.

---

## ADR-009 — Camada de configuração por variável de ambiente

**Contexto.** Caminhos Colab estão hardcoded em `lib/db.py:13`, `lib/llm.py:56` e em células de
notebook.

**Problema.** Sem configuração central, nada roda fora do Colab, e Docker é impossível.

**Alternativas.** (1) Manter e sobrescrever por env var caso a caso. (2) `lib/config.py` central
com `.env.example`. (3) Arquivo YAML por ambiente.

**Decisão.** Alternativa 2, **preservando os defaults atuais**.

**Justificativa.** `lib/db.py` já lê `HOSPITAL_DB_PATH`; a mudança generaliza um padrão existente em
vez de introduzir um novo. Manter os defaults Colab garante que os notebooks continuem funcionando
sem edição — requisito da ADR-001. YAML adicionaria dependência e formato sem ganho neste porte.

**Consequências.**
- (+) Execução local, em Docker e no Colab a partir do mesmo código.
- (+) Atende ao requisito não funcional de separar configuração de código.
- (−) Um módulo a mais para manter.

**Status.** Aceita.

---

## ADR-010 — Promoção do validador determinístico para `lib/`

**Contexto.** `referencias/validador_resposta_llm.py` implementa um validador regex completo, com
6 casos de teste que passam, mas está deliberadamente **fora** do pacote: a função
`_esboco_integracao_NAO_USE` (linhas 218-242) levanta `NotImplementedError` e o docstring explica
que a integração foi descartada por latência.

**Problema.** A nova fase exige política anti-alucinação e avisos de segurança aplicados. Reescrever
seria desperdiçar código testado.

**Alternativas.** (1) Manter em `referencias/` e duplicar a lógica. (2) Promover para
`lib/validacao.py` e estender com as verificações numéricas do ML. (3) Importar de `referencias/`.

**Decisão.** Alternativa 2.

**Justificativa.** O motivo original da não integração — latência — aplica-se ao `ValidadorLLM`
(segunda chamada ao modelo, 5–10 s), **não** ao `ValidadorDeterministico`, que é regex e custa
microssegundos. A decisão anterior foi correta para a classe errada. Promovendo o determinístico e
acrescentando a verificação de coerência numérica do ADR-007, ganha-se a política anti-alucinação
quase de graça. O `ValidadorLLM` permanece disponível mas desabilitado por padrão, com a razão
documentada.

**Consequências.**
- (+) Reaproveita código já testado, incluindo os 6 casos do `__main__`.
- (+) `referencias/` deixa de ser código morto.
- (−) Arquivo original precisa ser mantido ou redirecionado; será mantido com nota de depreciação
  para não quebrar referências dos relatórios da Fase 3.

**Status.** Aceita.

---

## ADR-011 — Dataset não versionado, manifesto versionado

**Contexto.** O dataset sintético tem 8 000 linhas em Parquet.

**Problema.** Versionar binários no git incha o repositório; não versionar compromete
reprodutibilidade.

**Alternativas.** (1) Commitar o Parquet. (2) Commitar CSV. (3) Não commitar; commitar gerador +
manifesto com hash. (4) Git LFS.

**Decisão.** Alternativa 3.

**Justificativa.** O gerador é determinístico por semente; o dataset é uma função pura do código
versionado. O manifesto com SHA-256 torna a reprodutibilidade **verificável**:
`scripts/train.py --verificar-dataset` regenera e compara. Git LFS adicionaria dependência de
infraestrutura. A escolha é consistente com o `.gitignore` atual, que já exclui `*.jsonl`, `*.db`
e `files/`.

**Consequências.**
- (+) Repositório enxuto; reprodutibilidade comprovável em vez de declarada.
- (−) Primeiro uso exige rodar a geração (segundos em CPU).
- (−) Mudança de versão de `numpy` pode alterar o fluxo do RNG; mitigado por
  `numpy.random.default_rng` (estável por contrato) e por versão pinada.

**Status.** Aceita.

---

## ADR-012 — Novo workflow dedicado em vez de só estender o obstétrico

**Contexto.** O ML poderia entrar apenas como um nó dentro de `obstetrico.py`.

**Problema.** O workflow mínimo exigido pelo prompt mestre §5.9 tem 11 etapas, incluindo validação,
dados incompletos, human-in-the-loop, explicabilidade e auditoria. Enxertar tudo em `obstetrico.py`
dobraria o arquivo e misturaria responsabilidades.

**Alternativas.** (1) Só estender `obstetrico.py`. (2) Só criar `risco_ml.py`. (3) Criar
`risco_ml.py` **e** adicionar ao obstétrico um nó de ML opcional sob flag.

**Decisão.** Alternativa 3.

**Justificativa.** `risco_ml.py` implementa o workflow completo exigido e é a peça demonstrável.
O nó opcional em `obstetrico.py` — ativado por `ML_RISCO_HABILITADO`, com o caminho LLM preservado
como fallback — mostra o ML melhorando um fluxo existente, que é a evidência mais forte de
integração real. Desligada a flag, o comportamento atual é idêntico, o que mantém a regressão
verde.

**Consequências.**
- (+) Workflow novo limpo, com todas as etapas exigidas.
- (+) Integração real demonstrada no fluxo existente, de forma reversível.
- (−) Dois caminhos para a mesma decisão; mitigado por ambos chamarem `lib/ml/predict.py`.
- (−) Exige teste de regressão nos dois estados da flag.

**Status.** Aceita.

---

## Índice

| ADR | Título | Status |
|---|---|---|
| 001 | Evolução aditiva em vez de reescrita | Aceita |
| 002 | Risco gestacional como problema de ML | Aceita |
| 003 | Classificação binária, não ternária | Aceita |
| 004 | Rótulo por modelo latente estocástico | Aceita |
| 005 | Perfis de execução e Docker sem GPU | Aceita, pendente de validação |
| 006 | Regra determinística precede e anula o ML | Aceita |
| 007 | LLM sob contrato somente-leitura | Aceita |
| 008 | SHAP com fallback obrigatório | Aceita |
| 009 | Configuração por variável de ambiente | Aceita |
| 010 | Promoção do validador determinístico | Aceita |
| 011 | Dataset não versionado, manifesto versionado | Aceita |
| 012 | Workflow dedicado + nó opcional no obstétrico | Aceita |
