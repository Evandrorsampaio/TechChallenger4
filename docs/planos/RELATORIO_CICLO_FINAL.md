# Relatório do ciclo de implementação (seção 12)

**Agente:** `EvolutionOrchestratorAgent`  
**Branch:** `feat/evolucao-ml-risco-gestacional`  
**Data:** 2026-09-18

## O que foi entregue

Evolução aditiva da Fase 3: dataset sintético v1 (8000, seed 42), quatro modelos, workflow `risco_ml`, 6ª aba Gradio, auditoria `predicoes_ml`, FakeChatModel no Docker `demo-cpu`.

## Sprints

| Sprint | Plano | Encerramento |
|---|---|---|
| 1 | PI-S01 | Documentos + T-03 = 128 (Hub); pesos locais ausentes |
| 2 | PI-S02 | Dataset + config + testes de vazamento + `perfil_v1.json` |
| 3 | PI-S03 | 4 model_cards + métricas + limiar na validação |
| 4 | PI-S04 | `explain.py` (SHAP se houver; senão coef/permutação) |
| 5 | PI-S05 | `risco_ml` + predicoes_ml + FakeChatModel |
| 6 | PI-S06 | Aba ML + `run_demo.py` + `artifacts/demo/` |
| 7 | PI-S07 | pytest, Docker log, CI, pip-audit documentado |
| 8 | PI-S08 | Números a partir de JSON; T-71 higiene |

## O que não é verdade

Dados sintéticos. Sem validação clínica. SHAP não instalado neste host. `pip-audit` listou vulnerabilidades sem bump de pins. Chroma/Llama de produção não vão na imagem CPU.

## Evidência âncora

- Manifesto: `artifacts/data/risco_gestacional_v1.manifest.json`
- Métricas: `artifacts/metrics/comparacao.json`
- Docker: `docs/deploy/EXECUCAO_DOCKER.md`
- Aceite: `docs/requisitos/CRITERIOS_DE_ACEITE.md`
