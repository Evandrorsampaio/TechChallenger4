# Perfil demo-cpu: sklearn + FakeChatModel. Sem CUDA, sem Llama, sem HF_TOKEN.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PERFIL_EXECUCAO=demo-cpu \
    ML_RISCO_HABILITADO=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

COPY lib ./lib
COPY scripts ./scripts
COPY referencias ./referencias
COPY tests/conftest.py ./tests/conftest.py
COPY pyproject.toml .env.example ./
COPY artifacts/metrics ./artifacts/metrics
COPY artifacts/models ./artifacts/models
COPY artifacts/data ./artifacts/data

EXPOSE 7860

CMD ["python", "scripts/run_demo.py"]
