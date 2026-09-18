# Guia da demo (CPU)

```
python scripts/train.py          # se ainda não houver joblib
python scripts/run_demo.py       # 4 JSON em artifacts/demo/
python scripts/app.py            # Gradio :7860, FakeChatModel
```

Docker (evidência 2026-09-18): `docker build -t techchallenger4-demo:cpu .` (699 s, 1,78 GB) e `docker run --rm techchallenger4-demo:cpu` (exit 0, 4 cenários). A imagem **não** carrega Llama. Log: `docs/deploy/EXECUCAO_DOCKER.md`.
