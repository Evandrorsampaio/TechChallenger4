# Plano de Evolução Técnica

**Agente orquestrador:** `EvolutionOrchestratorAgent`
**Ciclo:** 1 — Inspecionar → Planejar → Documentar
**Data:** 2026-09-18
**Escopo deste ciclo:** diagnóstico, requisitos, arquitetura, agentes, skills, roadmaps e planos de implementação.
**Código de produção alterado:** nenhum.

> Este é o entregável obrigatório da primeira execução. A implementação começa no ciclo seguinte, pelo plano [PI-S02_DADOS.md](PI-S02_DADOS.md), tarefa `T-08`.

---

## 1. Diagnóstico

O sistema atual é um assistente clínico de saúde da mulher, executável como aplicação de notebook no Google Colab: Llama 3.2 3B Instruct com adapter LoRA/QLoRA, RAG em ChromaDB, agente ReAct com 9 ferramentas LangChain, 4 workflows LangGraph e interface Gradio de 5 abas sobre um SQLite de 50 pacientes sintéticas.

Ele **funciona no que se propôs a fazer**. O que falta não é qualidade pontual — é cobertura da nova fase e capacidade de reprodução fora do Colab do autor.

### 1.1 O que está confirmado por código `[COD]`

- 14 módulos Python em `lib/`, 10 notebooks, 6 templates clínicos, 1 validador em `referencias/`.
- LLM: `meta-llama/Llama-3.2-3B-Instruct` em `lib/llm.py`; fine-tuning QLoRA no notebook 03.
- 9 `StructuredTool` em `lib/tools.py`; a 9ª (`buscar_protocolo`) não tem `args_schema`.
- 4 grafos LangGraph: `triagem`, `violencia`, `obstetrico`, `prevencao`.
- Classificação `habitual` / `alto_risco` no obstétrico **é feita pelo LLM** (`obstetrico.py:124-144`), com `default='habitual'` em falha de parse — falso negativo silencioso.
- Regras determinísticas em `lib/alertas.py` (`SINAIS_EMERGENCIA`, `SINAIS_ALARME_OBST`, `SINAIS_VIOLENCIA`).
- Único gate humano formal: checkbox `confirmacao_clinica` na aba de violência.
- Auditoria atual (`log_acesso`) cobre só acesso a violência, não decisões clínicas.
- Caminhos Colab fixos: `lib/db.py:12`, `lib/llm.py:51`.
- Zero `try/except` nos 4 workflows.

### 1.2 O que está ausente `[AUS]`

| Ausência | Impacto |
|---|---|
| ML supervisionado (`sklearn`, modelos, métricas, SHAP) | Bloqueia RF-05…RF-10 |
| Dataset tabular rotulado | Bloqueia treino; SFT JSONL **não** serve |
| `requirements.txt`, `Dockerfile`, `tests/`, `scripts/`, `lib/config.py` | Bloqueia reprodução local e Docker |
| Versionamento de modelo/dataset/métricas | Bloqueia RF-25, RNF-14…16 |

### 1.3 Números da Fase 3

Contagens do `README.md` (6414 pares, 5134 SFT, 1392 chunks, ROUGE-L etc.) são `[DOC]` / `[VAL]`: artefatos gitignored, outputs de notebook limpos. **Não serão reutilizados como métrica da nova fase.**

### 1.4 Inventário de lacunas

28 lacunas em `docs/03_LACUNAS_E_RISCOS.md`: 8 bloqueantes, 6 altas, 7 médias, 7 baixas. Nenhuma correção de código foi feita.

---

## 2. Viabilidade

**Viável por evolução aditiva (ADR-001).** Não é necessário reescrever o sistema.

| Questão | Resposta | Origem |
|---|---|---|
| Há ponto de extensão para um workflow novo? | Sim. `build_ui(..., workflows=)` já aceita dicionário | `[COD]` `lib/ui.py:287-298` |
| Há ponto de extensão para uma tool nova? | Sim. `build_langchain_tools` devolve lista | `[COD]` `lib/tools.py:242` |
| Há problema de ML justificado pelo código? | Sim. `_avaliar_risco_gestacional` delega classificação estruturada ao LLM | `[COD]` `obstetrico.py:124-144` |
| Há dataset tabular? | Não. Será sintético, declarado como tal | `[AUS]` / ADR-004 |
| Docker com Llama 3B é validável nesta máquina? | Não com GPU. Perfil `demo-cpu` + `FakeChatModel` torna o build executável | ADR-005 |
| O LLM pode ser mantido? | Sim, como síntese somente-leitura dos números do ML | ADR-007 |

**Condição de viabilidade ética:** métricas em dado sintético **não** são validação clínica. Isso é invariante de produto, não nota de rodapé.

---

## 3. Maior desafio

Há dois desafios, de naturezas diferentes.

### 3.1 Desafio técnico: circularidade do rótulo

Se o dataset sintético for rotulado pela mesma regra `CRITERIOS_ALTO_RISCO` que o baseline determinístico implementa, o Random Forest recupera a disjunção com F1 ≈ 1,00 e o ML não se justifica. A ADR-004 resolve isso com escore latente logístico + interações + amostragem de Bernoulli (erro de Bayes irredutível).

### 3.2 Desafio de afirmação (maior risco de entrega)

Declarar “Docker funcional” sem `docker build` + `docker run` (RIS-01) e apresentar métrica sintética como evidência clínica (RIS-02). Nenhum dos dois exige tecnologia nova; ambos exigem disciplina. Por isso T-60 e T-61 existem como itens de backlog próprios, e `aviso_dados_sinteticos` é campo obrigatório do payload.

O maior desafio **operacional** é o caminho crítico de 11 tarefas em sequência:

```
T-13 → T-15 → T-20 → T-21 → T-26 → T-30 → T-41 → T-50 → T-53 → T-58 → T-60
```

Atraso em qualquer uma desloca a entrega. `T-08` e `T-10` (configuração e pins) não estão no caminho crítico, mas bloqueiam dataset, dublê de LLM e Docker.

---

## 4. Arquitetura atual (resumo)

```
Gradio (5 abas)
  ├─ ReAct + 9 tools → SQLite + Chroma
  └─ 4 StateGraphs LangGraph
        ├─ regras determinísticas (alertas)
        ├─ RAG (chunk 6000 / overlap 400)
        └─ Llama 3.2 3B + LoRA  →  decisão + texto
```

Limites atuais:

- Decisão estruturada e redação estão no mesmo LLM.
- Sem camada de configuração, teste, erro, observabilidade ou empacotamento.
- Execução estruturalmente acoplada a Colab + Drive + GPU.

Detalhe em `docs/arquitetura/ARQUITETURA_ATUAL.md` e `docs/01_ESTADO_ATUAL.md`.

---

## 5. Arquitetura alvo (resumo)

```
Dados clínicos estruturados
        ↓
Validação Pydantic (GestanteFeatures)
        ↓
Regras determinísticas de alarme obstétrico   ← podem anular o ML
        ↓
Modelo supervisionado (LogReg + Random Forest + 2 baselines)
        ↓
Explicabilidade (SHAP → linear → permutação)
        ↓
RAG de protocolos (filtro ginecologia_obstetricia)
        ↓
LLM para síntese somente-leitura dos números
        ↓
Verificação anti-alucinação (descarte do texto se divergir)
        ↓
Avisos + auditoria predicoes_ml + Gradio (6ª aba)
```

Doze camadas, contratos por estrutura de dados, três perfis (`ml-only`, `demo-cpu`, `full-gpu`). Detalhe em `docs/arquitetura/ARQUITETURA_ALVO.md`. ADRs 001–012 em `DECISOES_ARQUITETURAIS.md`.

**O que a evolução explicitamente não faz:** validação clínica; escore de violência; multiclasse de urgência; alteração do schema de `hospital.db`; reescrita FastAPI; rechunking do RAG (maior impacto, mas invalida a Fase 3).

---

## 6. Problema de ML recomendado

> Dado um conjunto de variáveis clínicas estruturadas de uma gestante no pré-natal, estimar P(alto risco) e classificar sob limiar operacional escolhido por recall ≥ 0,90 na validação.

| Atributo | Valor |
|---|---|
| Tarefa | Classificação binária `habitual` / `alto_risco` |
| Justificativa | Substitui decisão que hoje o LLM toma mal | 
| Features | **24** (enumeração de `CONTRATO_DE_DADOS.md` §3.1–3.4). Pendência PC-01 encerrada neste ciclo |
| Alvo | `alto_risco` ∈ {0,1}, prevalência-alvo ≈ 0,22 |
| Dados | Sintéticos, 8 000 registros, semente 42, rótulo **não** derivado da regra MS/FEBRASGO |
| Modelos | Dummy(prior) · baseline por regra · LogisticRegression · RandomForestClassifier |
| Métrica primária | Recall da classe positiva; PR-AUC de ranqueamento. Acurácia reportada, nunca decisória |
| Limiar | Menor valor com recall ≥ 0,90 na **validação**; teste usado uma vez |

Não é diagnóstico, não prediz desfecho materno/fetal, não substitui obstetra, não foi validado em população real.

---

## 7. Agentes e skills

15 agentes catalogados em `docs/AGENTES_AUTONOMOS.md`. Skills reutilizáveis em `docs/SKILLS.md`.

| Papel | Agente |
|---|---|
| Coordenação | `EvolutionOrchestratorAgent` |
| Diagnóstico | `ProjectDiscoveryAgent` |
| Requisitos | `RequirementsAnalystAgent` |
| Arquitetura | `ArchitectureAgent` |
| Dados | `DataEngineeringAgent` |
| Modelos | `MachineLearningAgent` |
| Explicabilidade | `ExplainabilityAgent` |
| LLM | `LLMIntegrationAgent` |
| RAG | `RAGAgent` |
| Workflow | `LangGraphAgent` |
| Segurança | `SecurityAndComplianceAgent` |
| Testes | `TestingAndValidationAgent` |
| Deploy | `MLOpsAndDeploymentAgent` |
| Docs | `DocumentationAgent` |
| Demo | `DemoAndPresentationAgent` |

---

## 8. Roadmap

8 sprints = 8 fases. 58 itens de backlog (BL-01…BL-58). 71 tarefas técnicas (T-01…T-71).

| Sprint | Entrega que desbloqueia a seguinte |
|---|---|
| 1 Descoberta | Este plano e a documentação normativa |
| 2 Dados | Dataset reprodutível + `lib/config.py` + pins |
| 3 Modelos | 4 modelos comparados com IC e limiar versionado |
| 4 Explicabilidade | Contribuição por variável com método declarado |
| 5 Integração | `risco_ml.py` + auditoria + contrato de LLM |
| 6 Interface | 6ª aba + `run_demo.py` com 4 cenários |
| 7 Testes e Docker | Suíte verde + **log real** de build/run |
| 8 Documentação | Números reais publicados, limitações explícitas |

Documentos: `ROADMAP_EXECUTIVO.md`, `ROADMAP_TECNICO.md`, `ROADMAP_SPRINTS.md`, `ROADMAP_RISCOS.md`.

---

## 9. Requisitos (cobertura)

- 26 funcionais (RF-01…RF-26) · 20 não funcionais (RNF-01…RNF-20)
- 40 critérios de aceite + 20 critérios da evolução
- Matriz de rastreabilidade em `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md`
- Backlog MoSCoW em `docs/requisitos/BACKLOG_PRIORIZADO.md`

Placar atual da evolução: **0 de 20 critérios atendidos**. Documento não conta como implementação.

---

## 10. Riscos (os que param a entrega)

| ID | Risco | Mitigação no plano |
|---|---|---|
| RIS-01 | Afirmar Docker sem executar | T-60 é item próprio; nenhum texto pode dizer “funciona” antes do log |
| RIS-02 | Métrica sintética como validação clínica | Campo obrigatório `aviso_dados_sinteticos`; revisão de linguagem na Sprint 8 |
| RIS-03 | ML não superar o baseline | Reportar como está; não reconfigurar o gerador |
| RIS-05 | LLM inventar números | Verificação regex + descarte do texto |
| RIS-07 | `shap` falhar no Python 3.13 | Cascata de fallback (ADR-008) |
| RIS-15 | Escopo estourar | Must de infra antecipado na Sprint 2; CI é o único Could |

Mapa completo em `docs/roadmap/ROADMAP_RISCOS.md`.

---

## 11. Decisões de planejamento tomadas neste ciclo

Estas decisões desbloqueiam implementação. Não são código.

| ID | Decisão | Efeito |
|---|---|---|
| PC-01 | **24 features**, não 23. Fonte: enumeração §3.1–3.4 do contrato | `DEFINICAO_DO_PROBLEMA.md` alinhada; `N_FEATURES = 24` no schema |
| RAG-incompleto | Caminho `incompleto` **não** chama RAG | `ESTRATEGIA_RAG.md` §7 alinhada a `WORKFLOW_ML.md` §8 |
| max_seq_length | Permanece `[VAL]` até T-03 executar o encoder. Hipótese conservadora: 128 tokens. **Sem rechunking nesta fase** | T-03 fica como verificação, não como redesign |

---

## 12. Critérios de aceite da evolução (placar)

| # | Critério | Status agora |
|---|---|---|
| 1 | Problema de ML definido | Especificado; não treinado |
| 2 | Dataset documentado | Contrato existe; dataset **não gerado** |
| 3 | Dataset validado | Pendente T-14/T-16 |
| 4–6 | ≥2 modelos, comparação, métricas | Pendente Sprint 3 |
| 7 | FP/FN analisados | Pendente T-29 |
| 8 | Explicabilidade implementada | Pendente Sprint 4 |
| 9–12 | Predição + RAG + LLM + anti-invenção | Pendente Sprint 5 |
| 13 | Interface com jornada completa | Pendente Sprint 6 |
| 14 | Testes principais executados | Pendente Sprint 7 |
| 15 | Dockerfile funciona (com log) | Pendente T-60 |
| 16–18 | README, arquitetura, rastreabilidade | Arquitetura/requisitos escritos; README da fase pendente |
| 19 | Roadmap atualizado | Este ciclo |
| 20 | Limitações explícitas + demo preparada | Spec pronta; evidência pendente |

---

## 13. Próxima ação recomendada

**Não implementar o workflow nem treinar modelos ainda.**

1. Abrir [PI-S02_DADOS.md](PI-S02_DADOS.md).
2. Agente: `ArchitectureAgent`.
3. Tarefa: **T-08** — criar `lib/config.py` com defaults Colab preservados e `ML_RISCO_HABILITADO=0`.
4. Pré-condições: ADRs aceitas (estão); este plano lido; arquivos em “Não tocar” identificados.
5. Critério de conclusão: nenhum caminho absoluto literal nos módulos **novos**; testes `tests/unit/test_configuracao_central.py` passando.
6. Em seguida, no mesmo sprint: T-09 (`.env.example`) e T-10 (`requirements*.txt` pinados). Só então T-11…T-18 (schema e dataset).

Intervenção humana só é necessária se: (a) `shap` não instalar e o fallback precisar ser aceito formalmente; (b) o ML empata com o baseline (RIS-03); (c) `docker build` falhar por limite da máquina.

---

## 14. Relatório do ciclo 1 (formato obrigatório)

### Resumo

- **Objetivo:** ler o repositório, diagnosticar, planejar a evolução, criar agentes/skills/roadmaps/planos. Não implementar código.
- **Agentes acionados:** `EvolutionOrchestratorAgent`, `ProjectDiscoveryAgent`, `RequirementsAnalystAgent`, `ArchitectureAgent`, `DataEngineeringAgent`, `MachineLearningAgent`, `ExplainabilityAgent`, `LLMIntegrationAgent`, `RAGAgent`, `LangGraphAgent`, `SecurityAndComplianceAgent`, `DocumentationAgent`.
- **Skills utilizadas:** `project_inventory`, `gap_analysis`, `requirements_extraction`, `architecture_documentation`, `roadmap_generation`, `risk_analysis`, `data_contract_generation`, `problem_definition`.
- **Arquivos analisados:** árvore versionada (`lib/**`, 10 notebooks, docs da Fase 3, `.gitignore`).
- **Arquivos criados neste ciclo de planos:** `docs/planos/*`, `docs/roadmap/ROADMAP_SPRINTS.md`, `docs/roadmap/ROADMAP_RISCOS.md`, `docs/AGENTES_AUTONOMOS.md`, `docs/SKILLS.md`, complementos de segurança.
- **Arquivos alterados:** apenas documentação normativa para fechar PC-01, RAG-incompleto e status do backlog da Sprint 1.
- **Arquivos não alterados:** todo código Python, notebooks, templates.

### Diagnóstico

- Situação: Fase 3 completa em Colab; nova fase 0 % implementada.
- Evidências: busca zero por sklearn/SHAP; schema SQLite sem alvo; caminhos Colab literais.
- Premissas: dataset sintético é aceitável se declarado; CPU basta para a cadeia de ML.
- Lacunas: LAC-01…LAC-03 (tríade ML) + LAC-13…LAC-17 (infra).
- Riscos: RIS-01 e RIS-02 (afirmação), RIS-03 (circularidade evitada pela ADR-004).

### Implementação

Nenhuma alteração de comportamento. Planos e catálogos criados. Divergências documentais PC-01 e RAG-incompleto resolvidas no papel.

### Validação

- Testes executados: nenhum (não há suíte; ciclo de planejamento).
- Resultado: N/A.
- Pendências: T-03 (`max_seq_length`) exige execução do encoder — permanece `[VAL]`.

### Documentação

- Planos de implementação por sprint.
- Roadmaps de sprints e riscos.
- Catálogo de agentes e skills.
- Decisões PC-01 e RAG-incompleto.

### Próximas ações

- **Próxima tarefa:** T-08 `lib/config.py`
- **Agente:** `ArchitectureAgent`
- **Pré-condições:** este plano aceito; ADR-001 e ADR-005 vigentes
- **Critério de conclusão:** ver [PI-S02_DADOS.md](PI-S02_DADOS.md) § T-08
