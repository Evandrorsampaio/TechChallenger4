# Configuração de ambientes

| Perfil | Env | O que instala | LLM |
|---|---|---|---|
| ml-only | `PERFIL_EXECUCAO=ml-only` | `requirements.txt` + `requirements-ml.txt` | nenhum |
| demo-cpu | `PERFIL_EXECUCAO=demo-cpu` | o mesmo + Gradio/LangGraph pinados no `requirements.txt` | `FakeChatModel` |
| full-gpu | Colab / `requirements-llm.txt` | torch + Llama | modelo da Fase 3 `[VAL]` |

`HOSPITAL_DB_PATH` e `DRIVE_BASE` defaultam para caminhos Colab. Local: apontar `HOSPITAL_DB_PATH` para um `.db` gerado por `lib.mock_data.populate`.

`ML_RISCO_HABILITADO=0` (default): obstétrico idêntico à Fase 3.
