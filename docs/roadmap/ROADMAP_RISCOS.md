# Roadmap de Riscos

**Agente responsável:** `EvolutionOrchestratorAgent` + `SecurityAndComplianceAgent`
**Fonte inicial:** `docs/03_LACUNAS_E_RISCOS.md` Parte II
**Atualização:** após cada sprint, mudar apenas a coluna Status e o indicador observado.

Escala: probabilidade Alta/Média/Baixa · impacto Crítico/Alto/Moderado · nível do risco Alto/Médio/Baixo (combinação).

| Nível | Regra |
|---|---|
| **Alto** | impacto Crítico, ou (probabilidade Alta e impacto Alto) |
| **Médio** | demais combinações com impacto Alto, ou probabilidade Média |
| **Baixo** | impacto Moderado e probabilidade Baixa |

---

## RIS-01 — Afirmar Docker sem executar

| Campo | Conteúdo |
|---|---|
| Descrição | Documento ou README declara “Dockerfile funcional” sem log de `docker build` + `docker run` |
| Nível | **Alto** |
| Probabilidade | Alta |
| Impacto | Crítico (quebra critério de aceite da evolução) |
| Indicadores | Texto de deploy sem anexo de log; imagem não listada em `docker images` |
| Mitigação | T-60 é item próprio; ADR-005; perfil `demo-cpu` sem GPU |
| Contingência | Registrar a falha literalmente; reduzir a imagem; não inventar sucesso |
| Responsável | `MLOpsAndDeploymentAgent` |
| Status | Pendente |

## RIS-02 — Métrica sintética como validação clínica

| Campo | Conteúdo |
|---|---|
| Descrição | Apresentação ou README omite que o dataset é sintético |
| Nível | **Alto** |
| Probabilidade | Alta |
| Impacto | Crítico (afirmação falsa em domínio de saúde) |
| Indicadores | Frase “validado clinicamente”; ausência de `aviso_dados_sinteticos` na UI |
| Mitigação | Campo obrigatório do payload; revisão Sprint 8; testes de avisos |
| Contingência | Retratar publicamente no README e no roteiro |
| Responsável | `MachineLearningAgent`, `DocumentationAgent` |
| Status | Pendente |

## RIS-03 — ML não supera o baseline determinístico

| Campo | Conteúdo |
|---|---|
| Descrição | Recall do RF ≤ recall da regra, IC sobreposto |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto (justificativa do ML enfraquece) |
| Indicadores | `comparacao.json` após T-22 |
| Mitigação | ADR-004 (rótulo não é a regra); comparação honesta |
| Contingência | Publicar empate; discutir em `LIMITACOES_DO_MODELO.md`; não reconfigurar o gerador |
| Responsável | `MachineLearningAgent` |
| Status | Pendente |

## RIS-04 — Vazamento de dados

| Campo | Conteúdo |
|---|---|
| Descrição | Feature função do rótulo (`risco_latente`) ou scaler ajustado no teste |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto |
| Indicadores | Teste ≫ validação; \|ρ\| > 0,95 com o alvo |
| Mitigação | Loader remove `risco_latente`; Pipeline com fit no treino; teste dedicado |
| Contingência | Regenerar dataset; anular métricas publicadas |
| Responsável | `DataEngineeringAgent`, `TestingAndValidationAgent` |
| Status | Pendente |

## RIS-05 — LLM inventa números da predição

| Campo | Conteúdo |
|---|---|
| Descrição | Texto gerado contém numeral ou rótulo ausente do payload |
| Nível | **Alto** |
| Probabilidade | Média |
| Impacto | Crítico |
| Indicadores | Taxa de descarte; casos LLM-01… em `CASOS_DE_TESTE_LLM.md` |
| Mitigação | ADR-007: regex + descarte; resposta estruturada determinística |
| Contingência | Perfil `ml-only` sem LLM; UI mostra só a estrutura |
| Responsável | `LLMIntegrationAgent` |
| Status | Pendente |

## RIS-06 — Taxa de descarte alta demais para a demo

| Campo | Conteúdo |
|---|---|
| Descrição | > ~30 % dos textos do Llama 3B são descartados |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Moderado |
| Indicadores | `artifacts/metrics/taxa_descarte.json` |
| Mitigação | Medir e reportar; estrutura é completa sozinha |
| Contingência | Demo usa `FakeChatModel` (já previsto no Docker) |
| Responsável | `LLMIntegrationAgent`, `DemoAndPresentationAgent` |
| Status | Pendente |

## RIS-07 — `shap` indisponível no Python 3.13

| Campo | Conteúdo |
|---|---|
| Descrição | Pacote não instala ou quebra em runtime |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto (RF-10) |
| Indicadores | Falha de import na T-10 ou T-30 |
| Mitigação | ADR-008 cascata de fallback; teste sem shap |
| Contingência | Entregar só coef_linear / permutação, método declarado |
| Responsável | `ExplainabilityAgent` |
| Status | Pendente |

## RIS-08 — Extensões quebram notebooks 05–10

| Campo | Conteúdo |
|---|---|
| Descrição | Mudança em `db.py`/`tools.py`/`ui.py`/`obstetrico.py` altera a Fase 3 |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto |
| Indicadores | Testes de regressão T-56 vermelhos |
| Mitigação | ADR-001 aditivo; tabela `IF NOT EXISTS`; flag default 0 |
| Contingência | Reverter o diff do arquivo existente; manter só `lib/ml/` |
| Responsável | `ArchitectureAgent`, `TestingAndValidationAgent` |
| Status | Pendente |

## RIS-09 — `HF_TOKEN` / Llama gated indisponível

| Campo | Conteúdo |
|---|---|
| Descrição | 401/403 ao baixar Llama 3.2 3B |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Moderado |
| Indicadores | Falha no perfil `full-gpu` |
| Mitigação | Perfis `ml-only` e `demo-cpu` não dependem do gated |
| Contingência | Demonstração só com dublê, declarada |
| Responsável | `MLOpsAndDeploymentAgent` |
| Status | Pendente |

## RIS-10 — Training/serving skew

| Campo | Conteúdo |
|---|---|
| Descrição | Pré-processamento de treino ≠ inferência |
| Nível | **Médio** |
| Probabilidade | Baixa |
| Impacto | Alto |
| Indicadores | Mesmo payload, P diferente entre `evaluate` e `predict` |
| Mitigação | Um `Pipeline` serializado; teste de estabilidade |
| Contingência | Recarregar o joblib do registry; proibir preprocessor paralelo |
| Responsável | `MachineLearningAgent` |
| Status | Pendente |

## RIS-11 — RNG / versões alteram o hash do dataset

| Campo | Conteúdo |
|---|---|
| Descrição | SHA-256 diverge do manifesto após upgrade de numpy/sklearn |
| Nível | **Médio** |
| Probabilidade | Baixa |
| Impacto | Alto |
| Indicadores | `--verificar-dataset` falha |
| Mitigação | `default_rng`; pins; manifesto versionado |
| Contingência | Regenerar e bump de `dataset_version` (MAJOR se features mudarem) |
| Responsável | `DataEngineeringAgent` |
| Status | Pendente |

## RIS-12 — Auditoria persiste valor clínico em claro

| Campo | Conteúdo |
|---|---|
| Descrição | Coluna nova com feature crua em `predicoes_ml` |
| Nível | **Alto** |
| Probabilidade | Baixa |
| Impacto | Crítico (LGPD) |
| Indicadores | Teste de schema vermelho se coluna clínica aparecer |
| Mitigação | Só `features_hash`; `top_features` sem `value` |
| Contingência | DROP da coluna; aviso na política de auditoria |
| Responsável | `SecurityAndComplianceAgent` |
| Status | Pendente |

## RIS-13 — Flag cria dois caminhos clínicos divergentes

| Campo | Conteúdo |
|---|---|
| Descrição | `obstetrico.py` e `risco_ml.py` classificam o mesmo caso diferente |
| Nível | **Baixo** |
| Probabilidade | Baixa |
| Impacto | Moderado |
| Indicadores | Teste de equivalência T-45 |
| Mitigação | Ambos chamam `lib/ml/predict.py` |
| Contingência | Desligar a flag; demo só no workflow novo |
| Responsável | `LangGraphAgent` |
| Status | Pendente |

## RIS-14 — Banco e Chroma ausentes na avaliação

| Campo | Conteúdo |
|---|---|
| Descrição | Clone limpo sobe sem `hospital.db` nem índice |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto |
| Indicadores | RAG vazio; demo falha |
| Mitigação | `run_demo.py` regenera banco (seed 42) e reindexa |
| Contingência | Modo degradado de RAG (citação vazia declarada) |
| Responsável | `MLOpsAndDeploymentAgent`, `RAGAgent` |
| Status | Pendente |

## RIS-15 — Escopo de 8 sprints estoura

| Campo | Conteúdo |
|---|---|
| Descrição | Docker e testes ficam para o fim sem evidência |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto |
| Indicadores | Sprint 3 com Must de S2 aberto |
| Mitigação | Infra na Sprint 2; cortes documentados em `ROADMAP_SPRINTS.md` |
| Contingência | Cortar Could/Should na ordem publicada; nunca T-60/T-66 |
| Responsável | `EvolutionOrchestratorAgent` |
| Status | Pendente |

## RIS-16 — Reusar números não verificáveis da Fase 3

| Campo | Conteúdo |
|---|---|
| Descrição | 6414 / ROUGE-L etc. aparecem como resultado desta fase |
| Nível | **Médio** |
| Probabilidade | Média |
| Impacto | Alto |
| Indicadores | README novo sem marcador `[VAL]` |
| Mitigação | Rotular “Fase 3, evidência externa”; revisão T-65 |
| Contingência | Errata no CHANGELOG |
| Responsável | `DocumentationAgent` |
| Status | Pendente |

---

## Mapa probabilidade × impacto

| | Moderado | Alto | Crítico |
|---|---|---|---|
| Alta | — | — | RIS-01, RIS-02 |
| Média | RIS-06, RIS-09 | RIS-03, RIS-04, RIS-07, RIS-08, RIS-14, RIS-15, RIS-16 | RIS-05 |
| Baixa | RIS-13 | RIS-10, RIS-11 | RIS-12 |

Nenhuma mitigação de código foi implementada neste ciclo. O controle atual é documental: planos, ADRs e critérios de pronto que exigem evidência.
