# PI-S06 — Plano de implementação: Interface e demonstração

**Sprint:** 6  
**Backlog:** BL-39…BL-43  
**Tarefas:** T-50…T-54  
**Agente líder:** `DemoAndPresentationAgent`  
**Dependência:** T-41 (`risco_ml.py` invocável)

## Objetivo

O profissional vê a jornada completa na 6ª aba, sem traceback, com probabilidade, limiar, explicação, fontes e os dois avisos. Um comando reproduz os 4 cenários.

## Ordem

```
T-50 aba "Risco Gestacional (ML)" ao final, 11 obrigatórios destacados
 → T-51 render: classificação, P, limiar, top_features, imputados, regras, fontes, avisos, <details> do trace
  → T-52 mensagens dos 4 modos (degradação na primeira seção)
   → T-53 scripts/run_demo.py (banco seed 42 + reindex + 4 cenários)
    → T-54 e2e com FakeChatModel
```

## Arquivos

### Estender

`lib/ui.py` — somente acréscimo de aba e handlers. As 5 abas atuais permanecem na mesma ordem, com os mesmos componentes de entrada.

Ponto de extensão já existente: `build_ui(agent, conn, default_usuario, workflows)` (`ui.py:287-298`). A nova aba entra via `workflows['risco_ml']`. Se a chave faltar, a aba pode existir e devolver a mesma mensagem padrão `'⚠️ Workflow não disponível.'` já usada hoje.

### Criar

- `scripts/run_demo.py`
- `tests/e2e/test_ui_aba_ml.py`
- `tests/e2e/test_fluxo_completo.py`
- `tests/e2e/test_fluxo_dados_incompletos.py`
- `tests/e2e/test_run_demo.py`
- `tests/regression/test_ui_abas_existentes.py`
- `artifacts/demo/*.json` (saída dos 4 cenários)

### Não tocar

Handlers das abas 1–5, sidebar, checkbox SINAN.

## Os 4 cenários (T-53)

| ID | Cenário | Resultado esperado |
|---|---|---|
| D1 | Sucesso (24 features válidas, sem alarme) | `modo=normal`, P + explicação + fontes + avisos |
| D2 | Dados incompletos (faltam obrigatórios) | HIL; lista de campos; sem predição; 1 linha de auditoria `incompleto` |
| D3 | Alto risco / emergência (cefaleia intensa + escotomas + epigastralgia) | `bypass_regra`; encaminhamento imediato |
| D4 | Modelo indisponível | `degradado`; regra baseline; aviso na primeira seção |

`run_demo.py` **regenera** `hospital.db` (seed 42) e reindexa o Chroma local (mitigação RIS-14). Sem Drive.

## Regras de UI

1. Avisos `safety_notice` e `aviso_dados_sinteticos` visíveis em todo modo.
2. Limiar ao lado da probabilidade (senão o número mente).
3. Campos imputados listados nominalmente.
4. Fontes com `doc_id` do trecho que entrou no prompt, não da lista bruta do retriever.
5. Zero traceback ao usuário (CA / RNF-17).

## Critérios

CA-29, CA-33, CA-34.

## Definição de pronto

- [x] 6 abas; as 5 antigas intactas (regressão)
- [x] 4 capturas ou JSON de `artifacts/demo/`
- [x] `python scripts/run_demo.py` código 0 no perfil `demo-cpu`
- [x] e2e sem GPU/rede

## Próximo plano

[PI-S07_TESTES_DOCKER.md](PI-S07_TESTES_DOCKER.md). Parte da suíte já nasceu nas sprints 2–6; esta sprint formaliza evidência e Docker.
