# Assistente Clínico Hospitalar — Arquitetura (Fase 2)

Documento de arquitetura da segunda etapa do Tech Challenge: pipeline LangChain integrando o LLM fine-tuned (Llama 3.2 3B) com bases especializadas e protocolos clínicos.

**Público-alvo do assistente:** equipe de saúde do hospital (médicos, enfermeiros, residentes, técnicos). **Não** é assistente para a paciente — todas as respostas assumem que o leitor é um profissional durante atendimento.

---

## 1. Diagrama de componentes

```
                ┌───────────────────────────────────────────┐
                │            UI (Gradio ChatInterface)      │
                │  - input: texto livre + dropdown paciente │
                │  - output: resposta + citações + alertas  │
                └────────────────────┬──────────────────────┘
                                     │
                ┌────────────────────▼──────────────────────┐
                │        Agente LangChain (tool calling)    │
                │  - decide quais ferramentas chamar        │
                │  - sintetiza resposta final               │
                └────┬────────────┬──────────┬──────────────┘
                     │            │          │
       ┌─────────────▼──┐  ┌──────▼──────┐  ┌▼─────────────────────┐
       │ Tool: RAG      │  │ Tool: SQL   │  │ Tool: Calendário     │
       │ buscar_proto-  │  │ consultar_  │  │ menstrual / exames   │
       │ colo(query)    │  │ paciente()  │  │ atrasados()          │
       └───────┬────────┘  └──────┬──────┘  └──────┬───────────────┘
               │                  │                │
       ┌───────▼───────┐    ┌─────▼──────┐  ┌─────▼──────────────┐
       │ Chroma /FAISS │    │ SQLite     │  │ SQLite + lógica    │
       │ (protocolos)  │    │ (mock)     │  │ de thresholds      │
       └───────────────┘    └────────────┘  └────────────────────┘
                     │
                ┌────▼──────────────────────────────────────┐
                │     LLM: Llama 3.2 3B Instruct            │
                │  - fine-tuned (QLoRA) com dataset SFT     │
                │  - servido via Transformers no Colab      │
                │  - exposto como LangChain ChatModel       │
                └───────────────────────────────────────────┘
```

---

## 2. Componentes

### 2.1 Inferência (LLM)

| Item | Decisão |
|---|---|
| Modelo | `meta-llama/Llama-3.2-3B-Instruct` + adapter QLoRA treinado na fase 1 |
| Backend | HuggingFace `transformers` (4-bit via bitsandbytes) |
| Wrapper LangChain | `langchain_huggingface.ChatHuggingFace` ou `HuggingFacePipeline` |
| Tool calling | Llama 3.2 suporta tool calling nativo no chat template — usar via `bind_tools()` |
| Runtime | Colab A100/L4, exposto via Gradio + ngrok |

**Fallback:** se o tool calling do 3B for instável, usar **ReAct** (`create_react_agent`) com parsing de texto. LangGraph pode dar mais controle.

### 2.2 RAG — Protocolos clínicos

| Item | Decisão |
|---|---|
| Fonte | 39 PDFs já extraídos em `fontes_saude_mulher_v2.json` |
| Chunking | Já feito (1392 chunks de ~1500 tokens) — reusar a função `chunk_text` do notebook anterior |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (rápido) ou `intfloat/multilingual-e5-base` (melhor qualidade PT) |
| Vector store | **Chroma** (persistente no Drive, simples) |
| Retriever | top-k=4 com filtro opcional por `category` |
| Citação | Cada chunk guarda `doc_id`, `category`, `page` (se possível extrair) — agente cita na resposta |

### 2.3 Bases estruturadas (mock SQLite)

**Por que mock:** o enunciado pede integração com prontuário, exames preventivos, registros de violência, base de medicamentos. Em projeto acadêmico, vamos gerar dados sintéticos realistas com Faker + lógica clínica.

**Schema** (`/MyDrive/AssistenteHospitalar/files/hospital.db`):

```sql
-- 1. Pacientes
CREATE TABLE pacientes (
    paciente_id INTEGER PRIMARY KEY,
    nome TEXT,              -- nome fictício
    data_nascimento DATE,
    cpf_hash TEXT,          -- hash, não CPF real
    convenio TEXT,
    cadastro_em DATE
);

-- 2. Prontuário ginecológico/obstétrico
CREATE TABLE prontuario_gineco (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    menarca_idade INTEGER,
    g_p_a TEXT,             -- gestações/partos/abortos: ex "G2P1A0"
    dum DATE,               -- data última menstruação
    metodo_contraceptivo TEXT,
    historico_familiar TEXT,
    observacoes TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);

-- 3. Exames preventivos
CREATE TABLE exames (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    tipo TEXT,              -- 'papanicolau', 'mamografia', 'usg_mamaria', etc.
    data_realizacao DATE,
    resultado TEXT,         -- enum + texto livre
    proximo_recomendado DATE,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);

-- 4. Registros de violência (acesso auditado)
CREATE TABLE registros_violencia (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    tipo TEXT,              -- 'fisica', 'psicologica', 'sexual', 'patrimonial'
    data_atendimento DATE,
    notificado_sinan BOOLEAN,
    encaminhamentos TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);

-- 5. Log de acesso (LGPD) — TODA query em registros_violencia deve logar aqui
CREATE TABLE log_acesso (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    usuario TEXT,           -- mock: identificador do profissional
    tabela TEXT,
    paciente_id INTEGER,
    motivo TEXT
);

-- 6. Medicamentos (referência)
CREATE TABLE medicamentos (
    id INTEGER PRIMARY KEY,
    nome_principio_ativo TEXT,
    nome_comercial TEXT,
    indicacoes TEXT,
    contraindicacoes TEXT,
    categoria_gestacao TEXT,    -- A, B, C, D, X (FDA)
    categoria_lactacao TEXT
);

-- 7. Calendário menstrual (derivado de DUM + histórico)
CREATE TABLE ciclos_menstruais (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    data_inicio DATE,
    duracao_dias INTEGER,
    sintomas TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(paciente_id)
);
```

**Volume sintético:** ~50 pacientes, cobrindo todos os cenários do enunciado (atrasos de exame, históricos de violência, gestantes, climatério, etc.).

### 2.4 Tools (contratos)

| Tool | Assinatura | Descrição |
|---|---|---|
| `buscar_protocolo` | `(query: str, categoria: Optional[str]) -> List[Citacao]` | RAG nos PDFs. Retorna trechos + metadados. |
| `consultar_prontuario` | `(paciente_id: int) -> Prontuario` | Dados base + ginecológicos. |
| `historico_exames` | `(paciente_id: int, tipo: Optional[str]) -> List[Exame]` | Exames preventivos. |
| `exames_atrasados` | `(paciente_id: int) -> List[ExameAtrasado]` | Lógica de thresholds (papanicolau a cada 3 anos 25-64, mamografia bienal 50-69, etc.). |
| `consultar_medicamento` | `(nome_ou_indicacao: str) -> List[Medicamento]` | Lookup na tabela de meds. |
| `calendario_menstrual` | `(paciente_id: int) -> CalendarioMenstrual` | DUM + ciclos + previsão próxima menstruação. |
| `registrar_violencia` | `(paciente_id, tipo, encaminhamentos) -> Confirmacao` | Inclui notificação SINAN. Loga acesso. |
| `consultar_violencia` | `(paciente_id, motivo: str) -> List[Registro]` | **Loga acesso obrigatoriamente.** Motivo é registrado. |

### 2.5 UI (Gradio)

- `ChatInterface` com sistema de mensagens
- Dropdown lateral para selecionar `paciente_id` em contexto (ou "sem paciente" para perguntas gerais)
- Painel lateral com alertas pré-calculados (exames atrasados, sinais suspeitos)
- Botão "ver protocolo citado" expande a fonte
- Acesso via `gr.Interface().launch(share=True)` no Colab

---

## 3. Fluxos especializados

### 3.1 Triagem por sintomas

**Input:** profissional digita "Paciente 32 anos, sangramento intenso há 3 ciclos, dor pélvica."

**Fluxo:**
1. LLM extrai sintomas estruturados (`bind_tools` → `tool: extrair_sintomas`)
2. Tool `buscar_protocolo` consulta RAG com os sintomas
3. LLM compara com diagnósticos diferenciais do protocolo
4. Resposta: hipóteses + exames sugeridos + critérios de urgência, **citando o protocolo**

### 3.2 Alerta de exames preventivos em atraso

**Trigger:** quando `paciente_id` é selecionado no UI ou citado na pergunta.

**Lógica determinística (não LLM):**
- Papanicolau: mulheres 25–64a, intervalo trienal após 2 resultados anuais negativos
- Mamografia: 50–69a bienal (ou 40–49a se alto risco familiar)
- USG transvaginal: a critério clínico, sem rastreio populacional

Implementação: SQL + lógica em Python no `exames_atrasados`. LLM apenas formata a saída e contextualiza.

### 3.3 Identificação de padrões suspeitos de violência

**Sinais (do protocolo):**
- Lesões em locais não-expostos / múltiplas fases de cicatrização
- Retardo na busca por atendimento
- Discordância entre história e exame físico
- Acompanhante controlador
- Histórico de abortos não-explicados
- Sintomas psicossomáticos crônicos sem causa orgânica

**Fluxo:**
1. Profissional descreve o caso ou seleciona campos checklist
2. Tool `avaliar_padrao_violencia` aplica matriz de pontuação derivada dos protocolos
3. Se score ≥ threshold: assistente sugere abordagem (escuta qualificada, perguntas-chave do protocolo), notificação SINAN, encaminhamentos da rede
4. **Toda consulta a registros_violencia é logada** com motivo

### 3.4 Encaminhamento multidisciplinar

LLM identifica especialidades necessárias com base no protocolo (psicologia, assistência social, mastologia, psiquiatria, urologia ginecológica, etc.) e devolve uma lista estruturada de encaminhamentos com prioridade.

### 3.5 Orientações pós-consulta personalizadas

Dado um diagnóstico/conduta + perfil da paciente (idade, escolaridade inferida, comorbidades), o LLM gera um "resumo para a paciente" em linguagem acessível — **separado** da resposta técnica para o profissional. É um output secundário, opcional.

---

## 4. Privacidade e segurança (LGPD)

| Requisito | Implementação |
|---|---|
| Dados sensíveis (violência, saúde mental) | Tabela separada, acesso auditado |
| Log de acesso | Tabela `log_acesso` com timestamp, usuário, motivo |
| Mock de CPF | Hash SHA-256, nunca CPF real |
| Identificação do profissional | Mock simples (`usuario` hardcoded ou env var) — em produção seria OAuth/SSO |
| Não-vazamento entre pacientes | Tools sempre recebem `paciente_id` explícito; sem busca por nome livre |
| Documentação do tratamento | Este doc + README declaram que dados são sintéticos |

---

## 5. Plano de implementação

| # | Etapa | Saída | Estimativa |
|---|---|---|---|
| 1 | Gerar dados mock (Faker + lógica clínica) | `hospital.db` com 50 pacientes | 1 notebook, ~2h |
| 2 | Indexar protocolos no Chroma | Vector store persistido no Drive | 1 notebook, ~30 min |
| 3 | Implementar tools (8 funções) + testes unitários | módulo `tools.py` | ~3h |
| 4 | Wrapper LangChain do LLM fine-tuned | função `get_llm()` | ~1h |
| 5 | Agente com tool calling + prompt system | módulo `agent.py` | ~2h |
| 6 | Lógica de alertas determinística (exames, violência) | módulo `alertas.py` | ~2h |
| 7 | UI Gradio | notebook `app.ipynb` | ~2h |
| 8 | Testes de cenário (triagem, alerta, violência) | notebook `cenarios.ipynb` | ~3h |
| 9 | Documentação final + vídeo demo | README + script | ~2h |

**Total estimado:** ~18h de trabalho efetivo.

**Dependência crítica:** etapa 4 depende do fine-tuning estar concluído. Etapas 1–3, 6 podem ser feitas **em paralelo** com o run do dataset full (~6-8h) e o treino QLoRA (~2-4h).

---

## 6. Decisões em aberto

1. **Modelo durante desenvolvimento**: usar Llama 3.2 3B base ou esperar fine-tuned? Recomendação: **base agora**, troca depois (etapa 4 vira "trocar adapter").
2. **Embeddings**: MiniLM (rápido, 384d) vs e5-base (melhor PT, 768d)? Recomendação: começar com **MiniLM**, fazer benchmark de retrieval; trocar se recall < 70%.
3. **Volume de dados mock**: 50 pacientes é suficiente? Recomendação: sim para demo, cobrindo todos os cenários — não é benchmark, é storytelling.
4. **Persistência do Chroma**: no Drive (lento mas persiste) ou regenerar a cada sessão (rápido mas perde estado)? Recomendação: **no Drive**, indexar uma vez.
5. **Identificador do profissional**: hardcoded ou input no UI? Recomendação: input simples no Gradio, salvar em variável global da sessão.

---

## 7. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Tool calling do 3B instável | Fallback para ReAct; LangGraph para fluxo explícito |
| RAG retorna chunks irrelevantes | Hybrid search (BM25 + densa); rerankers leves se necessário |
| LLM "alucina" condutas não previstas no protocolo | System prompt forte exigindo citação; teste com 20 perguntas de validação clínica |
| Demora do tunnel Gradio no Colab | Já mapeado em memória — rodar direto no navegador Colab, não via VSCode tunnel para sessões longas |
| Dados mock pouco realistas | Validar com 1-2 cenários do enunciado antes de gerar em volume |
