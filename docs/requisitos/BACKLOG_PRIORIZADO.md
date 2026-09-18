# Backlog Priorizado

**Agente responsável:** `RequirementsAnalystAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Faixa de IDs:** `BL-01` a `BL-58`
**Organização:** 8 sprints, priorização MoSCoW, com valor e esforço declarados por item

> **Status global:** itens BL-01…BL-08 estão `Concluído (documento)`. Nenhuma linha de código da
> nova fase foi escrita. Documento não é implementação: RF-05…RF-20 e o Dockerfile permanecem
> abertos. Planos de implementação em `docs/planos/`.

## Escalas usadas

| MoSCoW | Significado nesta entrega |
|---|---|
| **Must** | Sem isto, um requisito obrigatório do desafio fica em aberto |
| **Should** | Eleva materialmente a qualidade ou fecha uma lacuna de severidade alta/média |
| **Could** | Desejável; primeiro a sair do escopo se o prazo apertar |
| **Won't** | Explicitamente fora desta fase; registrado para não ser reaberto |

| Esforço | Referência |
|---|---|
| `PP` | até 2 horas |
| `P` | meio dia |
| `M` | 1 a 2 dias |
| `G` | 3 a 5 dias |
| `GG` | mais de 5 dias |

| Valor | Critério |
|---|---|
| **Alto** | Desbloqueia requisito obrigatório ou fecha lacuna bloqueante |
| **Médio** | Fecha lacuna alta/média ou melhora verificabilidade |
| **Baixo** | Higiene técnica, sem efeito direto em requisito obrigatório |

---

## Sprint 1 — Descoberta e diagnóstico

Objetivo: **saber exatamente o que existe** antes de propor qualquer mudança. Nenhum código de
produção é alterado nesta sprint.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-01 | Inventário do repositório e verificação do ambiente local | Must | Alto | M | — | base para todos | `ProjectDiscoveryAgent` | Concluído (documento) |
| BL-02 | Descrição do estado atual ponta a ponta, com marcadores de origem | Must | Alto | M | BL-01 | base para todos | `ProjectDiscoveryAgent` | Concluído (documento) |
| BL-03 | Mapa de componentes e grafo de dependências de `lib/` | Must | Alto | M | BL-01 | RNF-01 | `ProjectDiscoveryAgent` | Concluído (documento) |
| BL-04 | Análise de lacunas (presente) e riscos (futuro) | Must | Alto | M | BL-02, BL-03 | base para todos | `ProjectDiscoveryAgent` | Concluído (documento) |
| BL-05 | Requisitos funcionais e não funcionais mensuráveis | Must | Alto | G | BL-04 | RF-01…RF-26, RNF-01…RNF-20 | `RequirementsAnalystAgent` | Concluído (documento) |
| BL-06 | Critérios de aceite, matriz de rastreabilidade e backlog | Must | Alto | M | BL-05 | RNF-03 | `RequirementsAnalystAgent` | Concluído (documento) |
| BL-07 | Arquitetura alvo, decisões arquiteturais e contratos de componentes | Must | Alto | G | BL-04 | RNF-01, RNF-12 | `ArchitectureAgent` | Concluído (documento) |
| BL-08 | Definição do problema de ML, contrato de dados e estratégia de rotulagem | Must | Alto | G | BL-04 | RF-05, RF-24 | `MachineLearningAgent`, `DataEngineeringAgent` | Concluído (documento) |

---

## Sprint 2 — Dados

Objetivo: existir um dataset rotulado, reprodutível e validado — e o sistema deixar de depender do
Colab para rodar.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-09 | `lib/config.py` + `.env.example` (configuração por variável de ambiente, defaults Colab preservados) | Must | Alto | M | BL-07 | RF-18, RNF-12, RNF-13 | `ArchitectureAgent` | Não iniciado |
| BL-10 | `requirements.txt`, `requirements-ml.txt`, `requirements-llm.txt` com versões pinadas | Must | Alto | P | BL-09 | RF-18, RNF-02, RNF-11 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-11 | `lib/ml/schema.py` — `GestanteFeatures`, validadores cruzados, `DadosIncompletosError` | Must | Alto | M | BL-08 | RF-01, RF-02, RF-03, RNF-17, RNF-18 | `DataEngineeringAgent` | Não iniciado |
| BL-12 | `lib/ml/dataset.py` — gerador sintético determinístico (8 000 registros, semente 42) + manifesto SHA-256 | Must | Alto | G | BL-08, BL-09 | RF-24, RNF-02, RNF-15 | `DataEngineeringAgent` | Não iniciado |
| BL-13 | `lib/ml/features.py` — `ColumnTransformer` dentro de `Pipeline` (imputação, escalonamento, codificação) | Must | Alto | M | BL-11, BL-12 | RF-05, RNF-18 | `DataEngineeringAgent` | Não iniciado |
| BL-14 | Perfilamento e qualidade dos dados; mapa de vazamentos e controles | Must | Médio | M | BL-12 | RF-24, RNF-18 | `DataEngineeringAgent` | Não iniciado |
| BL-15 | `features_de_paciente` — ponte `hospital.db` → `GestanteFeatures` com declaração de campos ausentes | Should | Médio | P | BL-11 | RF-01, RF-03 | `DataEngineeringAgent` | Não iniciado |
| BL-16 | Testes unitários de dados: reprodutibilidade, ausência de vazamento, aderência ao contrato | Must | Alto | M | BL-12, BL-13 | RF-24, RNF-02, RNF-04 | `TestingAndValidationAgent` | Não iniciado |

**Por que a configuração vem antes dos modelos.** BL-09 e BL-10 não são itens de ML, mas são
pré-requisito de tudo que vem depois: enquanto os caminhos do Colab estiverem fixos no código
(`lib/db.py:12`, `lib/llm.py:51`), nenhum treino roda localmente, nenhum teste roda em CI e o
Docker é impossível. Adiá-los para a sprint de Docker (padrão comum) é o que produz o cenário do
risco RIS-01.

---

## Sprint 3 — Modelos

Objetivo: quatro modelos treinados, comparados com intervalo de confiança e com limiar justificado.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-17 | `lib/ml/train.py` — treino dos 4 modelos com `GridSearchCV` + `StratifiedKFold(5)` sobre o treino | Must | Alto | G | BL-13 | RF-05 | `MachineLearningAgent` | Não iniciado |
| BL-18 | Baseline determinístico por regra, implementando `CRITERIOS_ALTO_RISCO` | Must | Alto | P | BL-13 | RF-05, RF-08 | `MachineLearningAgent` | Não iniciado |
| BL-19 | `lib/ml/evaluate.py` — matriz de confusão, PR-AUC, ROC-AUC, Brier, calibração, IC por bootstrap | Must | Alto | G | BL-17, BL-18 | RF-08, RF-09, RNF-16 | `MachineLearningAgent` | Não iniciado |
| BL-20 | Seleção do limiar operacional por recall ≥ 0,90 na validação, versionado no `model_card` | Must | Alto | P | BL-19 | RF-06 | `MachineLearningAgent` | Não iniciado |
| BL-21 | `lib/ml/registry.py` + `model_card.json` + recusa de MAJOR incompatível | Must | Alto | M | BL-17 | RF-25, RNF-08, RNF-14 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-22 | `lib/ml/predict.py` — inferência a partir do `Pipeline` serializado, com modo degradado | Must | Alto | M | BL-21 | RF-06, RF-07, RF-22 | `MachineLearningAgent` | Não iniciado |
| BL-23 | `scripts/train.py` e `scripts/evaluate.py`, incluindo `--gerar-dataset` e `--verificar-dataset` | Must | Alto | M | BL-17, BL-19 | RF-05, RF-24, RNF-15 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-24 | Análise de erros: perfil dos falsos negativos e falsos positivos, desempenho por subgrupo | Must | Médio | M | BL-19 | RF-09 | `MachineLearningAgent` | Não iniciado |

**Ponto de decisão desta sprint.** Se BL-19 mostrar que os modelos de ML não superam o baseline
determinístico (RIS-03), o resultado será **reportado como está** e discutido em
`docs/ml/LIMITACOES_DO_MODELO.md`. Nenhum item do backlog prevê ajustar o experimento para produzir
superioridade.

---

## Sprint 4 — Explicabilidade

Objetivo: toda predição acompanhada de contribuição por variável, com o método declarado.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-25 | `lib/ml/explain.py` — SHAP `TreeExplainer` com detecção de disponibilidade em import | Must | Alto | G | BL-22 | RF-10 | `ExplainabilityAgent` | Não iniciado |
| BL-26 | Fallback local (contribuição linear) e global (`permutation_importance`), com método registrado no payload | Must | Alto | M | BL-25 | RF-10, RNF-09 | `ExplainabilityAgent` | Não iniciado |
| BL-27 | `EXPLICABILIDADE.md` e `INTERPRETACAO_DAS_PREDICOES.md` com exemplos reais de saída | Must | Médio | M | BL-25, BL-26 | RF-10, RNF-10 | `ExplainabilityAgent` | Não iniciado |
| BL-28 | Testes de explicabilidade, incluindo execução com `shap` ausente | Must | Alto | M | BL-26 | RF-10, RNF-04 | `TestingAndValidationAgent` | Não iniciado |

**Sobre o fallback ser `Must` e não `Should`.** O ambiente local é Python 3.13 e `shap` tem
dependências compiladas (ADR-008, RIS-07). Sem BL-26, a explicabilidade — requisito obrigatório —
fica dependente de um único pacote que pode não instalar.

---

## Sprint 5 — Integração

Objetivo: o modelo deixa de ser um artefato isolado e passa a viver dentro do sistema, com
auditoria, contrato de LLM e caminhos de exceção.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-29 | Tabela `predicoes_ml` (aditiva a `lib/db.py`) + gravação com `features_hash` | Must | Alto | M | BL-22 | RF-15, RNF-03, RNF-06 | `SecurityAndComplianceAgent` | Não iniciado |
| BL-30 | `lib/validacao.py` — promoção do validador determinístico + verificação de coerência numérica | Must | Alto | M | BL-22 | RF-23 | `LLMIntegrationAgent` | Não iniciado |
| BL-31 | `lib/ml/llm_contract.py` — payload somente-leitura, prompt de síntese e campos de aviso | Must | Alto | M | BL-26, BL-30 | RF-13, RF-14, RNF-19 | `LLMIntegrationAgent` | Não iniciado |
| BL-32 | `lib/workflows/risco_ml.py` — workflow completo com arestas condicionais e os 4 caminhos de exceção | Must | Alto | GG | BL-29, BL-31 | RF-12, RF-21, RF-22, RNF-09 | `LangGraphAgent` | Não iniciado |
| BL-33 | Dublê determinístico de chat para o perfil `demo-cpu` | Must | Alto | M | BL-10 | RNF-04, RF-19 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-34 | Nó de ML opcional em `obstetrico.py` sob a flag `ML_RISCO_HABILITADO`, com caminho LLM preservado | Should | Alto | M | BL-32 | RF-12, RNF-20 | `LangGraphAgent` | Não iniciado |
| BL-35 | Décima tool `predizer_risco_gestacional`, com `args_schema` declarado | Should | Médio | P | BL-22 | RF-26 | `LLMIntegrationAgent` | Não iniciado |
| BL-36 | `lib/observabilidade.py` — logging estruturado com correlação por execução | Should | Médio | M | BL-32 | RNF-07 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-37 | Correção de LAC-07: devolver as 6 medidas de segurança do nó `_protocolo_seguranca` | Should | Médio | PP | — | RF-14 | `SecurityAndComplianceAgent` | Não iniciado |
| BL-38 | Testes de integração: regra antes do ML, modo degradado, RAG indisponível, auditoria, caminhos de erro | Must | Alto | G | BL-32 | RF-04, RF-11, RF-15, RNF-09 | `TestingAndValidationAgent` | Não iniciado |

**BL-37 custa duas horas e devolve conteúdo clínico perdido.** É o melhor item de valor por esforço
do backlog inteiro: seis condutas de proteção a vítima de violência que o código já escreve e
descarta (`lib/workflows/violencia.py:107-113`). Está como `Should` apenas porque não é exigido
pelo enunciado da nova fase — não porque seja de baixo valor.

---

## Sprint 6 — Interface e experiência

Objetivo: o resultado do modelo chega ao profissional com incerteza, explicação e limites visíveis.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-39 | Aba "Risco Gestacional (ML)" com formulário das variáveis do contrato | Must | Alto | G | BL-32 | RF-16 | `DemoAndPresentationAgent` | Não iniciado |
| BL-40 | Exibição de probabilidade, limiar, campos imputados, regras disparadas, fontes e os dois avisos | Must | Alto | M | BL-39 | RF-14, RF-16, RNF-19 | `DemoAndPresentationAgent` | Não iniciado |
| BL-41 | Mensagens de interface para os 4 modos, sem traceback ao usuário | Must | Alto | M | BL-39 | RNF-17, RNF-09 | `DemoAndPresentationAgent` | Não iniciado |
| BL-42 | `scripts/run_demo.py` com os 4 cenários de demonstração | Must | Alto | M | BL-32 | RF-17 | `DemoAndPresentationAgent` | Não iniciado |
| BL-43 | Testes ponta a ponta da aba e do script de demonstração | Must | Alto | M | BL-39, BL-42 | RF-16, RF-17, RNF-04 | `TestingAndValidationAgent` | Não iniciado |

---

## Sprint 7 — Testes e Docker

Objetivo: transformar "funciona" em evidência anexada.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-44 | Estrutura `tests/` (unit, integration, e2e, regression) + `conftest.py` + `pyproject.toml` | Must | Alto | M | BL-16 | RF-20, RNF-04 | `TestingAndValidationAgent` | Não iniciado |
| BL-45 | Testes de regressão: 9 tools intactas, grafos existentes, flag desligada, predição estável | Must | Alto | G | BL-34, BL-35 | RNF-20 | `TestingAndValidationAgent` | Não iniciado |
| BL-46 | Testes estruturais: imports/ciclos, docstrings públicas, ausência de segredos, schema de auditoria, versões declaradas | Should | Médio | M | BL-44 | RNF-01, RNF-06, RNF-08, RNF-10, RNF-13 | `TestingAndValidationAgent` | Não iniciado |
| BL-47 | `Dockerfile`, `.dockerignore` e `docker-compose.yml` para o perfil `demo-cpu` | Must | Alto | G | BL-33, BL-42 | RF-19 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-48 | **Execução real** de `docker build` e `docker run`, com log anexado à documentação | Must | Alto | M | BL-47 | RF-19, RNF-11 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-49 | **Execução real** do pipeline em ambiente local limpo, com log anexado | Must | Alto | M | BL-23 | RF-18, RNF-11 | `MLOpsAndDeploymentAgent` | Não iniciado |
| BL-50 | Relatório de testes e cobertura persistidos como evidência | Must | Alto | P | BL-45 | RF-20, RNF-04 | `TestingAndValidationAgent` | Não iniciado |
| BL-51 | `pip-audit` e varredura de credenciais no repositório | Should | Médio | P | BL-44 | RNF-05, RNF-13 | `SecurityAndComplianceAgent` | Não iniciado |
| BL-52 | CI no GitHub Actions executando a suíte do perfil `ml-only` | Could | Médio | M | BL-44 | RNF-04 | `MLOpsAndDeploymentAgent` | Não iniciado |

**BL-48 e BL-49 são itens de backlog, não formalidades.** Existem como itens próprios justamente
porque escrever o `Dockerfile` (BL-47) e executá-lo são coisas diferentes, e é a segunda que o
requisito exige. Enquanto BL-48 não estiver concluído, nenhum documento pode afirmar que o Docker
funciona (ADR-005, RIS-01).

---

## Sprint 8 — Documentação e apresentação

Objetivo: fechar a rastreabilidade e comunicar com honestidade o que foi e o que não foi validado.

| ID | Título | MoSCoW | Valor | Esforço | Dependências | Requisitos atendidos | Agente | Status |
|---|---|---|---|---|---|---|---|---|
| BL-53 | Atualização do `README.md` e do relatório técnico com a nova fase | Must | Alto | G | BL-50 | RNF-10 | `DocumentationAgent` | Não iniciado |
| BL-54 | `METRICAS_E_RESULTADOS.md` e `COMPARACAO_MODELOS.md` preenchidos **exclusivamente** com saída real de execução | Must | Alto | M | BL-19, BL-24 | RF-08, RF-09, RNF-16 | `DocumentationAgent` | Não iniciado |
| BL-55 | `LIMITACOES_DO_MODELO.md` e consolidação dos avisos de uso clínico | Must | Alto | M | BL-54 | RNF-19 | `DocumentationAgent`, `SecurityAndComplianceAgent` | Não iniciado |
| BL-56 | `GUIA_DEMO.md` e roteiro de vídeo, declarando o uso de dublê de LLM no Docker | Must | Alto | M | BL-42, BL-48 | RF-17 | `DemoAndPresentationAgent` | Não iniciado |
| BL-57 | Fechamento da matriz de rastreabilidade com os status reais e as evidências anexadas | Must | Alto | M | todos | RNF-03 | `DocumentationAgent` | Não iniciado |
| BL-58 | `CHANGELOG.md` e higiene técnica (`TODAY` único, imports mortos, `max_iterations`, wrapper de RAG duplicado) | Should | Baixo | M | BL-09 | RNF-01, RNF-08 | `ArchitectureAgent` | Não iniciado |

---

## Priorização consolidada

### Distribuição MoSCoW

| Prioridade | Itens | IDs |
|---|---|---|
| **Must** | 49 | todos os demais |
| **Should** | 8 | BL-15, BL-34, BL-35, BL-36, BL-37, BL-46, BL-51, BL-58 |
| **Could** | 1 | BL-52 |
| **Won't** | — | ver a tabela abaixo |
| **Total** | **58** | BL-01 … BL-58 |

### Fora de escopo declarado (`Won't`)

Registrado para que não seja reaberto como omissão:

| Item | Razão |
|---|---|
| `GradientBoosting` / `XGBoost` como modelos obrigatórios | `DEFINICAO_DO_PROBLEMA.md` §4: só entram se LogReg e RF empatarem dentro do IC |
| Escore probabilístico para detecção de violência | ADR-002: transformar violência doméstica em caixa-preta com dados sintéticos é irresponsável; a matriz determinística permanece |
| Classificação multiclasse de urgência na triagem | ADR-002, alternativa 3 — registrada como extensão futura |
| Alteração do schema de `hospital.db` para acomodar features de ML | `CONTRATO_DE_DADOS.md` §4: quebraria os notebooks 05, 07 e 10 |
| Integração do `ValidadorLLM` (segunda chamada ao modelo) | ADR-010: latência de 5–10 s; permanece disponível e desabilitado por padrão |
| Migração para FastAPI ou reescrita em camadas | ADR-001: evolução aditiva |

### Quadrante valor × esforço (itens de maior alavancagem)

| | Esforço baixo (`PP`–`P`) | Esforço alto (`G`–`GG`) |
|---|---|---|
| **Valor alto** | BL-10 (requirements), BL-18 (baseline por regra), BL-20 (limiar), BL-35 (tool), BL-50 (relatório de testes) | BL-12 (dataset), BL-17 (treino), BL-19 (avaliação), BL-25 (SHAP), BL-32 (workflow), BL-39 (aba), BL-47 (Docker) |
| **Valor médio** | BL-15 (ponte com o banco), BL-37 (medidas de violência), BL-51 (auditoria de dependências) | BL-45 (regressão), BL-53 (documentação) |

`[INF]` Os itens do quadrante superior esquerdo são os que devem ser feitos mesmo sob pressão de
prazo: custam pouco e desbloqueiam muito. BL-18 é o exemplo mais claro — meio dia de trabalho que
transforma toda a avaliação de modelos numa comparação com significado, em vez de um número
isolado.

### Caminho crítico

```
BL-08 → BL-12 → BL-13 → BL-17 → BL-19 → BL-22 → BL-25 → BL-32 → BL-39 → BL-42 → BL-47 → BL-48
```

Doze itens em sequência estrita. Qualquer atraso neles desloca a entrega inteira; os demais têm
folga. `BL-09` e `BL-10` não estão no caminho crítico, mas **bloqueiam** BL-12, BL-33 e BL-47 —
são pré-requisitos silenciosos que costumam ser subestimados.

### Dependências externas ao backlog

| Dependência | Afeta | Contorno se indisponível |
|---|---|---|
| `HF_TOKEN` com aprovação Meta para o Llama 3.2 3B | Perfil `full-gpu`, demonstração com LLM real | Perfis `ml-only` e `demo-cpu` com dublê determinístico (BL-33) |
| Google Drive do autor (adapter LoRA, `hospital.db`, índice Chroma) | Reprodução dos resultados da Fase 3 | Regeneração local: banco pela semente 42, índice pelos notebooks 01 e 06 |
| GPU | Fine-tuning e inferência do LLM real | Toda a cadeia de ML é CPU (ADR-005) |

---

## Observação final sobre o status

BL-01…BL-08 mudaram para `Concluído (documento)` porque os artefatos em `docs/` existem. As
linhas BL-09…BL-58 permanecem `Não iniciado` enquanto não existirem `lib/ml/`, `tests/`,
`scripts/`, `Dockerfile`, `requirements.txt` e `artifacts/`. O primeiro item de *código* a mudar
de status é BL-09 (`lib/config.py`), evidência em `docs/planos/PI-S02_DADOS.md`.
