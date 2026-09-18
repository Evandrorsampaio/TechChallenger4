# PI-S04 — Plano de implementação: Explicabilidade

**Sprint:** 4  
**Backlog:** BL-25…BL-28  
**Tarefas:** T-30…T-34  
**Agente líder:** `ExplainabilityAgent`  
**Dependência:** T-26 (`predict.py` devolve payload real)

## Objetivo

Toda predição carrega contribuição por variável. O método usado é declarado. A linguagem é associativa (“as variáveis que mais contribuíram…”), nunca causal.

## Ordem

```
T-30 explain.py + detecção de shap no import + TreeExplainer no RF
 → T-31 fallback local coef × valor padronizado (LogReg)
  → T-32 fallback global permutation_importance + aviso de escopo
   → T-34 testes inclusive com shap ausente (monkeypatch)
    → T-33 docs preenchidos com JSON real de artifacts/explainability/
```

T-33 fica por último de propósito: documentação sem artefato é invenção.

## Cascata (ADR-008)

```
shap disponível e modelo em árvore → shap_tree_explainer (local)
shap ausente e modelo linear     → coef_linear (local)
caso contrário                   → permutacao (global) + aviso obrigatório
falha total                      → top_features=[] + aviso; nunca levanta exceção
```

## Arquivos

### Criar

- `lib/ml/explain.py`
- `tests/unit/test_explicabilidade.py`
- `tests/unit/test_explicabilidade_fallback.py`
- `artifacts/explainability/shap_exemplo.json` (gerado)
- `artifacts/explainability/importancia_global.json` (gerado)

### Preencher (não inventar)

- `docs/ml/EXPLICABILIDADE.md`
- `docs/ml/INTERPRETACAO_DAS_PREDICOES.md`

### Não tocar

Workflows e UI. A explicação ainda não é exibida nesta sprint; só o módulo e os artefatos.

## Contrato de `top_features`

Cada item: `feature`, `value` (no payload da UI/LLM), `contribution`, `direction ∈ {aumenta, reduz}`. Mínimo 3 entradas no caminho feliz.

Na auditoria (Sprint 5) a chave `value` **não** é persistida.

## Regras de linguagem

Permitido: “As variáveis que mais contribuíram para esta classificação foram…”  
Proibido: “Esta variável causou o risco…”

O teste de documentação (revisão T-33) falha se aparecer causalidade indevida.

## Critérios

CA-18 (explicação corresponde à predição), CA-19 (fallback declarado).

## Riscos

RIS-07 (`shap` no Python 3.13): T-34 simula ausência. Se a instalação falhar de verdade, o sistema continua entregando explicação local via coeficientes ou global via permutação.

## Definição de pronto

- [x] Import de `lib.ml.explain` não quebra sem `shap`
- [x] Payload traz `explanation_method` e `explanation_scope`
- [x] Teste com monkeypatch de import passa
- [x] Exemplos nos docs são cópia literal dos JSON gerados

## Próximo plano

[PI-S05_INTEGRACAO.md](PI-S05_INTEGRACAO.md).
