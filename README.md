# Assistente Clínico Hospitalar — Saúde da Mulher

Assistente virtual de apoio à equipe de saúde (médicos, enfermeiros, residentes, técnicos) de um hospital especializado em **saúde e segurança da mulher**, construído a partir de:

- **Fine-tuning QLoRA** do Llama 3.2 3B Instruct sobre 6414 pares Q&A sintéticos derivados de protocolos do Ministério da Saúde, FEBRASGO, OMS e INCA;
- **RAG** sobre 1392 chunks dos mesmos protocolos via ChromaDB + embeddings multilíngues;
- **Agente LangChain** com 9 ferramentas estruturadas (prontuário, exames, medicamentos, calendário menstrual, registros de violência);
- **4 fluxos LangGraph** explícitos (Triagem Ginecológica, Detecção de Violência, Obstétrico, Prevenção);
- **UI Gradio** para demonstração ponta-a-ponta.

> **Tech Challenge FIAP — Pós Tech em IA para Devs — Fase 3.**
> Projeto acadêmico. Não substitui avaliação clínica profissional.

---

## Sumário

- [Demonstração](#demonstração)
- [Arquitetura](#arquitetura)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Stack técnico](#stack-técnico)
- [Como rodar](#como-rodar)
- [Pipeline em 9 notebooks](#pipeline-em-9-notebooks)
- [Categorias cobertas](#categorias-cobertas)
- [Segurança, ética e LGPD](#segurança-ética-e-lgpd)
- [Limitações conhecidas](#limitações-conhecidas)
- [Documentação adicional](#documentação-adicional)

---

## Demonstração

Capturas dos 4 fluxos LangGraph rodando ponta-a-ponta estão disponíveis em [`09_demo_workflows.ipynb`](09_demo_workflows.ipynb) (com diagramas Mermaid auto-gerados) e a UI integrada em [`08_app_gradio.ipynb`](08_app_gradio.ipynb).

O vídeo demo (até 15 min) está descrito em [`ROTEIRO_VIDEO.md`](ROTEIRO_VIDEO.md).

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                  UI Gradio (Colab + share=True)                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
       ┌─────────────────────┴─────────────────────┐
       │              4 LangGraph Workflows         │
       │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──┐│
       │  │ Triagem │ │ Violen- │ │ Obstétri-│ │P.││
       │  │ Ginec.  │ │ cia     │ │ co       │ │..││
       │  └────┬────┘ └────┬────┘ └────┬─────┘ └─┬┘│
       └───────┼───────────┼───────────┼─────────┼─┘
               │           │           │         │
       ┌───────▼───────────▼───────────▼─────────▼─────┐
       │  9 Tools (LangChain StructuredTool)            │
       │  consultar_prontuario, historico_exames,       │
       │  exames_atrasados, consultar_medicamento,      │
       │  calendario_menstrual, avaliar_padrao_violencia│
       │  consultar_violencia (auditado LGPD),          │
       │  registrar_violencia, buscar_protocolo (RAG)   │
       └─┬──────────────────────────────────────┬───────┘
         │                                      │
   ┌─────▼─────┐                       ┌────────▼────────┐
   │ SQLite    │                       │ Chroma (RAG)    │
   │ mock      │                       │ 1392 chunks     │
   │ 50 pacs   │                       │ MiniLM 384d     │
   │ + log_    │                       │ multilíngue     │
   │ acesso    │                       └─────────────────┘
   └───────────┘
         │
   ┌─────▼──────────────────────────────────────────────┐
   │ LLM: Llama 3.2 3B Instruct + adapter QLoRA         │
   │       (treinado com 5134 ex SFT em PT-BR)          │
   └────────────────────────────────────────────────────┘
```

Detalhes em [`ARQUITETURA.md`](ARQUITETURA.md).

---

## Estrutura do repositório

```
fine-tuning-rag-documentos-fiap/
├── README.md                              ← você está aqui
├── ARQUITETURA.md                         ← decisões técnicas, schema, contratos
├── RELATORIO_TECNICO.md                   ← relatório executivo (visão de ~3 páginas)
├── RELATORIO_TECNICO_DETALHADO.md         ← relatório acadêmico estendido
├── ROTEIRO_VIDEO.md                       ← roteiro do vídeo demo (≤15 min)
├── .gitignore                             ← exclui .env, dados grandes, adapters
│
├── 01_extrair_protocolos.ipynb            ← PDF → JSON (PyMuPDF)
├── 02_gerar_dataset_sft.ipynb             ← chunking + geração Q&A via Llama 3.1 8B
├── 03_treinar_qlora.ipynb                 ← SFT QLoRA do Llama 3.2 3B
├── 04_avaliar_modelo.ipynb                ← base vs FT (ROUGE + heurísticas)
├── 05_gerar_dados_mock.ipynb              ← popula hospital.db
├── 06_indexar_protocolos.ipynb            ← indexa Chroma
├── 07_testar_tools_alertas.ipynb          ← sanity check das 9 tools
├── 08_app_gradio.ipynb                    ← orquestrador UI completo
├── 09_demo_workflows.ipynb                ← demo dos 4 fluxos + Mermaid
├── 10_relatorio_utilizacao.ipynb          ← relatório gerencial: cobertura, auditoria LGPD, KPIs
│
└── lib/
    ├── db.py                              ← SQLite + 7 tabelas + log LGPD
    ├── mock_data.py                       ← Faker pt_BR + cenários clínicos
    ├── alertas.py                         ← regras determinísticas MS/FEBRASGO
    ├── tools.py                           ← 9 StructuredTools LangChain
    ├── llm.py                             ← load_finetuned + ChatHuggingFace
    ├── agent.py                           ← LangGraph ReAct agent
    ├── ui.py                              ← Gradio Blocks (chat + triagem)
    ├── workflows/
    │   ├── common.py                      ← llm_json, rag_search, estimar_confianca
    │   ├── triagem.py                     ← StateGraph: 7 nodes + edge condicional
    │   ├── violencia.py                   ← StateGraph: 7 nodes + matriz SINAN
    │   ├── obstetrico.py                  ← StateGraph: 7 nodes + alertas obstétricos
    │   └── prevencao.py                   ← StateGraph: 6 nodes + agendamento
    └── templates/                         ← modelos especializados de documentos clínicos
        ├── README.md                      ← índice + instruções de uso
        ├── laudo_mamografia_birads.md     ← laudo BI-RADS (ACR / INCA)
        ├── laudo_colposcopia_biopsia.md   ← colposcopia + AP de colo (IFCPC 2011 / INCA)
        ├── receita_terapia_hormonal.md    ← receita COC/POP/DIU/TRH com checklist FEBRASGO
        ├── acompanhamento_prenatal_puerperio.md  ← caderneta pré-natal + 2 puerperais (EPDS)
        ├── ficha_notificacao_sinan_violencia.md  ← Ficha SINAN compulsória
        └── relatorio_atendimento_violencia.md    ← relatório circunstanciado (Norma Técnica MS)
```

---

## Stack técnico

| Camada | Tecnologia | Versão |
|---|---|---|
| LLM base | meta-llama/Llama-3.2-3B-Instruct | — |
| LLM gerador (dataset) | meta-llama/Llama-3.1-8B-Instruct | — |
| Fine-tuning | QLoRA (4-bit NF4 + bfloat16) | bitsandbytes ≥ 0.45 |
| Treino | TRL SFTTrainer + PEFT | trl ≥ 0.12, peft ≥ 0.13 |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 384d |
| Vector store | Chroma | persistente em Drive |
| Orquestração | LangChain + LangGraph (StateGraph + create_react_agent) | langgraph ≥ 0.2 |
| Base estruturada | SQLite (7 tabelas + log_acesso) | stdlib |
| UI | Gradio Blocks | ≥ 4.x |
| Runtime | Google Colab Pro (A100/L4) | — |

---

## Como rodar

### Pré-requisitos

1. **Google Colab Pro** (ou Pro+) com GPU **A100** ou **L4**.
2. **Conta HuggingFace** com aprovação Meta para `Llama-3.1-8B-Instruct` e `Llama-3.2-3B-Instruct`.
3. **Google Drive** com a seguinte estrutura mínima:
   ```
   /MyDrive/AssistenteHospitalar/
   ├── .env                              ← HF_TOKEN=hf_xxx
   ├── lib/                              ← upload da pasta lib/ deste repo
   │   ├── db.py, tools.py, llm.py, agent.py, ui.py, ...
   │   └── workflows/
   └── files/
       └── (PDFs originais dos protocolos por categoria — opcional, se for refazer extração)
   ```

A pasta `lib/` precisa estar **diretamente em `AssistenteHospitalar/`** (não dentro de subpasta), porque os notebooks fazem `sys.path.insert(0, '/content/drive/MyDrive/AssistenteHospitalar')` e depois `from lib import ...`.

### Pipeline em 9 notebooks

Cada notebook é numerado pela ordem de execução. Saídas de um alimentam o próximo via Drive.

| # | Notebook | Saída | Tempo |
|---|---|---|---|
| 01 | [`01_extrair_protocolos.ipynb`](01_extrair_protocolos.ipynb) | `files/fontes_saude_mulher_v2.json` (39 PDFs estruturados) | 5 min |
| 02 | [`02_gerar_dataset_sft.ipynb`](02_gerar_dataset_sft.ipynb) | `files/sft/sft_train.jsonl` (5134 ex) + val/test | 6-8h em A100 |
| 03 | [`03_treinar_qlora.ipynb`](03_treinar_qlora.ipynb) | `files/finetune/llama32-3b-saude-mulher_<ts>/adapter_final/` | 2-3h em A100 |
| 04 | [`04_avaliar_modelo.ipynb`](04_avaliar_modelo.ipynb) | `eval_report.json` + `eval_sidebyside.md` | 5 min |
| 05 | [`05_gerar_dados_mock.ipynb`](05_gerar_dados_mock.ipynb) | `files/hospital.db` (50 pacientes mock) | <1 min |
| 06 | [`06_indexar_protocolos.ipynb`](06_indexar_protocolos.ipynb) | `files/chroma/` (1392 chunks indexados) | ~5 min |
| 07 | [`07_testar_tools_alertas.ipynb`](07_testar_tools_alertas.ipynb) | logs no notebook (sanity check) | 2 min |
| 08 | [`08_app_gradio.ipynb`](08_app_gradio.ipynb) | URL pública Gradio (≈72h) | 3 min |
| 09 | [`09_demo_workflows.ipynb`](09_demo_workflows.ipynb) | demos dos 4 workflows + diagramas Mermaid | 5 min |
| 10 | [`10_relatorio_utilizacao.ipynb`](10_relatorio_utilizacao.ipynb) | relatório gerencial: cobertura preventiva, auditoria LGPD, indicadores epidemiológicos | 1 min |

**Dependências:** 03 e 04 dependem de 02 (dataset). 05 e 06 são independentes e podem rodar em paralelo. 07/08/09 precisam de 05+06 (e idealmente 03+04 para o adapter).

Após o passo 08 ou 09, o link público do Gradio (via `share=True`) fica ativo por ~72h.

---

## Categorias cobertas

| Categoria | Slug interno | Sensitive | # PDFs | # Chunks |
|---|---|---|---|---|
| Ginecologia e obstetrícia | `ginecologia_obstetricia` | não | 19 | 257 |
| Câncer de mama e colo | `cancer_mama_colo` | não | 4 | 242 |
| Planejamento familiar | `planejamento_familiar` | não | 6 | 484 |
| Violência doméstica | `violencia_domestica` | **sim** | 8 | 237 |
| Saúde mental | `saude_mental` | **sim** | 2 | 172 |
| **Total** | — | — | **39** | **1392** |

Categorias `sensitive: true` recebem prompts diferenciados durante a geração do dataset (foco em encaminhamento SINAN, escuta qualificada, fluxo da rede) e ativam o **fluxo dedicado de violência** no LangGraph.

---

## Segurança, ética e LGPD

### Limites de atuação codificados

Hard-coded no system prompt do agente e nos workflows:

- **NUNCA** prescreve medicação sem validação de especialista
- **NUNCA** diagnostica condições definitivamente
- **SEMPRE** encaminha casos suspeitos de violência para profissionais qualificados (notificação SINAN compulsória)
- **SEMPRE** sugere avaliação presencial para sintomas alarmantes
- **NÃO** se dirige à paciente — é ferramenta de apoio à equipe de saúde

### Auditoria LGPD

Toda chamada à `consultar_violencia` e `registrar_violencia` grava em `log_acesso` com:
- timestamp
- usuario (identificador do profissional)
- tabela acessada
- paciente_id
- **motivo clínico obrigatório** (mínimo 5 caracteres)

### Dados pessoais

- **Mock 100% sintético** via Faker pt_BR (sem dado real)
- **CPF hash** SHA-256 (nunca CPF real)
- Tabela `registros_violencia` em schema separado

### Limites técnicos

- Não há criptografia at-rest (uso acadêmico em mock); para produção, recomenda-se Fernet em `registros_violencia.observacoes`
- Não há autenticação federada — `usuario` é mock simples; em produção viria de OAuth/SSO

---

## Limitações conhecidas

### Resultados do fine-tuning (run `llama32-3b-saude-mulher_20260524_0217`)

**Ganhos confirmados:**
- ✅ Citação de serviços da rede (SINAN, Ligue 180, CVV, CAPS) em casos sensitive saltou de ~33% (base) para ~100% (FT)
- ✅ Tom inicial mais alinhado ao público profissional (não inicia com "Lamento ter de abordar...")

**Regressões mensuráveis:**
- ❌ ROUGE-L caiu de 0.101 para 0.095 (-5.9%) — proxy fraco mas regressão real
- ❌ ~60% das respostas FT apresentam **loops repetitivos** — mitigado com `repetition_penalty=1.2` + `no_repeat_ngram_size=4` aplicados em [`lib/llm.py`](lib/llm.py)
- ❌ FT cita serviços da rede inadequadamente em contextos não-sensitive (overfitting do padrão sensitive)
- ❌ Respostas 18.6% mais longas que o base — mitigado com `max_new_tokens=256`

Análise detalhada no [`RELATORIO_TECNICO_DETALHADO.md`](RELATORIO_TECNICO_DETALHADO.md#43-análise-crítica-honesta-dos-resultados).

### Limitações estruturais

1. **Validação clínica formal pendente** — o dataset é sintético gerado por LLM. Validação por especialistas em ginecologia/obstetrícia é necessária antes de qualquer uso real.
2. **Tool calling do Llama 3.2 3B** pode ter taxa de erro maior que modelos maiores em cenários complexos. Fallback ReAct presente.
3. **RAG enviesado pela base de protocolos** — coberta MS/FEBRASGO/OMS/INCA brasileiros. Pode ter gaps em protocolos institucionais específicos.
4. **Sem feedback de profissionais reais** — métricas atuais são heurísticas + ROUGE-L, não satisfação clínica.
5. **Anonimização** dos dados reais não está implementada como pipeline — apenas demonstrada via mock. Para produção, seria necessário pipeline de PHI removal antes do fine-tuning.
6. **Tamanho amostral da avaliação pequeno** (n=30 de 640 do test set) — para conclusões estatísticas seria necessário n≥100 com bootstrap.

---

## Documentação adicional

- **[`RELATORIO_TECNICO.md`](RELATORIO_TECNICO.md)** — relatório executivo: sumário, arquitetura, fluxogramas LangChain/LangGraph, atendimento aos requisitos
- **[`RELATORIO_TECNICO_DETALHADO.md`](RELATORIO_TECNICO_DETALHADO.md)** — relatório acadêmico estendido: metodologia, métricas, análise de bias, considerações éticas
- **[`ARQUITETURA.md`](ARQUITETURA.md)** — decisões técnicas detalhadas, schemas das bases, contratos das tools
- **[`ROTEIRO_VIDEO.md`](ROTEIRO_VIDEO.md)** — script estruturado do vídeo demonstração

---

## Tech Challenge — Critérios de avaliação

| Critério | Onde encontrar |
|---|---|
| Precisão médica especializada | Dataset baseado em MS/FEBRASGO/OMS/INCA; RAG cita fonte |
| Segurança da paciente | Workflow de violência (notificação SINAN, rede de proteção); limites no system prompt |
| Sensibilidade ética | Prompts diferenciados para `sensitive`; tom técnico (assistente para profissional, não paciente) |
| Aplicabilidade prática | Mock realista de prontuário/exames/violência; UI Gradio funcional |
| Impacto social | Apoio a equipe de saúde da mulher (categoria com déficit de protocolos digitalizados no Brasil) |
| Conformidade regulatória | `log_acesso` (LGPD), CPF hashado, separação de dados sensíveis |
