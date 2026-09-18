# PI-S07 — Plano de implementação: Testes e Docker

**Sprint:** 7  
**Backlog:** BL-44…BL-52  
**Tarefas:** T-55…T-64  
**Agente líder:** `TestingAndValidationAgent` + `MLOpsAndDeploymentAgent`  
**Dependência:** T-18 (unidade de dados) e T-53 (demo). Integração da Sprint 5 deve estar verde.

## Objetivo

Transformar “funciona na máquina do autor” em evidência anexada: suíte pytest, regressão da Fase 3, `docker build` **e** `docker run` com log literal.

## Ordem

```
T-55 estrutura tests/ + conftest.py + pyproject.toml
 → T-56 regressão Fase 3 (9 tools, 4 grafos, flag off, notebooks intactos, predição estável)
  → T-57 testes estruturais (imports, docstrings, segredos, schema auditoria, versões)
   → T-62 relatório + cobertura ≥ 80 % em lib/ml/   (pode rodar já aqui)
    → T-58 Dockerfile + .dockerignore (perfil demo-cpu)
     → T-59 docker-compose.yml
      → T-60 EXECUÇÃO REAL build + run, log em docs/deploy/EXECUCAO_DOCKER.md
       → T-61 EXECUÇÃO REAL local limpa, log em docs/deploy/EXECUCAO_LOCAL.md
        → T-63 pip-audit + varredura de credenciais (Should)
         → T-64 CI GitHub Actions (Could — primeiro a cortar)
```

**T-60 não é T-58.** Escrever o Dockerfile não atende RF-19. Enquanto o log literal não existir, nenhum documento pode afirmar que o Docker funciona (ADR-005, RIS-01).

## Arquivos a criar

- `tests/conftest.py` — fixtures: banco temp, `FakeChatModel`, retriever falso, seed 42
- `pyproject.toml` — pytest + cobertura
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`
- `docs/deploy/EXECUCAO_DOCKER.md`, `EXECUCAO_LOCAL.md`, `CONFIGURACAO_AMBIENTES.md`, `VERSIONAMENTO_MODELOS.md`
- `docs/testes/PLANO_DE_TESTES.md`, `RELATORIO_DE_TESTES.md`, `MATRIZ_DE_COBERTURA.md`
- testes de regressão nominados em T-56 e T-57
- `.github/workflows/ci.yml` somente se T-64 entrar

## Dockerfile (contrato)

- Multi-stage, base `slim`.
- Instala `requirements.txt` + `requirements-ml.txt`. **Nunca** `requirements-llm.txt`.
- `PERFIL_EXECUCAO=demo-cpu`.
- Sem CUDA, sem pesos Llama, sem `HF_TOKEN` obrigatório.
- `.dockerignore` exclui `.git`, notebooks, `files/`, `artifacts/models/*.joblib` se forem grandes demais — os `model_card.json` podem ir copiados ou gerados no entrypoint.
- Compose expõe Gradio, monta `artifacts/`, lê `.env.example`.

Entrypoint sugerido: gerar dataset se manifesto divergir, treinar se modelo ausente (CPU, minutos), `scripts/run_demo.py` ou UI.

## Critérios de cobertura da suíte

| Nível | O que prova |
|---|---|
| unit | schema, vazamento, baseline, payload, validador, explain fallback, config, avisos |
| integration | ordem dos nós, bypass, degradado, RAG indisponível, auditoria, treino |
| e2e | aba, 4 cenários, HIL incompleto |
| regression | 9 tools, 4 grafos, flag 0, UI 5 abas, predição estável, notebook 05–10 ainda importáveis |

Perfil `ml-only`: rede desabilitada, ≤ 5 minutos, 100 % passando, cobertura de linha ≥ 80 % em `lib/ml/`.

## Definição de pronto

- [ ] `pytest` verde documentado em `RELATORIO_DE_TESTES.md`
- [ ] Cobertura anexada (saída de `--cov`, não número chutado)
- [ ] `docs/deploy/EXECUCAO_DOCKER.md` contém log **literal** de `docker build` e `docker run` (data, tamanho da imagem, tempo)
- [ ] `docs/deploy/EXECUCAO_LOCAL.md` contém sessão de clone + venv + treino + predict, ≤ 15 min, zero edição de fonte
- [ ] RF-19 só então pode ser marcado atendido

## Se o build falhar

Não declarar sucesso. Registrar o erro em `EXECUCAO_DOCKER.md` como bloqueio, abrir contingência: reduzir a imagem, gerar o modelo no entrypoint em vez de copiá-lo, ou documentar a falha e o que foi tentado. Mentir sobre Docker é RIS-01.

## Próximo plano

[PI-S08_DOCUMENTACAO.md](PI-S08_DOCUMENTACAO.md) — só publica números que existem em `artifacts/`.
