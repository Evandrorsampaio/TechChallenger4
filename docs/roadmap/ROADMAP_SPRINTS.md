# Roadmap por Sprint

**Agente responsável:** `EvolutionOrchestratorAgent`
**Correspondência:** 1 sprint = 1 fase do `ROADMAP_EXECUTIVO.md` = 1 plano em `docs/planos/`
**Regra:** uma sprint só fecha com a evidência da definição de pronto, não com esforço.

---

## Visão geral

| Sprint | Plano | Itens | Tarefas | Status |
|---|---|---|---|---|
| 1 Descoberta | [PI-S01](../planos/PI-S01_DESCOBERTA.md) | BL-01…08 | T-01…07 | Encerrada; T-03 = 128 (Hub); pesos locais ausentes |
| 2 Dados | [PI-S02](../planos/PI-S02_DADOS.md) | BL-09…16 | T-08…18 | **Fechada** (dataset + testes) |
| 3 Modelos | [PI-S03](../planos/PI-S03_MODELOS.md) | BL-17…24 | T-19…29 | **Fechada** (4 modelos + métricas) |
| 4 Explicabilidade | [PI-S04](../planos/PI-S04_EXPLICABILIDADE.md) | BL-25…28 | T-30…34 | **Fechada com ressalva** (fallback; SHAP opcional) |
| 5 Integração | [PI-S05](../planos/PI-S05_INTEGRACAO.md) | BL-29…38 | T-35…49 | **Fechada** (risco_ml + auditoria) |
| 6 Interface | [PI-S06](../planos/PI-S06_INTERFACE.md) | BL-39…43 | T-50…54 | **Fechada** (aba 6 + run_demo) |
| 7 Testes e Docker | [PI-S07](../planos/PI-S07_TESTES_DOCKER.md) | BL-44…52 | T-55…64 | **Fechada** — pytest verde; Docker build+run com log em `EXECUCAO_DOCKER.md` |
| 8 Documentação | [PI-S08](../planos/PI-S08_DOCUMENTACAO.md) | BL-53…58 | T-65…71 | **Fechada** (números reais; Docker em `EXECUCAO_DOCKER.md`; T-71) |

---

## Sprint 1 — Descoberta e diagnóstico

**Objetivo.** Inventário fiel ao código; requisitos; arquitetura alvo; problema de ML; planos.

**Critério de saída.** Toda afirmação classificada por origem; ADRs com alternativas; planos de implementação publicados; PC-01 e RAG-incompleto decididos.

**Trabalho.** Leitura de `lib/**` e notebooks; documentos em `docs/`; **zero código de produção**.

**Riscos da sprint.** Inventar arquivo que não existe; tratar SFT como dataset tabular.

**Status.** Encerrada. T-03: `max_seq_length=128` no config oficial; pesos do encoder não carregaram localmente.

---

## Sprint 2 — Dados

**Objetivo.** Configuração por ambiente + dataset sintético reprodutível + pipeline de features.

**Critério de saída.** Hash SHA-256 idêntico em duas gerações; 24 features; `risco_latente` fora de `X`; `pytest tests/unit/` da camada de dados verde.

**Primeira tarefa de código.** T-08 `lib/config.py`.

**Riscos.** RIS-04, RIS-11. Pins quebrados no Python 3.13.

---

## Sprint 3 — Modelos

**Objetivo.** Dummy + regra + LogReg + RF comparados com IC; limiar por recall ≥ 0,90 na validação.

**Critério de saída.** 4 `model_card.json`; `comparacao.json`; `analise_erros.json`; scripts CPU código 0.

**Ponto de decisão.** Se o ML não superar a regra (RIS-03), publicar o empate.

**Riscos.** RIS-03, RIS-10 (skew treino/serviço — um único Pipeline).

---

## Sprint 4 — Explicabilidade

**Objetivo.** Cascata SHAP → linear → permutação, método no payload.

**Critério de saída.** Teste com `shap` ausente passando; exemplos documentais copiados de JSON gerado.

**Riscos.** RIS-07.

---

## Sprint 5 — Integração

**Objetivo.** Workflow `risco_ml` ponta a ponta, auditoria, anti-alucinação, RAG nos modos que predizem.

**Critério de saída.** Integração verde com `FakeChatModel`; bypass de emergência apesar de P baixa; 1 linha de auditoria por invocação.

**Riscos.** RIS-05, RIS-08, RIS-13. T-48 (violência) é paralelo de alto valor.

---

## Sprint 6 — Interface e experiência

**Objetivo.** 6ª aba + `run_demo.py` com 4 cenários.

**Critério de saída.** Regressão das 5 abas; demo código 0; avisos visíveis.

**Riscos.** RIS-14 (banco/índice ausentes — o script regenera).

---

## Sprint 7 — Testes e Docker

**Objetivo.** Evidência. Cobertura ≥ 80 % em `lib/ml/`. Docker **executado**.

**Critério de saída.** Logs literais em `docs/deploy/EXECUCAO_DOCKER.md` e `EXECUCAO_LOCAL.md`.

**Riscos.** RIS-01. T-64 (CI) é Could.

---

## Sprint 8 — Documentação e apresentação

**Objetivo.** Números reais, limitações explícitas, matriz fechada, roteiro de demo.

**Critério de saída.** Cruzamento documento × `artifacts/metrics/`; Fase 3 rotulada `[VAL]`; Docker descrito como `FakeChatModel`.

**Riscos.** RIS-02, RIS-16.

---

## Dependências entre sprints

```
S1 (docs) → S2 (config+dados) → S3 (treino) → S4 (explain)
                                              ↓
                         S5 (workflow) ←──────┘
                              ↓
                         S6 (UI/demo)
                              ↓
                         S7 (evidência Docker)
                              ↓
                         S8 (publicação)
```

S7 formaliza testes que já nascem em S2–S6. Não deixar a suíte inteira para a semana 7.

## Cortes se o prazo apertar (ordem)

Nesta branch **não foram cortados** T-64 nem T-71. T-63 registrou o `pip-audit` sem bump de pins.

1. T-64 CI (`Could`) — feito: `.github/workflows/ci.yml`
2. T-71 higiene ampla (ficar no CHANGELOG)
3. T-17 ponte `hospital.db` (Should)
4. T-45/T-46 flag obstétrico e 10ª tool (Should) — o workflow novo já demonstra a integração
5. T-47 observabilidade (Should)
6. Nunca cortar: T-08, T-13, T-20, T-26, T-32, T-41, T-50, T-60, T-66
