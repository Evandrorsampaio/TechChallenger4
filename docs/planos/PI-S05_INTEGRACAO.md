# PI-S05 — Plano de implementação: Integração ML + LangGraph + LLM + RAG + auditoria

**Sprint:** 5  
**Backlog:** BL-29…BL-38  
**Tarefas:** T-35…T-49  
**Agente líder:** `LangGraphAgent`  
**Dependência:** T-26 e T-32 (inferência + explicabilidade)

## Objetivo

O modelo deixa de ser artefato isolado. Surge `lib/workflows/risco_ml.py` com 16 nós, 4 arestas condicionais, 4 caminhos de exceção, contrato de LLM somente-leitura e uma linha de auditoria por invocação.

## Ordem (caminho crítico da sprint)

```
T-35 DDL predicoes_ml (aditivo)
 → T-36 gravação com features_hash
  → T-37 lib/validacao.py (promove ValidadorDeterministico)
   → T-38 coerência numérica pós-geração
    → T-39 llm_contract.py (13 chaves, avisos constantes)
     → T-40 prompt + resposta_estruturada determinística
      → T-44 FakeChatModel          (pode paralelizar após T-10)
       → T-41 16 nós de risco_ml.py
        → T-42 rotas condicionais
         → T-43 RAG no fluxo (não no caminho incompleto)
          → T-47 observabilidade (Should)
           → T-49 testes de integração
            → T-45 nó opcional em obstetrico.py (Should, flag default 0)
             → T-46 10ª tool (Should)
              → T-48 LAC-07 medidas de violência (Should, independente)
```

T-44 pode começar cedo: só depende de T-10. T-48 não depende de ML — pode ser feito em paralelo no dia 1 da sprint.

## Agentes

`SecurityAndComplianceAgent` (T-35, T-36, T-48) · `LLMIntegrationAgent` (T-37…T-40, T-46) · `LangGraphAgent` (T-41, T-42, T-45) · `RAGAgent` (T-43, T-03 se ainda aberto) · `MLOpsAndDeploymentAgent` (T-44, T-47) · `TestingAndValidationAgent` (T-49)

## Arquivos

### Criar

| Arquivo | Tarefa |
|---|---|
| `lib/validacao.py` | T-37, T-38 |
| `lib/ml/llm_contract.py` | T-39, T-40 |
| `lib/workflows/risco_ml.py` | T-41…T-43 |
| `lib/llm_fake.py` | T-44 |
| `lib/observabilidade.py` | T-47 |
| testes em `tests/integration/` e `tests/unit/` listados em T-37…T-49 | |

### Estender

| Arquivo | Mudança aditiva |
|---|---|
| `lib/db.py` | `CREATE TABLE IF NOT EXISTS predicoes_ml` — 7 tabelas intactas |
| `lib/tools.py` | +1 tool; `args_schema` em `buscar_protocolo` |
| `lib/workflows/obstetrico.py` | nó ML atrás de `ML_RISCO_HABILITADO` |
| `lib/workflows/common.py` | R-01 filtro nativo com detecção de suporte |
| `lib/workflows/violencia.py` | `return` inclui `medidas` (T-48) |
| `referencias/validador_resposta_llm.py` | nota de depreciação; arquivo permanece |

### Não tocar

`lib/alertas.py`, `lib/mock_data.py`, `lib/llm.py` (o dublê é arquivo novo), `triagem.py`, `prevencao.py`, notebooks.

## Invariantes do workflow (testáveis)

1. `regras_seguranca` executa **antes** de `executar_modelo_ml` em todo caminho que prediz.
2. Emergência (`SINAIS_ALARME_OBST`) → `bypass_ml`, mesmo se um dublê de modelo devolver P=0,05.
3. Campo obrigatório ausente → HIL; **não** imputar; **não** chamar RAG (decisão RAG-incompleto).
4. Modelo indisponível → `modo_degradado` usando **a mesma** função de `lib/ml/baseline.py`.
5. LLM não calcula números; verificação regex; divergência descarta o texto.
6. `safety_notice` e `aviso_dados_sinteticos` presentes nos 4 modos.
7. Exatamente 1 INSERT em `predicoes_ml` por invocação que chega a `compilar_resposta`, inclusive incompleto (`probabilidade NULL`).
8. `features_hash` = SHA-256 canônico; `top_features` persistido **sem** `value`.
9. `build_risco_ml_workflow(chat_model, conn, retriever)` — mesma assinatura dos 4 workflows atuais.
10. Com `ML_RISCO_HABILITADO=0`, grafo de `obstetrico.py` idêntico ao atual.

## Os 16 nós (referência)

`validar_dados`, `erro_validacao`, `dados_incompletos`, `solicitar_complemento`, `regras_seguranca`, `bypass_ml`, `executar_modelo_ml`, `modo_degradado`, `gerar_explicabilidade`, `recuperar_protocolos_rag`, `sintetizar_com_llm`, `validar_resposta_llm`, `usar_resposta_estruturada`, `aplicar_avisos_seguranca`, `auditar`, `compilar_resposta`.

Rotas puras: `_rota_validacao`, `_rota_regras`, `_rota_modelo`, `_rota_validacao_llm`. Testáveis com dicionário literal, sem LLM.

## T-03 (max_seq_length) nesta sprint

Se ainda aberto: carregar `SentenceTransformer(EMB_MODEL)` uma vez, registrar o inteiro em `docs/00_INVENTARIO_PROJETO.md` e `docs/rag/ESTRATEGIA_RAG.md`. **Não reindexar.** Hipótese conservadora atual: 128. Divergência 128 vs 512 é documentação, não redesign.

## Critérios

CA-08 regra antes do ML · CA-09 bypass · CA-20/21 RAG · CA-22…24 caminhos de erro · CA-25…28 contrato LLM e avisos · CA-30…32 auditoria.

## Definição de pronto

- [x] `pytest tests/integration/` verde com `FakeChatModel`, sem GPU
- [x] Caso cefaleia + escotomas + epigastralgia → `bypass_regra` apesar de P=0,05
- [x] 4 modos gravam 1 linha cada
- [x] Flag desligada: obstétrico inalterado (teste de regressão, mesmo que T-45 seja Should)
- [x] T-48: 6 medidas visíveis se o item for incluído

## Rollback

Remover `risco_ml.py` e a tabela nova (`IF NOT EXISTS` não altera as 7 antigas). Reverter o `return` de `violencia.py` se T-48 tiver sido feito. Flag default 0 isola o obstétrico.

## Próximo plano

[PI-S06_INTERFACE.md](PI-S06_INTERFACE.md).
