# PI-S08 — Plano de implementação: Documentação e apresentação

**Sprint:** 8  
**Backlog:** BL-53…BL-58  
**Tarefas:** T-65…T-71  
**Agente líder:** `DocumentationAgent`  
**Dependência:** T-28 (métricas JSON), T-60 (log Docker), T-53 (demo)

## Objetivo

Fechar rastreabilidade e comunicar com honestidade o que foi medido, o que é sintético e o que a Fase 3 já fazia. Nenhum número novo é digitado à mão.

## Ordem

```
T-66 METRICAS + COMPARACAO a partir de artifacts/metrics/*.json
 → T-67 LIMITACOES + avisos clínicos (incluindo taxa de descarte do LLM)
  → T-65 README e relatórios técnicos (números da Fase 3 rotulados [VAL])
   → T-68 GUIA_DEMO + LOG_DEMO (declara FakeChatModel no Docker)
    → T-69 roteiro de vídeo e checklist com números reais
     → T-70 matriz de rastreabilidade com status real (inclusive Não atendido, se houver)
      → T-71 CHANGELOG + higiene (TODAY único, imports mortos, max_iterations, RAG duplicado)
```

## Arquivos

### Atualizar

- `README.md`, `RELATORIO_TECNICO.md`, `RELATORIO_TECNICO_DETALHADO.md`
- `docs/ml/METRICAS_E_RESULTADOS.md`, `COMPARACAO_MODELOS.md`, `MODELOS_AVALIADOS.md`, `LIMITACOES_DO_MODELO.md`
- `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md`, `CRITERIOS_DE_ACEITE.md`
- `docs/roadmap/*` status final

### Criar

- `docs/demo/ROTEIRO_DEMO.md`, `CASOS_DE_USO.md`, `ROTEIRO_VIDEO.md`, `CHECKLIST_APRESENTACAO.md`, `GUIA_DEMO.md`, `LOG_DEMO.md`
- `docs/RELATORIO_TECNICO.md` (versão docs/, se distinta da raiz)
- `docs/GUIA_DE_DESENVOLVIMENTO.md`, `docs/GLOSSARIO.md`, `docs/CHANGELOG.md` (ou `CHANGELOG.md` na raiz — T-71)
- `docs/deploy/*` se ainda faltarem textos além dos logs da Sprint 7

### Higiene (T-71) — único toque residual em código antigo

| Arquivo | Mudança | Teste de não regressão |
|---|---|---|
| `lib/alertas.py`, `lib/mock_data.py`, `lib/tools.py`, `lib/workflows/prevencao.py` | `TODAY` de fonte única | grafos e alertas |
| `lib/tools.py`, `lib/workflows/triagem.py` | remover imports mortos | tools intactas |
| `lib/agent.py` | usar ou remover `max_iterations` | ReAct |
| wrapper RAG | unificar `common.rag_search` e `buscar_protocolo` | recuperação |

Nenhuma dessas mudanças pode alterar comportamento observável. Se o risco for alto, T-71 vira diff mínimo ou fica registrado como dívida no CHANGELOG.

## Regras de redação

1. Todo número da nova fase tem chave em `artifacts/metrics/` ou log anexado.
2. Todo número da Fase 3 leva o rótulo “resultado da Fase 3, evidência externa ao repositório” (LAC-24, RIS-16).
3. Frases proibidas: “validado clinicamente”, “diagnóstico”, “Docker funcional” sem apontar o log de T-60.
4. Frases obrigatórias: dados sintéticos; não substitui profissional; não é única fonte de decisão; incerteza existe; crítico vai para humano.
5. Docker: dizer que a imagem `demo-cpu` usa `FakeChatModel`, não o Llama 3.2 3B.

## Definição de pronto da evolução

Os 20 critérios da seção 13 do prompt mestre só podem ser marcados `Atendido` com evidência. Se Docker ou alguma métrica falhar, a matriz registra `Não atendido` — isso é entrega honesta, não falha de documentação.

## Encerramento

`EvolutionOrchestratorAgent` publica o relatório do ciclo final no formato da seção 12 do prompt mestre e atualiza os quatro roadmaps.
