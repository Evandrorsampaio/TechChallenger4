# Arquivos afetados pela evolução

**Agente responsável:** `EvolutionOrchestratorAgent` + `ArchitectureAgent`
**Fonte:** `docs/arquitetura/ARQUITETURA_ALVO.md` §7 · ADR-001
**Regra:** evolução aditiva. Nada do que funciona hoje é removido sem justificativa registrada.

Este documento é o inventário de impacto **antes** da primeira linha de código. Se um arquivo não está aqui, ele não deve ser alterado.

## 1. Não tocar (regressão obrigatória)

Alterar qualquer item desta lista exige ADR nova e teste de regressão específico.

| Caminho | Motivo |
|---|---|
| `01_extrair_protocolos.ipynb` … `10_relatorio_utilizacao.ipynb` | Entrega da Fase 3; notebooks 05–10 devem continuar executáveis |
| `lib/alertas.py` | Regras determinísticas existentes; `SINAIS_ALARME_OBST` é consumido, não reescrito |
| `lib/mock_data.py` | Geração do prontuário sintético (seed 42); schema do banco mock |
| `lib/llm.py` | Loader do Llama + LoRA; defaults Colab preservados via `lib/config.py` |
| `lib/agent.py` | ReAct atual; `max_iterations` só na higiene da Sprint 8 (`T-71`) |
| `lib/workflows/triagem.py` | Grafo existente |
| `lib/workflows/violencia.py` | Exceção: `T-48` devolve as 6 medidas já calculadas (aditivo no `return`) |
| `lib/workflows/prevencao.py` | Exceção: `T-71` unifica `TODAY` (higiene, Sprint 8) |
| `lib/workflows/common.py` | Exceção: `T-43` R-01 filtro nativo **aditivo** |
| `lib/templates/**` | Não referenciados pelo código; fora do escopo da fase |
| `referencias/validador_resposta_llm.py` | Permanece; recebe nota de depreciação. Lógica sobe para `lib/validacao.py` |
| `ROTEIRO_VIDEO.md` (raiz) | Roteiro da Fase 3; o da nova fase vive em `docs/demo/` |
| `ARQUITETURA.md`, `RELATORIO_TECNICO.md`, `RELATORIO_TECNICO_DETALHADO.md` | Atualizados só na Sprint 8, sem apagar a Fase 3 |

## 2. Estender (aditivo, retrocompatível)

| Caminho | O que muda | Tarefa | Risco se errar |
|---|---|---|---|
| `lib/db.py` | `CREATE TABLE IF NOT EXISTS predicoes_ml`; defaults de path passam a ler `lib/config.py` | T-08, T-35, T-36 | Quebra notebooks 05/07/10 se o schema antigo mudar |
| `lib/tools.py` | +1 tool `predizer_risco_gestacional`; `args_schema` em `buscar_protocolo` | T-43, T-46 | Quebra as 9 tools se a assinatura de `build_langchain_tools` mudar |
| `lib/ui.py` | +1 aba ao final; mensagens dos 4 modos | T-50, T-51, T-52 | Quebra as 5 abas se a ordem ou os handlers atuais mudarem |
| `lib/workflows/obstetrico.py` | +1 nó ML **atrás de** `ML_RISCO_HABILITADO` (default `0`) | T-45 | Com flag desligada o grafo compilado deve ser idêntico |
| `lib/workflows/__init__.py` | Exportar `build_risco_ml_workflow` | T-41 | Import circular se `lib/ml` importar workflows |
| `.gitignore` | Permitir `artifacts/data/*.manifest.json` e `artifacts/metrics/*.json`; continuar ignorando pesos e `*.db` | T-14, T-25 | Versionar binário grande ou deixar de versionar manifesto |

## 3. Criar — configuração e operação

| Caminho | Sprint | Tarefa |
|---|---|---|
| `lib/config.py` | 2 | T-08 |
| `.env.example` | 2 | T-09 |
| `requirements.txt` | 2 | T-10 |
| `requirements-ml.txt` | 2 | T-10 |
| `requirements-llm.txt` | 2 | T-10 |
| `pyproject.toml` | 7 | T-55 |
| `Dockerfile` | 7 | T-58 |
| `.dockerignore` | 7 | T-58 |
| `docker-compose.yml` | 7 | T-59 |
| `lib/observabilidade.py` | 5 | T-47 |
| `lib/validacao.py` | 5 | T-37 |
| `lib/llm_fake.py` | 5 | T-44 |

## 4. Criar — camada de ML (`lib/ml/`)

| Caminho | Sprint | Tarefa |
|---|---|---|
| `lib/ml/__init__.py` | 2 | T-11 |
| `lib/ml/schema.py` | 2 | T-11, T-12, T-17 |
| `lib/ml/dataset.py` | 2 | T-13, T-14 |
| `lib/ml/features.py` | 2 | T-15 |
| `lib/ml/baseline.py` | 3 | T-19 |
| `lib/ml/train.py` | 3 | T-20 |
| `lib/ml/evaluate.py` | 3 | T-21…T-24, T-29 |
| `lib/ml/registry.py` | 3 | T-25 |
| `lib/ml/predict.py` | 3 | T-26 |
| `lib/ml/explain.py` | 4 | T-30…T-32 |
| `lib/ml/llm_contract.py` | 5 | T-39, T-40 |

**Invariante de importação:** `lib/ml/` **não** importa `lib.ui`, `lib.agent` nem `lib.llm`. Verificado por `tests/unit/test_arquitetura_imports.py` (T-57).

## 5. Criar — workflow e scripts

| Caminho | Sprint | Tarefa |
|---|---|---|
| `lib/workflows/risco_ml.py` | 5 | T-41, T-42, T-43 |
| `scripts/train.py` | 3 | T-27 |
| `scripts/evaluate.py` | 3 | T-28 |
| `scripts/predict.py` | 3 | T-26 (CLI fino sobre `predict.py`) |
| `scripts/run_demo.py` | 6 | T-53 |

## 6. Criar — testes

Estrutura criada formalmente em T-55; arquivos individuais nascem junto da implementação (regra §11.18).

```
tests/
├── conftest.py
├── unit/
├── integration/
├── e2e/
└── regression/
```

Lista nominativa em cada plano de sprint. Nenhum teste exige GPU, Drive ou rede no perfil `ml-only`.

## 7. Criar — artefatos gerados por execução

Estes **não são escritos à mão**. Só existem depois de rodar os scripts.

| Caminho | Origem | Versionado? |
|---|---|---|
| `artifacts/data/risco_gestacional_v1.parquet` | `scripts/train.py --gerar-dataset` | Não (binário grande; gitignore) |
| `artifacts/data/risco_gestacional_v1.manifest.json` | mesmo comando | **Sim** |
| `artifacts/data/perfil_v1.json` | T-16 | Sim |
| `artifacts/models/**/*.joblib` | `scripts/train.py` | Não (gitignore já cobre `*.bin`; incluir `*.joblib`) |
| `artifacts/models/**/model_card.json` | T-25 | **Sim** |
| `artifacts/metrics/*.json` | `scripts/evaluate.py` | **Sim** |
| `artifacts/explainability/*` | T-30…T-32 | JSON sim; PNG opcional |
| `artifacts/demo/*.json` | `scripts/run_demo.py` | Sim |

## 8. Documentos a preencher com evidência real (não inventar números)

Já existem como especificação. Só recebem números **depois** da execução correspondente.

| Documento | Preenchido em |
|---|---|
| `docs/dados/QUALIDADE_DOS_DADOS.md` | T-16 |
| `docs/ml/METRICAS_E_RESULTADOS.md` | T-66 (após T-28) |
| `docs/ml/COMPARACAO_MODELOS.md` | T-66 |
| `docs/ml/EXPLICABILIDADE.md` | T-33 |
| `docs/ml/INTERPRETACAO_DAS_PREDICOES.md` | T-33 |
| `docs/ml/LIMITACOES_DO_MODELO.md` | T-67 |
| `docs/deploy/EXECUCAO_LOCAL.md` | T-61 |
| `docs/deploy/EXECUCAO_DOCKER.md` | T-60 |
| `docs/testes/RELATORIO_DE_TESTES.md` | T-62 |

## 9. Ordem de criação recomendada (caminho crítico)

```
lib/config.py
  → requirements*.txt
    → lib/ml/schema.py
      → lib/ml/dataset.py
        → lib/ml/features.py
          → lib/ml/baseline.py
            → lib/ml/train.py + evaluate.py
              → lib/ml/registry.py + predict.py
                → lib/ml/explain.py
                  → lib/db.py (+predicoes_ml) + lib/ml/llm_contract.py
                    → lib/workflows/risco_ml.py
                      → lib/ui.py (+aba)
                        → scripts/run_demo.py
                          → Dockerfile
                            → docker build + docker run (log anexado)
```
