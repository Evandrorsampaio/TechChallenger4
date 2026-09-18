# PI-S01 — Plano de implementação: Descoberta e diagnóstico

**Sprint:** 1  
**Backlog:** BL-01…BL-08  
**Tarefas:** T-01…T-07  
**Código de produção:** não se altera nesta sprint  
**Agente líder:** `ProjectDiscoveryAgent` + `EvolutionOrchestratorAgent`

## Objetivo

Saber exatamente o que existe, o que falta e o que será construído, com origem classificada (`[COD]`/`[CFG]`/`[DOC]`/`[INF]`/`[AUS]`/`[VAL]`), antes de qualquer implementação.

## Pré-condições

- Repositório clonado no commit base `a8b26cd` ou sucessor que ainda não contenha `lib/ml/`.
- Leitura de `lib/**`, notebooks 01–10, `.gitignore`, README e relatórios da Fase 3.

## Agentes e skills

| Agente | Skills |
|---|---|
| `ProjectDiscoveryAgent` | `project_inventory`, `repository_analysis`, `technology_detection`, `gap_analysis` |
| `RequirementsAnalystAgent` | `requirements_extraction`, `acceptance_criteria_generation`, `traceability_matrix`, `backlog_prioritization` |
| `ArchitectureAgent` | `architecture_reverse_engineering`, `architecture_documentation` |
| `DataEngineeringAgent` / `MachineLearningAgent` | `data_contract_generation`, `problem_definition` |
| `EvolutionOrchestratorAgent` | `roadmap_generation`, `risk_analysis` |

## Estado ao encerrar o ciclo 1

| Tarefa | Status | Evidência |
|---|---|---|
| T-05 Inventário, estado, mapa | **Concluído (documento)** | `docs/00_*.md`, `01_*.md`, `02_*.md` |
| T-06 Lacunas, requisitos, matriz | **Concluído (documento)** | `docs/03_*.md`, `docs/requisitos/*` |
| T-07 Arquitetura, ADRs, specs | **Concluído (documento)** | `docs/arquitetura/*`, `docs/ml/DEFINICAO_DO_PROBLEMA.md`, `docs/dados/*`, `docs/llm/*`, `docs/rag/*`, `docs/langgraph/*` |
| T-01 Reconciliar BL-01…BL-08 | **A executar neste ciclo documental** | backlog com status coerente |
| T-02 PC-01 (23 vs 24 features) | **Resolvida: 24 features** | enumeração §3.1–3.4; `N_FEATURES=24` |
| T-04 RAG no caminho `incompleto` | **Resolvida: não passa pelo RAG** | `WORKFLOW_ML.md` §8 prevalece |
| T-03 `max_seq_length` do encoder | **Aberta `[VAL]`** | exige carregar `SentenceTransformer` |

## Sequência restante (sem código)

1. Marcar BL-01…BL-08 como `Concluído (documento)` no backlog.
2. Registrar PC-01 = 24 features nos três documentos (`DEFINICAO`, `CONTRATO`, `DICIONARIO`).
3. Alinhar `ESTRATEGIA_RAG.md` §7 ao caminho `incompleto` sem RAG.
4. Deixar T-03 como primeira verificação da Sprint 5/RAG, **não** como redesign de chunking.
5. Publicar este conjunto de planos e os roadmaps de sprint/risco.

## Arquivos

- **Criados (docs):** inventário, requisitos, arquitetura, dados, ML spec, LLM, RAG, LangGraph, segurança parcial, planos.
- **Não tocar:** qualquer `.py`, `.ipynb`, templates.

## Definição de pronto da sprint

- [x] Inventário com marcadores de origem
- [x] 28 lacunas e 16 riscos
- [x] RF/RNF/CA/matriz/backlog
- [x] ADRs 001–012
- [x] Problema de ML e contrato de dados
- [x] Planos de implementação por sprint
- [ ] T-03 medido por execução (carrega para sprint de RAG; não bloqueia T-08)

## Próximo plano

[PI-S02_DADOS.md](PI-S02_DADOS.md) — primeira linha de código: `lib/config.py`.
