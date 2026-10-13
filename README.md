# Guardiã AI — Inteligência Artificial para Saúde e Segurança da Mulher

**Tech Challenge Fase 5**
**Curso: Pós Tech em IA para Devs - FIAP**

**Grupo 63:** 
Evandro Rosa Sampaio, 
Gustavo Brasil Pires Octaviano, 
Paulo Roberto Goncalves, 
Wallace Gomes da Silva.

---

## Sumário

- [O problema](#o-problema)
- [Arquitetura](#arquitetura)
- [Principais resultados](#principais-resultados)
- [Como executar](#como-executar)
- [Entregáveis](#entregáveis)
- [Onde encontrar cada requisito do enunciado](#onde-encontrar-cada-requisito-do-enunciado)
- [Segurança, ética e LGPD](#segurança-ética-e-lgpd)
- [Limitações](#limitações)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Stack técnico](#stack-técnico)
- [Pipeline completo no Colab (Llama + Chroma)](#pipeline-completo-no-colab-llama--chroma)
- [Documentação adicional](#documentação-adicional)

---

## O problema

A Guardiã AI apoia a **equipe de saúde** (médicos, enfermeiros, residentes, técnicos) na análise inicial de um atendimento. Ela não se dirige à paciente. A solução trabalha os dois contextos do desafio:

1. **Saúde da mulher — triagem de gestante (cenário principal).** A partir de 24 variáveis clínicas estruturadas, estima se a gestação é de risco habitual ou de alto risco. Regras de sinais de alarme obstétrico rodam **antes** do modelo: em emergência, o ML é pulado e o caso vai direto para encaminhamento.
2. **Segurança da mulher — relato de violência.** O fluxo de violência analisa o relato, calcula um score de suspeita, consulta protocolos e orienta a notificação SINAN. A notificação nunca é decidida automaticamente: depende de confirmação clínica.

Fluxo da jornada principal:

```
Entrada dos dados → regras de alarme → modelo de ML → explicabilidade
  → consulta a protocolos (RAG) → síntese pela LLM → validação da resposta
  → avisos de segurança → auditoria → apresentação ao profissional
```

A LLM **não classifica** o risco: ela só lê os números já calculados e os explica. Um validador descarta qualquer texto que altere probabilidades ou limiares, e nesse caso a resposta volta a um template determinístico.

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│              UI Gradio — Guardiã AI (6 abas)                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │
       ┌─────────────────────┴──────────────────────────┐
       │  LangGraph: 5 StateGraphs                       │
       │  Triagem | Violência | Obstétrico | Prevenção   │
       │  risco_ml (jornada principal da Fase 5)         │
       │  + agente LangChain ReAct (aba de consulta)     │
       └───────┬────────────────────────────────────────┘
               │
       ┌───────▼────────────────────────────────────────┐
       │  10 tools LangChain (StructuredTool)            │
       │  inclui predizer_risco_gestacional              │
       │  e buscar_protocolo (RAG)                       │
       └─┬───────────────┬──────────────────┬───────────┘
         │               │                  │
   ┌─────▼─────┐  ┌──────▼───────────┐ ┌────▼──────────────────┐
   │ SQLite    │  │ lib/ml           │ │ RAG                   │
   │ prontuário│  │ LogReg / RF      │ │ CPU: lexical, subset  │
   │ log_acesso│  │ explicabilidade  │ │ Colab: Chroma MiniLM  │
   │ predicoes │  └──────────────────┘ └───────────────────────┘
   │ _ml       │
   └───────────┘
         │
   ┌─────▼──────────────────────────────────────────────┐
   │ LLM: FakeChatModel (CPU/Docker) ou                 │
   │      Llama 3.2 3B + QLoRA (Colab, GPU)             │
   └────────────────────────────────────────────────────┘
```

O workflow `risco_ml` ([`lib/workflows/risco_ml.py`](lib/workflows/risco_ml.py)) tem 16 nós e 4 rotas condicionais:

| Modo | Quando acontece | O que o fluxo faz |
|---|---|---|
| `normal` | Dados completos, sem sinal de alarme | ML, explicabilidade, RAG, LLM |
| `bypass_regra` | Relato com sinal de alarme (ex.: pré-eclâmpsia grave) | Pula o ML e indica encaminhamento imediato |
| `incompleto` | Campos obrigatórios ausentes | Não imputa; pede complemento ao profissional (human-in-the-loop) |
| `degradado` | Modelo indisponível | Classifica por regra clínica determinística e avisa |

O grafo do fluxo de risco está em [`lib/workflows/risco_ml.py`](lib/workflows/risco_ml.py).

---

## Principais resultados

**Dados:** 8000 gestantes sintéticas, 24 variáveis, semente 42, prevalência de alto risco de 20,6 %, divisão 5600 / 1200 / 1200 (treino / validação / teste). O SHA-256 do dataset está em [`artifacts/data/risco_gestacional_v1.manifest.json`](artifacts/data/risco_gestacional_v1.manifest.json).

**Modelos comparados no mesmo conjunto de teste** (fonte: [`artifacts/metrics/comparacao.json`](artifacts/metrics/comparacao.json)):

| Modelo | PR-AUC | Recall (alto risco) | Precisão (alto risco) |
|---|---|---|---|
| Dummy (prevalência) | 0,206 | — | — |
| Regra clínica | 0,263 | — | — |
| **Regressão logística (escolhido)** | **0,590** | **0,955** | 0,265 |
| Random forest | 0,557 | 0,947 | 0,246 |

Por que essas métricas e não a acurácia:

- A classe de interesse (alto risco) é minoritária. Um modelo que responde sempre "habitual" teria 79 % de acurácia sem detectar nenhum caso. Por isso o modelo é escolhido pela **PR-AUC**, e a acurácia fica registrada como não decisória.
- Um **falso negativo** (gestante de alto risco classificada como habitual) pode atrasar o encaminhamento e é o erro mais grave. O limiar operacional (0,278, calibrado na validação, não 0,5) prioriza o recall: no teste, só 11 de 247 casos de alto risco passaram despercebidos.
- O custo dessa escolha é a baixa precisão: muitos falsos positivos, que geram avaliações extras feitas pelo profissional. É um custo aceitável para uma ferramenta de triagem que não decide sozinha.

**Explicabilidade:** cada predição mostra as variáveis que mais contribuíram, por coeficientes da regressão logística ou importância das variáveis do random forest. SHAP é usado quando a biblioteca está instalada (é opcional). A implementação está em [`lib/ml/explain.py`](lib/ml/explain.py).

---

## Como executar

O caminho padrão roda em CPU, sem GPU e sem conta no Hugging Face. O pipeline com Llama e Chroma está em [Pipeline completo no Colab](#pipeline-completo-no-colab-llama--chroma).

### Requisitos

- Python 3.12 ou 3.13
- Git
- Docker Desktop (opcional)

### 1. Instalar

```text
git clone https://github.com/Evandrorsampaio/TechChallenger4.git
cd TechChallenger4
pip install -r requirements.txt -r requirements-ml.txt
```

Copie o arquivo de ambiente (Windows: `copy .env.example .env`; Linux/macOS: `cp .env.example .env`). Não é preciso `HF_TOKEN` neste perfil.

### 2. Conferir o dataset e rodar os testes

```text
python scripts/train.py --verificar-dataset
python -m pytest -q
```

`--verificar-dataset` confere o SHA-256 do dataset. Para retreinar os modelos, rode `python scripts/train.py` sem a flag; para reavaliar, `python scripts/evaluate.py`.

### 3. Demo de linha de comando (quatro cenários)

```text
python scripts/run_demo.py
```

Gera `artifacts/demo/D1_sucesso.json`, `D2_incompleto.json`, `D3_emergencia.json` e `D4_degradado.json`, um para cada modo do workflow, com as fontes do RAG (`retrieved_sources`).

### 4. Interface Gradio

```text
python scripts/app.py
```

Abra http://localhost:7860. Escolha uma paciente na barra lateral (nomes gerados pelo Faker). A aba **Risco Gestacional (ML)** executa a jornada principal; a aba **Violência** cobre o contexto de segurança.

### 5. Docker

O `docker compose up` da raiz continua no perfil de CPU, com `FakeChatModel` e o RAG lexical. O mesmo fluxo do Colab (Llama 3.2 3B + índice Chroma) é outro compose.

**CPU, chat de demonstração**

```text
docker build -t techchallenger4-demo:cpu .
docker run --rm techchallenger4-demo:cpu
docker compose up --build
```

A imagem `demo-cpu` não inclui o Llama.

**Colab no Docker (Llama + Chroma)**

1. Aceite a licença de `meta-llama/Llama-3.2-3B-Instruct` na conta Hugging Face e grave o token em `.env` (`HF_TOKEN=`).
2. A imagem copia `files/` (Chroma, adapter em `files/finetune` e `files/hospital.db`). Sem `adapter_final` o contêiner sobe o modelo base.
3. Suba com GPU NVIDIA visível no Docker Desktop (WSL2):

```text
docker compose -f docker-compose.full.yml -f docker-compose.gpu.yml up --build
```

Abra http://localhost:7860. A primeira subida baixa o Llama e o modelo de embedding; o cache fica no volume `hf-cache`.

Sem GPU, o mesmo arquivo sobe o Llama em CPU (lento, sem 4-bit):

```text
docker compose -f docker-compose.full.yml up --build
```

Na máquina, sem Docker, `python scripts/app_full.py` lê a mesma pasta `files/`: índice em `files/chroma`, adapter em `files/finetune` e prontuário em `files/hospital.db`. No contêiner esses caminhos são `/app/files/...`.

### 6. Relatório técnico em PDF

```text
python scripts/export_pdf_html.py
```

Abra o `RELATORIO_TECNICO.html` gerado no Chrome e use Imprimir → Salvar como PDF.

---

## Entregáveis

| Entregável | Onde está | Situação |
|---|---|---|
| Código-fonte | `lib/`, `scripts/` | Pronto |
| Scripts de treino dos modelos | `scripts/train.py`, `scripts/evaluate.py`, `lib/ml/` | Pronto |
| Instruções de execução | [Como executar](#como-executar) | Pronto |
| Interface | Gradio, `python scripts/app.py` | Pronto |
| Dockerfile | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml) | Pronto |
| Relatório técnico | [`RELATORIO_TECNICO.md`](RELATORIO_TECNICO.md) e `.html` | Falta exportar o PDF |
| Vídeo de até 15 minutos | YouTube ou Vimeo, público ou não listado | Falta gravar e publicar o link aqui |

---

## Onde encontrar cada requisito do enunciado

| Requisito | Onde encontrar |
|---|---|
| Dataset relacionado ao problema | [`artifacts/data/`](artifacts/data/) |
| Exploração e preparação dos dados | [`lib/ml/dataset.py`](lib/ml/dataset.py), [`lib/ml/features.py`](lib/ml/features.py) |
| Pelo menos dois modelos comparados | [`lib/ml/train.py`](lib/ml/train.py), [`artifacts/metrics/comparacao.json`](artifacts/metrics/comparacao.json) |
| Justificativa das métricas e impacto dos erros | [Principais resultados](#principais-resultados), [`artifacts/metrics/analise_erros.json`](artifacts/metrics/analise_erros.json) |
| Interpretação do modelo | [`lib/ml/explain.py`](lib/ml/explain.py), [`artifacts/explainability/`](artifacts/explainability/) |
| Integração com LLM | [`lib/llm.py`](lib/llm.py), [`lib/ml/llm_contract.py`](lib/ml/llm_contract.py), nó `sintetizar_com_llm` |
| RAG com indicação da fonte | [`lib/rag_local.py`](lib/rag_local.py), [`06_indexar_protocolos.ipynb`](06_indexar_protocolos.ipynb), campo `retrieved_sources` |
| LangChain / LangGraph | [`lib/workflows/`](lib/workflows/), [`lib/agent.py`](lib/agent.py), [`lib/tools.py`](lib/tools.py) |
| IA como apoio, sem decisão automática | Avisos obrigatórios no fluxo de risco, modo `incompleto`, confirmação clínica no fluxo de violência |
| Registro das análises | Tabelas `predicoes_ml` e `log_acesso` em [`lib/db.py`](lib/db.py) |

---

## Segurança, ética e LGPD

**Limites de atuação** (no prompt do agente e nos workflows):

- Nunca prescreve medicação nem dá diagnóstico definitivo.
- Sinais de alarme obstétrico são tratados por regra determinística, antes do ML.
- Casos suspeitos de violência são sempre encaminhados a profissionais qualificados; a notificação SINAN depende de confirmação clínica.
- Com dados insuficientes, o sistema pede complemento em vez de imputar valores obrigatórios.
- Toda resposta do fluxo de risco gestacional carrega o aviso de apoio à decisão e o aviso de dados sintéticos.

**Auditoria:**

- `predicoes_ml` registra cada análise de risco: usuário, paciente, modelo e versão, versão do dataset, hash das variáveis de entrada, predição, probabilidade, limiar, método de explicação, principais variáveis, regras disparadas e modo de execução.
- `log_acesso` registra cada consulta ou gravação de registros de violência, com timestamp, usuário, paciente e motivo clínico obrigatório (mínimo de 5 caracteres).

**Dados pessoais:** todo o prontuário é sintético (Faker pt_BR, 50 pacientes), o CPF é guardado como hash SHA-256 e os registros de violência ficam em tabela separada.

---

## Limitações

1. **Sem validação clínica.** O dataset tabular e os pares de perguntas e respostas do fine-tuning são sintéticos. As métricas não representam desempenho em pacientes reais.
2. **LLM no perfil CPU/Docker padrão.** `docker compose up` usa o `FakeChatModel`, um dublê determinístico com respostas fixas por padrão de texto. O Llama 3.2 3B com QLoRA sobe no compose `docker-compose.full.yml` (GPU NVIDIA) ou no Colab.
3. **RAG no perfil CPU/Docker.** Usa busca lexical sobre um recorte pequeno dos protocolos ([`artifacts/rag/protocolos_subset.json`](artifacts/rag/protocolos_subset.json)). O índice Chroma completo (1392 trechos de 39 PDFs) fica no Google Drive, fora do Git.
4. **Baixa precisão do classificador.** O limiar prioriza o recall; cerca de três em cada quatro alertas de alto risco são falsos positivos.
5. **Auditoria por hash.** `predicoes_ml` guarda o hash das variáveis de entrada, não os valores.
6. **Sem criptografia at-rest e sem autenticação federada.** O campo `usuario` é simples; em produção viria de OAuth/SSO.
7. **Fine-tuning com regressões.** Ver [resultados do fine-tuning](#resultados-do-fine-tuning).

---

## Estrutura do repositório

```
TechChallenger4/
├── README.md                        ← você está aqui
├── RELATORIO_TECNICO.md / .html     ← relatório técnico da Fase 5
├── Dockerfile / docker-compose.yml  ← perfil demo-cpu
├── requirements*.txt                ← dependências (base, ML, LLM)
│
├── lib/
│   ├── ml/                          ← schema, dataset, features, treino, predição, explicabilidade
│   ├── workflows/                   ← 5 StateGraphs (triagem, violência, obstétrico, prevenção, risco_ml)
│   ├── tools.py                     ← 10 StructuredTools LangChain
│   ├── agent.py                     ← agente LangGraph ReAct
│   ├── ui.py                        ← interface Gradio (6 abas)
│   ├── db.py                        ← SQLite: prontuário, log_acesso, predicoes_ml
│   ├── rag_local.py                 ← retriever lexical (CPU)
│   ├── llm.py / llm_fake.py         ← Llama + QLoRA (Colab) / dublê determinístico (CPU)
│   ├── alertas.py, validacao.py     ← regras determinísticas e validação da resposta da LLM
│   ├── mock_data.py                 ← prontuário sintético (Faker pt_BR)
│   └── templates/                   ← modelos de documentos clínicos (BI-RADS, SINAN, pré-natal...)
│
├── scripts/                         ← train, evaluate, predict, run_demo, app, export_pdf_html
├── artifacts/                       ← data, models, metrics, explainability, rag, demo
├── tests/                           ← unit, integration, e2e, regression
│
├── 01…10_*.ipynb                    ← pipeline LLM + RAG no Colab (Fase 5)
└── COLAB_EXECUTAR.ipynb             ← atalho para subir a aplicação no Colab
```

---

## Stack técnico

| Camada | Tecnologia |
|---|---|
| ML tabular | scikit-learn (regressão logística, random forest, dummy, regra clínica) |
| Explicabilidade | coeficientes lineares, importância de variáveis, SHAP (opcional) |
| Orquestração | LangChain + LangGraph |
| LLM | `FakeChatModel` (CPU/Docker); meta-llama/Llama-3.2-3B-Instruct + QLoRA (Colab) |
| Embeddings / vector store | paraphrase-multilingual-MiniLM-L12-v2 + Chroma (Colab) |
| Base estruturada | SQLite |
| Interface | Gradio Blocks |
| Execução | CPU local, Docker (`demo-cpu`) ou Google Colab com GPU |

---

## Pipeline completo no Colab (Llama + Chroma)

A base de LLM e RAG desta Fase 5 usa fine-tuning QLoRA do Llama 3.2 3B sobre 6414 pares de perguntas e respostas sintéticos derivados de protocolos do Ministério da Saúde, FEBRASGO, OMS e INCA, e RAG sobre 1392 trechos desses protocolos.

**Atalho:** abra [`COLAB_EXECUTAR.ipynb`](COLAB_EXECUTAR.ipynb) no Colab com GPU e execute tudo. Ele clona o repositório, monta o Drive e sobe o Gradio com link público (`share=True`). Com `HF_TOKEN` e GPU carrega o Llama; sem eles, usa o `FakeChatModel`. Não refaz o treino QLoRA.

### Pré-requisitos

1. Google Colab Pro (ou Pro+) com GPU A100 ou L4.
2. Conta no Hugging Face com acesso aprovado pela Meta a `Llama-3.1-8B-Instruct` e `Llama-3.2-3B-Instruct`.
3. Google Drive com a estrutura:
   ```
   /MyDrive/AssistenteHospitalar/
   ├── .env          ← HF_TOKEN=hf_xxx
   ├── lib/          ← cópia da pasta lib/ deste repositório
   └── files/        ← PDFs dos protocolos (opcional, só para refazer a extração)
   ```

A pasta `lib/` precisa ficar diretamente em `AssistenteHospitalar/`, porque os notebooks fazem `sys.path.insert(0, '/content/drive/MyDrive/AssistenteHospitalar')` antes de `from lib import ...`.

### Notebooks

| # | Notebook | Saída | Tempo |
|---|---|---|---|
| 01 | [`01_extrair_protocolos.ipynb`](01_extrair_protocolos.ipynb) | `files/fontes_saude_mulher_v2.json` (39 PDFs estruturados) | 5 min |
| 02 | [`02_gerar_dataset_sft.ipynb`](02_gerar_dataset_sft.ipynb) | `files/sft/sft_train.jsonl` (5134 exemplos) + validação/teste | 6–8 h em A100 |
| 03 | [`03_treinar_qlora.ipynb`](03_treinar_qlora.ipynb) | `files/finetune/llama32-3b-saude-mulher_<ts>/adapter_final/` | 2–3 h em A100 |
| 04 | [`04_avaliar_modelo.ipynb`](04_avaliar_modelo.ipynb) | `eval_report.json` + `eval_sidebyside.md` | 5 min |
| 05 | [`05_gerar_dados_mock.ipynb`](05_gerar_dados_mock.ipynb) | `files/hospital.db` (50 pacientes sintéticas) | < 1 min |
| 06 | [`06_indexar_protocolos.ipynb`](06_indexar_protocolos.ipynb) | `files/chroma/` (1392 trechos indexados) | ~5 min |
| 07 | [`07_testar_tools_alertas.ipynb`](07_testar_tools_alertas.ipynb) | verificação das tools | 2 min |
| 08 | [`08_app_gradio.ipynb`](08_app_gradio.ipynb) | link público do Gradio (≈ 72 h) | 3 min |
| 09 | [`09_demo_workflows.ipynb`](09_demo_workflows.ipynb) | demos dos workflows + diagramas Mermaid | 5 min |
| 10 | [`10_relatorio_utilizacao.ipynb`](10_relatorio_utilizacao.ipynb) | relatório gerencial: cobertura preventiva, auditoria LGPD, indicadores | 1 min |

03 e 04 dependem de 02. 05 e 06 são independentes entre si. 07, 08 e 09 precisam de 05 e 06 (e, idealmente, de 03 e 04 para o adapter).

### Categorias de protocolos

| Categoria | Slug interno | Sensível | PDFs | Trechos |
|---|---|---|---|---|
| Ginecologia e obstetrícia | `ginecologia_obstetricia` | não | 19 | 257 |
| Câncer de mama e colo | `cancer_mama_colo` | não | 4 | 242 |
| Planejamento familiar | `planejamento_familiar` | não | 6 | 484 |
| Violência doméstica | `violencia_domestica` | **sim** | 8 | 237 |
| Saúde mental | `saude_mental` | **sim** | 2 | 172 |
| **Total** | — | — | **39** | **1392** |

Categorias sensíveis recebem prompts diferenciados na geração do dataset (encaminhamento SINAN, escuta qualificada, rede de proteção) e ativam o fluxo dedicado de violência.

### Resultados do fine-tuning

Run `llama32-3b-saude-mulher_20260524_0217`, avaliado em 30 exemplos do conjunto de teste.

Ganhos:

- Citação de serviços da rede (SINAN, Ligue 180, CVV, CAPS) em casos sensíveis subiu de cerca de 33 % (modelo base) para cerca de 100 % (fine-tuned).
- Tom mais alinhado ao público profissional.

Regressões:

- ROUGE-L caiu de 0,101 para 0,095 (−5,9 %).
- Cerca de 60 % das respostas apresentavam loops repetitivos; mitigado com `repetition_penalty=1.2` e `no_repeat_ngram_size=4` em [`lib/llm.py`](lib/llm.py).
- O modelo passou a citar serviços da rede também em contextos não sensíveis.
- Respostas 18,6 % mais longas; mitigado com `max_new_tokens=256`.

A amostra de avaliação é pequena (n = 30); conclusões estatísticas exigiriam n ≥ 100 com bootstrap.

---

## Documentação adicional

- [`RELATORIO_TECNICO.md`](RELATORIO_TECNICO.md) — relatório técnico da Fase 5
