# Planos de Implementação — Índice

**Agente responsável:** `EvolutionOrchestratorAgent`
**Ciclo:** 1 — Descoberta, diagnóstico e planejamento
**Status:** Planos aprovados para execução. **Nenhum código de produção foi alterado neste ciclo.**
**Commit base analisado:** `a8b26cd` (`main`)

## Como usar este conjunto

A implementação **não começa neste ciclo**. Cada plano abaixo é um contrato executável: o próximo ciclo só avança se as pré-condições do plano estiverem satisfeitas e se a evidência da tarefa anterior existir no repositório.

Ordem de leitura:

1. [PLANO_DE_EVOLUCAO_TECNICA.md](PLANO_DE_EVOLUCAO_TECNICA.md) — diagnóstico, viabilidade, arquitetura, problema de ML, riscos e critérios de aceite.
2. [ARQUIVOS_AFETADOS.md](ARQUIVOS_AFETADOS.md) — o que criar, estender e **não tocar**.
3. Planos por sprint, na ordem:

| Plano | Sprint | Primeira tarefa de código | Status |
|---|---|---|---|
| [PI-S01_DESCOBERTA.md](PI-S01_DESCOBERTA.md) | 1 — Descoberta | nenhuma (documentação) | Documentos entregues; 1 pendência `[VAL]` |
| [PI-S02_DADOS.md](PI-S02_DADOS.md) | 2 — Dados | `T-08` `lib/config.py` | **Próximo a executar** |
| [PI-S03_MODELOS.md](PI-S03_MODELOS.md) | 3 — Modelos | `T-19` `lib/ml/baseline.py` | Bloqueado por S2 |
| [PI-S04_EXPLICABILIDADE.md](PI-S04_EXPLICABILIDADE.md) | 4 — Explicabilidade | `T-30` `lib/ml/explain.py` | Bloqueado por S3 |
| [PI-S05_INTEGRACAO.md](PI-S05_INTEGRACAO.md) | 5 — Integração | `T-35` tabela `predicoes_ml` | Bloqueado por S4 |
| [PI-S06_INTERFACE.md](PI-S06_INTERFACE.md) | 6 — Interface | `T-50` 6ª aba Gradio | Bloqueado por S5 |
| [PI-S07_TESTES_DOCKER.md](PI-S07_TESTES_DOCKER.md) | 7 — Testes e Docker | `T-55` suíte pytest | Paralelo parcial com S6 |
| [PI-S08_DOCUMENTACAO.md](PI-S08_DOCUMENTACAO.md) | 8 — Documentação | nenhuma (preenche evidências reais) | Último |

Catálogos de trabalho:

- [docs/AGENTES_AUTONOMOS.md](../AGENTES_AUTONOMOS.md)
- [docs/SKILLS.md](../SKILLS.md)
- [docs/roadmap/ROADMAP_EXECUTIVO.md](../roadmap/ROADMAP_EXECUTIVO.md)
- [docs/roadmap/ROADMAP_TECNICO.md](../roadmap/ROADMAP_TECNICO.md)
- [docs/roadmap/ROADMAP_SPRINTS.md](../roadmap/ROADMAP_SPRINTS.md)
- [docs/roadmap/ROADMAP_RISCOS.md](../roadmap/ROADMAP_RISCOS.md)

## Regra de avanço entre planos

Um plano só muda de `Não iniciado` para `Em execução` quando:

1. o plano anterior está `Pronto` **ou** as dependências explícitas da primeira tarefa estão satisfeitas;
2. os arquivos listados em “Não tocar” continuam intactos;
3. existe pelo menos um teste (ou evidência documental, na Sprint 1) associado à primeira tarefa.

Uma tarefa só muda de `Não iniciado` quando o artefato da linha “Evidência esperada” existe no repositório. Status não é esforço.
