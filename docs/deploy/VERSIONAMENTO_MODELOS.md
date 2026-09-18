# Versionamento de modelos

Cada pasta `artifacts/models/<nome>/` contém `modelo.joblib` (não versionado no git) e `model_card.json` (versionável).

Campos do card: `nome`, `versao`, `dataset_version`, `threshold` (escolhido na **validação**), `hiperparametros`, `metricas_teste`, `semente`, `timestamp`.

Incompatibilidade MAJOR de `dataset_version` levanta `IncompatibilidadeDatasetError` em `lib/ml/registry.py`.
