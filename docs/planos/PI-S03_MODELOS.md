# PI-S03 — Plano de implementação: Modelos

**Sprint:** 3  
**Backlog:** BL-17…BL-24  
**Tarefas:** T-19…T-29  
**Agente líder:** `MachineLearningAgent`  
**Dependência:** PI-S02 pronto (dataset + pipeline + testes de vazamento)

## Objetivo

Treinar e comparar quatro modelos no **mesmo split**, escolher limiar por recall na validação, serializar o pipeline vencedor com `model_card.json`. Não usar acurácia como critério.

## Pré-condições

- Manifesto SHA-256 verificado (`scripts/train.py --verificar-dataset` ou equivalente T-14).
- `risco_latente` ausente da matriz.
- `RANDOM_SEED=42` em `lib/config.py`.

## Ordem de execução

```
T-19 baseline_regra (mesma função do futuro modo_degradado)
 → T-20 train.py (Dummy, regra, LogReg, RF + GridSearchCV no treino)
  → T-21 evaluate.py (matriz, precision/recall/F1, ROC/PR-AUC, Brier)
   → T-22 IC bootstrap 1000 no teste
    → T-23 calibração
     → T-24 limiar (menor com recall ≥ 0,90 na validação)
      → T-25 registry + model_card (recusa MAJOR incompatível)
       → T-26 predict.py (payload + modo degradado)
        → T-27 scripts/train.py
         → T-28 scripts/evaluate.py
          → T-29 análise de FP/FN e subgrupos
```

T-19 **antes** de T-20: o baseline precisa existir como função testável, não como afterthought.

## Agentes e skills

`MachineLearningAgent` + `MLOpsAndDeploymentAgent`  
Skills: `baseline_model_training`, `classification_model_training`, `model_comparison`, `metrics_evaluation`, `confusion_matrix_analysis`, `class_imbalance_analysis`, `model_serialization`, `inference_pipeline_generation`.

## Arquivos

### Criar

| Arquivo | Tarefa |
|---|---|
| `lib/ml/baseline.py` | T-19 — disjunção de `CRITERIOS_ALTO_RISCO` (`obstetrico.py:50-66`) sobre features validadas |
| `lib/ml/train.py` | T-20 |
| `lib/ml/evaluate.py` | T-21…T-24, T-29 |
| `lib/ml/registry.py` | T-25 |
| `lib/ml/predict.py` | T-26 |
| `scripts/train.py` | T-27 — `--gerar-dataset`, `--verificar-dataset`, treino |
| `scripts/evaluate.py` | T-28 |
| `scripts/predict.py` | CLI fino |
| `tests/unit/test_baseline_regra.py` | T-19 |
| `tests/unit/test_bootstrap_ic.py` | T-22 |
| `tests/unit/test_limiar_operacional.py` | T-24 — prova que o teste não entrou na escolha |
| `tests/unit/test_registry_compatibilidade.py` | T-25 |
| `tests/unit/test_payload_predicao.py` | T-26 |
| `tests/integration/test_treino_completo.py` | T-20, T-27 |
| `tests/integration/test_metricas_reportadas.py` | T-21, T-28 |
| `tests/regression/test_predicao_estavel.py` | T-26 |

### Não tocar

Workflows, UI, `lib/llm.py`, notebooks. Ainda não integrar o modelo ao LangGraph (isso é Sprint 5).

## Regras

1. Quatro modelos, mesmo hash de split.
2. `GridSearchCV` + `StratifiedKFold(5)` **somente no treino**, métrica `average_precision`.
3. `class_weight='balanced'` em LogReg e RF. Sem SMOTE.
4. Limiar **não** é 0,5. Menor limiar com recall ≥ 0,90 na validação; reportar precisão resultante.
5. Teste usado **uma vez**, no relatório.
6. Acurácia no JSON, fora da regra de escolha.
7. `predict()` devolve `predicao`, `probabilidades` (somam 1 ± 1e-6), `threshold`, `dados_imputados`, versões.
8. Pós-condição: `predicao == 'alto_risco' ⇔ probabilities['alto_risco'] >= threshold`.
9. Modelo ausente → `ModeloIndisponivelError` com caminho esperado (não traceback genérico).
10. Se RF/LogReg não superarem o baseline por regra dentro do IC (RIS-03): **publicar o empate**. Proibido mexer no gerador para “ganhar”.
11. Todo número publicado depois (Sprint 8) precisa existir em `artifacts/metrics/*.json`.

## Mapeamento da regra baseline (T-19)

Traduzir `CRITERIOS_ALTO_RISCO` para features, sem inventar critério novo:

| Critério textual | Feature(s) |
|---|---|
| idade <16 ou >35 | `idade` |
| HAS prévia ou induzida | `has_cronica` ou PAS/PAD em faixa hipertensiva (documentar o corte) |
| DM prévio ou gestacional | `diabetes_previo` ou `glicemia_jejum_mg_dl` (corte documentado) |
| cardiopatia / nefropatia / TEV | flags homônimas |
| cesárea prévia (≥2) | `cesareas_previas >= 2` |
| abortamento de repetição (≥2) | `abortos >= 2` |
| natimorto prévio | `natimorto_previo` |
| gemelaridade | `gemelaridade` |
| IMC ≥35 | `imc_pre_gestacional` |
| tabagismo / álcool / drogas | `tabagismo` (álcool/drogas **não existem** no contrato — documentar a redução) |
| HIV / sífilis / hepatites | `infeccao_sexual_ativa` |
| malformação fetal prévia / isoimunização Rh | **ausentes do contrato** — a regra baseline não as usa; registrar em `MODELOS_AVALIADOS.md` como limitação da ponte |

A função da regra em treino **é a mesma** chamada pelo nó `modo_degradado` na Sprint 5.

## Critérios de aceite

CA-13 (dois modelos + baselines), CA-14 (limiar), CA-15 (comparação com IC), CA-16 (métricas completas), CA-17 (FP/FN).

## Definição de pronto

- [ ] 4 `model_card.json` com os 9 campos
- [ ] `artifacts/metrics/comparacao.json` com ponto e IC
- [ ] `limiar.json` gerado na validação
- [ ] `analise_erros.json` com perfil de FN (prioridade clínica) e FP
- [ ] `scripts/train.py` e `scripts/evaluate.py` código 0 em CPU, sem Drive
- [ ] Testes de payload e estabilidade verdes
- [ ] Nenhum documento de `docs/ml/` preenchido com número digitado à mão (isso é T-66)

## Rollback

Apagar `lib/ml/{baseline,train,evaluate,registry,predict}.py` e `artifacts/models/`. Dataset da Sprint 2 permanece.

## Próximo plano

[PI-S04_EXPLICABILIDADE.md](PI-S04_EXPLICABILIDADE.md) — exige T-26.
