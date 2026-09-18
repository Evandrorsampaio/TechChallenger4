# PI-S02 — Plano de implementação: Dados e configuração

**Sprint:** 2  
**Backlog:** BL-09…BL-16  
**Tarefas:** T-08…T-18  
**Agente líder:** `DataEngineeringAgent`  
**Dependência:** PI-S01 pronto (documentos)  
**Esta é a primeira sprint com código.**

## Objetivo

1. O sistema deixa de depender de caminhos Colab espalhados.
2. Existe um dataset tabular sintético, reprodutível, com manifesto SHA-256.
3. Existe um `Pipeline` sklearn de features com `fit` só no treino.

## Pré-condições

- ADR-001, ADR-004, ADR-005 aceitas.
- Contrato v1.0.0 com **24 features** (PC-01 encerrada).
- Nenhum arquivo de `lib/ml/` existe ainda.

## Ordem de execução (obrigatória)

```
T-08 config.py
 → T-09 .env.example
  → T-10 requirements*.txt   (instalar em venv limpo e registrar log)
   → T-11 GestanteFeatures
    → T-12 DadosIncompletosError + validadores cruzados
     → T-13 gerador 8 000 registros
      → T-14 manifesto SHA-256 (duas gerações independentes)
       → T-15 ColumnTransformer no Pipeline
        → T-16 perfilamento (números de execução, não inventados)
         → T-17 features_de_paciente (Should)
          → T-18 testes unitários da camada de dados
```

T-17 pode ser adiado se o prazo apertar (Should). T-08, T-10, T-13, T-15 e T-18 são Must e estão no caminho que alimenta o treino.

## Agentes e skills


| Tarefa     | Agente                                            | Skills                                                                                                                                                     |
| ---------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-08, T-09 | `ArchitectureAgent`, `SecurityAndComplianceAgent` | `environment_configuration`, `dependency_analysis`                                                                                                         |
| T-10       | `MLOpsAndDeploymentAgent`                         | `environment_configuration`, `reproducibility_validation`                                                                                                  |
| T-11…T-17  | `DataEngineeringAgent`                            | `data_contract_generation`, `synthetic_data_generation`, `dataset_profiling`, `data_leakage_detection`, `labeling_strategy`, `train_test_split_validation` |
| T-18       | `TestingAndValidationAgent`                       | `unit_test_generation`, `test_evidence_collection`                                                                                                         |


## Arquivos

### Criar


| Arquivo                                    | Tarefa           | Conteúdo mínimo                                                                                                                                 |
| ------------------------------------------ | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `lib/config.py`                            | T-08             | `HOSPITAL_DB_PATH`, `DRIVE_BASE`, `HF_TOKEN`, `PERFIL_EXECUCAO`, `ML_RISCO_HABILITADO` (default `"0"`), `ARTIFACTS_DIR`, `RANDOM_SEED=42`       |
| `.env.example`                             | T-09             | as mesmas chaves, sem segredo real                                                                                                              |
| `requirements.txt`                         | T-10             | base (pydantic, python-dotenv, …) com `==`                                                                                                      |
| `requirements-ml.txt`                      | T-10             | pandas, numpy, scikit-learn, joblib, pyarrow; `shap` opcional/comentado se quebrar 3.13                                                         |
| `requirements-llm.txt`                     | T-10             | torch, transformers, peft, bitsandbytes, langchain, langgraph, chromadb, sentence-transformers, gradio — **não** instalado no Docker `demo-cpu` |
| `lib/ml/__init__.py`                       | T-11             | exporta schema público                                                                                                                          |
| `lib/ml/schema.py`                         | T-11, T-12, T-17 | `N_FEATURES = 24`, `GestanteFeatures`, `DadosIncompletosError`                                                                                  |
| `lib/ml/dataset.py`                        | T-13, T-14       | `numpy.random.default_rng(42)`, manifesto                                                                                                       |
| `lib/ml/features.py`                       | T-15             | `ColumnTransformer` dentro de `Pipeline`                                                                                                        |
| `tests/unit/test_configuracao_central.py`  | T-08             |                                                                                                                                                 |
| `tests/unit/test_sem_segredos.py`          | T-09             |                                                                                                                                                 |
| `tests/unit/test_schema_gestante.py`       | T-11             | `len(FEATURES) == N_FEATURES == 24`                                                                                                             |
| `tests/unit/test_validacao_entrada.py`     | T-11             |                                                                                                                                                 |
| `tests/unit/test_dados_incompletos.py`     | T-12             |                                                                                                                                                 |
| `tests/unit/test_mensagens_de_erro.py`     | T-12             |                                                                                                                                                 |
| `tests/unit/test_dataset_reprodutivel.py`  | T-13, T-14       |                                                                                                                                                 |
| `tests/unit/test_contrato_dataset.py`      | T-13             |                                                                                                                                                 |
| `tests/unit/test_dataset_sem_vazamento.py` | T-15, T-16       | `risco_latente` ausente da matriz                                                                                                               |
| `tests/unit/test_features_pipeline.py`     | T-15             |                                                                                                                                                 |
| `tests/unit/test_features_de_paciente.py`  | T-17             |                                                                                                                                                 |


### Estender


| Arquivo      | Como                                                            | O que não fazer                  |
| ------------ | --------------------------------------------------------------- | -------------------------------- |
| `lib/db.py`  | Ler path via `lib.config` **preservando** o default Colab atual | Não mudar o DDL das 7 tabelas    |
| `lib/llm.py` | Idem para `DRIVE_BASE`                                          | Não alterar `BitsAndBytesConfig` |
| `.gitignore` | Versionar `*.manifest.json`; ignorar `*.parquet` e `*.joblib`   | Não versionar `hospital.db`      |


### Não tocar

Notebooks, `lib/alertas.py`, `lib/mock_data.py`, `lib/agent.py`, `lib/ui.py`, workflows.

## Regras de implementação

1. **Teste junto do código** (T-08 já nasce com `test_configuracao_central.py`).
2. Defaults Colab **permanecem** para não quebrar notebooks 05–10.
3. Rótulo **não** é `CRITERIOS_ALTO_RISCO`. Seguir `docs/dados/ESTRATEGIA_DE_ROTULAGEM.md` (modelo latente + Bernoulli).
4. Split 70/15/15 estratificado, semente 42, coluna `split` persistida.
5. `risco_latente` nunca entra em `X`.
6. Campos obrigatórios ausentes → `DadosIncompletosError`. **Proibido imputar obrigatório.**
7. Validadores cruzados: `partos + abortos <= gestacoes`; `pad_mmhg < pas_mmhg`.
8. Mensagens de erro citam campo, valor e faixa.
9. Dataset declarado `SINTÉTICO` no manifesto e no aviso.
10. Dois processos distintos devem produzir o mesmo SHA-256 (T-14). Sem essa evidência, T-13 não está pronto.

## 24 features (contrato fechado)

Obrigatórias na inferência (11): `idade`, `imc_pre_gestacional`, `ig_semanas`, `gestacoes`, `partos`, `abortos`, `pas_mmhg`, `pad_mmhg`, `has_cronica`, `diabetes_previo`, `gemelaridade`.

Opcionais (13): `escolaridade_anos`, `cesareas_previas`, `natimorto_previo`, `pre_eclampsia_previa`, `intervalo_interpartal_meses`, `hemoglobina_g_dl`, `glicemia_jejum_mg_dl`, `proteinuria_fita`, `cardiopatia`, `nefropatia`, `tev_previo`, `tabagismo`, `infeccao_sexual_ativa`.

## Critérios de aceite da sprint


| CA           | Como prova                                                                     |
| ------------ | ------------------------------------------------------------------------------ |
| CA-01, CA-02 | schema Pydantic rejeita extra e fora de faixa                                  |
| CA-03, CA-05 | `DadosIncompletosError` lista campos; ponte com `hospital.db` declara ausentes |
| CA-10        | manifesto + hash idêntico em duas gerações                                     |
| CA-11        | `risco_latente` fora de `X`; pipeline com fit só no treino                     |
| CA-12        | 24 features, 8 000 linhas, prevalência 0,22 ± 0,02                             |
| CA-37        | `.env.example` cobre 100 % das variáveis de `config.py`                        |


## Riscos desta sprint


| Risco                       | Mitigação                                                                                           |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| RIS-04 vazamento            | teste dedicado; `risco_latente` removido no loader                                                  |
| RIS-11 RNG numpy            | `default_rng`; pins em `requirements-ml.txt`                                                        |
| Pins quebram no Python 3.13 | T-10 instala em venv limpo **antes** de seguir; se `shap` falhar, fica fora deste arquivo (ADR-008) |


## Definição de pronto

- [x] `lib/config.py` resolve as variáveis; testes de config passam
- [x] Três requirements com `==` em cada linha; log de install limpo anexado (não precisa ser Docker ainda)
- [x] Parquet gerado + manifesto versionado + hash reproduzido
- [x] `Pipeline` serializável
- [x] `pytest tests/unit/` da camada de dados verde, sem GPU/rede/Drive
- [x] `QUALIDADE_DOS_DADOS.md` contém estatísticas **medidas**, ou declara explicitamente que T-16 ficou para o fim da sprint com `perfil_v1.json` como evidência

## Rollback

Remover `lib/config.py` e reverter as duas linhas de path em `db.py`/`llm.py`. Dataset e `lib/ml/` são novos: apagar a pasta não afeta a Fase 3.

## Próximo plano

[PI-S03_MODELOS.md](PI-S03_MODELOS.md) — só começa com T-15 e T-18 verdes.