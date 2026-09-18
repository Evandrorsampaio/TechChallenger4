# Execução Docker (evidência)

**Data:** 2026-09-18  
**Host:** Windows 10, Docker Desktop 29.3.1 (`desktop-linux`)  
**Status:** **comprovado neste ciclo.** RF-19 atendido com log literal de `build` e `run`.

A imagem `demo-cpu` usa `FakeChatModel`. **Não** carrega Llama 3.2 3B nem `requirements-llm.txt`.

## Build

```
docker --version
# Docker version 29.3.1, build c2be9cc

# BUILD_START 2026-09-18T12:32:31.0402907-03:00
docker build --progress=plain -t techchallenger4-demo:cpu .
```

Trechos literais do build (engine `desktop-linux`):

```
#0 building with "desktop-linux" instance using docker driver
#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 919B 0.0s done
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#5 [ 1/13] FROM docker.io/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
#9 [ 5/13] RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt
#9 DONE 421.2s
#18 exporting to image
#18 exporting manifest sha256:47ef19f50b73a36f5c97f2566dc62891504693a82ac728184c403e8575fe9b73
#18 naming to docker.io/library/techchallenger4-demo:cpu done
#18 DONE 76.5s

BUILD_EXIT 0
BUILD_ELAPSED_SEC 699
IMAGE techchallenger4-demo:cpu 3dd7f0b4e3d1 1.78GB 2026-09-18 12:42:52 -0300
```

## Run

```
# RUN_START 2026-09-18T12:44:30.6898799-03:00
docker run --rm techchallenger4-demo:cpu
```

Saída (CMD = `python scripts/run_demo.py`):

```
D1_sucesso normal alto_risco
D2_incompleto incompleto incompleto
D3_emergencia bypass_regra alto_risco
D4_degradado degradado alto_risco
auditoria_linhas 4
RUN_EXIT 0
RUN_ELAPSED_SEC 12
```

UI Gradio (`docker compose up`) não foi o comando desta evidência; o contrato de T-60 é build + run com log. O `run` exercitou os quatro modos do workflow na imagem.
