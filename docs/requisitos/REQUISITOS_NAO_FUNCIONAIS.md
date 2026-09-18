# Requisitos Não Funcionais

**Agente responsável:** `RequirementsAnalystAgent`
**Ciclo:** 1 — Descoberta e diagnóstico
**Faixa de IDs:** `RNF-01` a `RNF-20`

> **Status global: nada foi implementado.** Todos os requisitos deste documento estão em
> `Não iniciado`. Nenhum limiar foi medido.

## Regra de redação adotada

Um requisito não funcional que não pode ser medido é uma intenção, não um requisito. Por isso cada
item abaixo tem **dois campos adicionais** em relação aos requisitos funcionais:

| Campo | O que traz |
|---|---|
| **Métrica e limiar** | O número que define atendido/não atendido. Sem faixa vaga |
| **Método de verificação** | O comando, teste ou script que produz esse número |

Requisitos como "o sistema deve ser modular" ou "deve ser seguro" foram traduzidos em condições
binárias verificáveis por execução. Onde a verificação depende de julgamento (documentação, por
exemplo), o julgamento foi reduzido a uma contagem objetiva.

---

## RNF-01 — Modularidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | A camada de ML deve ser um subpacote isolado (`lib/ml/`) com responsabilidade única por módulo, sem dependência de interface, agente ou LLM. O grafo de importação do pacote deve permanecer acíclico. |
| **Tipo** | Estrutural |
| **Prioridade** | Obrigatório |
| **Justificativa** | O grafo atual é acíclico e estratificado (`docs/02_MAPA_DE_COMPONENTES.md` §2), e a inserção de `lib/ml/` não deve degradá-lo. Já existem sinais de erosão: imports declarados e não usados (LAC-09) e duplicação do wrapper de RAG (LAC-12). |
| **Métrica e limiar** | 0 ciclos de importação em `lib/`; 0 imports de `lib.ui`, `lib.agent` ou `lib.llm` dentro de `lib/ml/`; 0 imports declarados e não utilizados nos módulos novos |
| **Método de verificação** | `tests/unit/test_arquitetura_imports.py` — constrói o grafo com `ast`, detecta ciclos e valida a lista de imports proibidos |
| **Dependências** | — |
| **Critério de aceite** | O teste de arquitetura passa; a duplicação do wrapper de RAG não é replicada dentro de `lib/ml/` |
| **Evidência esperada** | `tests/unit/test_arquitetura_imports.py`; grafo atualizado em `docs/arquitetura/DIAGRAMA_COMPONENTES.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `ArchitectureAgent` |
| **Risco associado** | — |

## RNF-02 — Reprodutibilidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | Geração de dataset, split, treino, escolha de limiar e bootstrap devem ser determinísticos sob `RANDOM_SEED = 42`. Duas execuções na mesma versão de dependências produzem os mesmos artefatos e as mesmas métricas. |
| **Tipo** | Qualidade de processo |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-011 e `DEFINICAO_DO_PROBLEMA.md` §6. Hoje nenhuma dependência é pinada fora do notebook 03 (LAC-15), o que torna qualquer resultado irrepetível por construção. |
| **Métrica e limiar** | SHA-256 do Parquet idêntico entre execuções; diferença máxima de 1e-9 em qualquer métrica reportada; 100 % das dependências com versão pinada em `requirements*.txt` |
| **Método de verificação** | `python scripts/train.py --verificar-dataset` + segunda execução completa de `scripts/train.py` comparando `artifacts/metrics/*.json` |
| **Dependências** | RNF-12, RNF-15 |
| **Critério de aceite** | Duas execuções consecutivas em ambiente limpo produzem hash e métricas idênticos |
| **Evidência esperada** | `artifacts/data/*.manifest.json`; log das duas execuções em `docs/ml/REPRODUTIBILIDADE.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent`, `MachineLearningAgent` |
| **Risco associado** | RIS-11 |

## RNF-03 — Rastreabilidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo número publicado em documento deve ter origem identificável num artefato gerado por execução; todo requisito deve ter linha na matriz de rastreabilidade; toda predição deve ter registro de auditoria. |
| **Tipo** | Governança |
| **Prioridade** | Obrigatório |
| **Justificativa** | LAC-24: os números da fase anterior não são verificáveis a partir do repositório. A nova fase não pode repetir isso — e RIS-16 é justamente reimportar esses números sem rótulo. |
| **Métrica e limiar** | 100 % dos RF e RNF presentes na matriz; 100 % das métricas citadas com caminho de artefato; 1 linha de auditoria por execução de workflow (inclusive nas que não predizem) |
| **Método de verificação** | Conferência da matriz (contagem de linhas × contagem de IDs) + `tests/integration/test_auditoria_predicoes.py` |
| **Dependências** | RF-15, RNF-16 |
| **Critério de aceite** | Nenhum ID de requisito fica fora da matriz e nenhuma métrica aparece sem artefato de origem |
| **Evidência esperada** | `docs/requisitos/MATRIZ_DE_RASTREABILIDADE.md`; tabela `predicoes_ml` |
| **Status** | **Não iniciado** |
| **Responsável** | `DocumentationAgent` |
| **Risco associado** | RIS-16 |

## RNF-04 — Testabilidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo componente novo deve ser testável sem GPU, sem rede, sem Google Drive e sem pesos de LLM, por injeção de dependência e uso do dublê determinístico de chat. |
| **Tipo** | Qualidade de processo |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-005. O desacoplamento necessário já existe em parte: `llm.py` não é importado por nenhum módulo de `lib/` e o `chat_model` sempre chega por injeção (`docs/02_MAPA_DE_COMPONENTES.md` §1.6). `[COD]` |
| **Métrica e limiar** | Cobertura de linha ≥ 80 % em `lib/ml/`; suíte completa do perfil `ml-only` em ≤ 5 minutos; 0 testes exigindo GPU, rede ou Drive |
| **Método de verificação** | `pytest --cov=lib/ml --cov-report=term-missing` com rede desabilitada |
| **Dependências** | RF-20 |
| **Critério de aceite** | Cobertura atinge o limiar e a suíte roda num contêiner sem GPU e sem acesso externo |
| **Evidência esperada** | `docs/testes/COBERTURA.md`; saída do `pytest` anexada |
| **Status** | **Não iniciado** |
| **Responsável** | `TestingAndValidationAgent` |
| **Risco associado** | RIS-15 |

## RNF-05 — Segurança

| Campo | Conteúdo |
|---|---|
| **Descrição** | Regra determinística de segurança nunca pode ser rebaixada por inferência probabilística; dependências não podem conter vulnerabilidade crítica conhecida; nenhum caminho novo pode escrever no banco sem passar por função auditada. |
| **Tipo** | Segurança |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-006 e LAC-11 (a UI hoje consulta a existência de registros de violência fora do caminho auditado, `lib/ui.py:63-66`). `[COD]` |
| **Métrica e limiar** | 0 casos em que a predição anula a regra de alarme; 0 vulnerabilidades de severidade crítica em `pip-audit`; 0 `INSERT`/`UPDATE` fora de função com auditoria |
| **Método de verificação** | `tests/integration/test_regra_precede_ml.py`; `pip-audit -r requirements.txt -r requirements-ml.txt`; revisão de `grep` por `INSERT`/`UPDATE` nos módulos novos |
| **Dependências** | RF-04, RF-15 |
| **Critério de aceite** | Os três indicadores em zero |
| **Evidência esperada** | `docs/seguranca/ESTRATEGIA_DE_SEGURANCA.md`; saída do `pip-audit` |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent` |
| **Risco associado** | RIS-12 |

## RNF-06 — Privacidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | A auditoria de predições não pode persistir valores clínicos em claro: apenas `features_hash` (SHA-256) e `top_features` sem o campo `value`. Nenhum dado de pessoa real pode entrar no projeto. |
| **Tipo** | Conformidade (LGPD) |
| **Prioridade** | Obrigatório |
| **Justificativa** | `ARQUITETURA_ALVO.md` §5.3. Gravar os valores clínicos na tabela de auditoria anularia a proteção obtida com o hash — seria duplicar o prontuário numa segunda tabela. |
| **Métrica e limiar** | 0 colunas de valor clínico em `predicoes_ml`; 0 ocorrências de `value` no JSON persistido de `top_features`; 100 % dos dados de origem sintética |
| **Método de verificação** | `tests/unit/test_schema_auditoria.py` (falha se o DDL ganhar coluna de valor); inspeção de dump de exemplo |
| **Dependências** | RF-15 |
| **Critério de aceite** | O teste de schema passa e o dump de exemplo não contém valor clínico legível |
| **Evidência esperada** | `docs/seguranca/LGPD_E_PRIVACIDADE.md`; dump anonimizado de `predicoes_ml` |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent` |
| **Risco associado** | RIS-12 |

## RNF-07 — Observabilidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | Logging estruturado em `lib/observabilidade.py`, com identificador de correlação por execução, nível configurável por ambiente, e evento de início/fim por nó de workflow com duração. Sem `print` nos módulos novos. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | LAC-23: não há `import logging` em `lib/`; o diagnóstico atual é `print` (`lib/llm.py:72, 74`). Sem correlação de execução, um erro em produção não é reconstituível. `[COD]` |
| **Métrica e limiar** | 100 % dos nós de `risco_ml` emitindo evento de início e fim; 0 `print` em `lib/ml/` e `lib/workflows/risco_ml.py`; 1 identificador de correlação por execução |
| **Método de verificação** | `tests/unit/test_observabilidade.py` captura os logs de uma execução e confere a contagem de eventos; `grep -r "print(" lib/ml lib/workflows/risco_ml.py` |
| **Dependências** | RF-12 |
| **Critério de aceite** | Contagem de eventos igual ao número de nós × 2 e nenhum `print` nos módulos novos |
| **Evidência esperada** | `lib/observabilidade.py`; `docs/arquitetura/ESTRATEGIA_DE_OBSERVABILIDADE.md`; log de exemplo |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | — |

## RNF-08 — Versionamento

| Campo | Conteúdo |
|---|---|
| **Descrição** | Contrato de dados, dataset, modelos e payload seguem versionamento semântico explícito. Mudança incompatível exige incremento de MAJOR e registro em `CHANGELOG.md`. |
| **Tipo** | Governança |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §6. Sem MAJOR explícito, uma feature renomeada vira uma predição errada sem aviso. |
| **Métrica e limiar** | 100 % dos artefatos publicados com campo de versão; 1 entrada de `CHANGELOG.md` por mudança de contrato; 0 artefatos com versão implícita ou ausente |
| **Método de verificação** | `tests/unit/test_versoes_declaradas.py` — falha se qualquer `model_card.json` ou manifesto estiver sem versão |
| **Dependências** | RNF-14, RNF-15 |
| **Critério de aceite** | Nenhum artefato sem versão; `CHANGELOG.md` coerente com as versões publicadas |
| **Evidência esperada** | `CHANGELOG.md`; `artifacts/**/model_card.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-10 |

## RNF-09 — Tratamento de erros

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo caminho de exceção previsto deve ser um **nó explícito** do grafo, não um `except` genérico. Nenhuma exceção não tratada pode chegar à interface. |
| **Tipo** | Robustez |
| **Prioridade** | Obrigatório |
| **Justificativa** | LAC-18: os quatro workflows atuais têm zero `try`/`except`, zero nó de fallback e zero retry; uma falha do LLM propaga até o Gradio. `[COD]` |
| **Métrica e limiar** | 4 de 4 caminhos de exceção (`dados_incompletos`, `bypass_ml`, `modo_degradado`, `usar_resposta_estruturada`) cobertos por teste; 0 tracebacks exibidos ao usuário em testes de injeção de falha |
| **Método de verificação** | `tests/integration/test_caminhos_de_erro.py` — injeta falha em cada dependência (modelo, LLM, retriever, banco) e confere que a resposta é estruturada |
| **Dependências** | RF-12, RF-21, RF-22, RF-23 |
| **Critério de aceite** | Os 4 caminhos são alcançados e nenhuma injeção produz traceback na saída |
| **Evidência esperada** | `tests/integration/test_caminhos_de_erro.py`; `docs/arquitetura/FLUXOS_DE_EXECUCAO.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `LangGraphAgent` |
| **Risco associado** | RIS-07 |

## RNF-10 — Documentação

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo módulo e toda função pública nova deve ter docstring que descreva contrato de entrada, saída e efeitos colaterais. A documentação existente não pode divergir do código. |
| **Tipo** | Manutenibilidade |
| **Prioridade** | Obrigatório |
| **Justificativa** | Há precedente de divergência documentação↔código no repositório: `obstetrico.py:1-27` desenha um ramo condicional que `build_obstetrico_workflow` não constrói (LAC-06), e `build_agent` anuncia um `max_iterations` que não usa (LAC-08). `[COD]` |
| **Métrica e limiar** | 100 % das funções públicas de `lib/ml/` com docstring; 0 links quebrados em `docs/`; 0 divergências conhecidas entre diagrama e grafo compilado |
| **Método de verificação** | `tests/unit/test_docstrings_publicas.py` (inspeção via `inspect`); verificação de links em `docs/`; comparação entre o diagrama de `risco_ml` e `graph.get_graph()` |
| **Dependências** | RF-12 |
| **Critério de aceite** | Os três indicadores atingidos |
| **Evidência esperada** | `docs/` atualizada; saída da verificação de links |
| **Status** | **Não iniciado** |
| **Responsável** | `DocumentationAgent` |
| **Risco associado** | — |

## RNF-11 — Execução em ambiente limpo

| Campo | Conteúdo |
|---|---|
| **Descrição** | A partir de um clone limpo, em ambiente virtual novo, sem Colab, sem Drive, sem GPU e sem editar código, deve ser possível instalar, gerar o dataset, treinar, avaliar e obter uma predição. |
| **Tipo** | Operação |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-005 e ADR-009. Hoje nada disso é possível: caminhos do Colab fixos (`lib/db.py:12`, `lib/llm.py:51`), sem `requirements.txt`, sem scripts. `[COD]` LAC-15, LAC-16, LAC-17. |
| **Métrica e limiar** | Sequência documentada termina com código de saída 0; tempo total ≤ 15 minutos em CPU; 0 edições de código-fonte necessárias |
| **Método de verificação** | Execução real em máquina limpa (Windows + Python 3.13 verificados) com log completo anexado |
| **Dependências** | RF-18, RNF-12 |
| **Critério de aceite** | O log anexado mostra a sequência completa bem-sucedida, com tempos |
| **Evidência esperada** | `docs/deploy/EXECUCAO_LOCAL.md` com transcrição da sessão |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-14 |

## RNF-12 — Separação entre configuração e código

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo caminho, credencial, flag de perfil e parâmetro de ambiente deve ser resolvido em `lib/config.py` a partir de variáveis de ambiente, com defaults documentados em `.env.example`. Os defaults atuais do Colab são preservados para não quebrar os notebooks. |
| **Tipo** | Estrutural |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-009. `lib/db.py` já lê `HOSPITAL_DB_PATH`; a mudança generaliza um padrão existente em vez de introduzir um novo. |
| **Métrica e limiar** | 0 caminhos absolutos literais fora de `lib/config.py` nos módulos novos; 100 % das variáveis de ambiente usadas presentes no `.env.example` |
| **Método de verificação** | `tests/unit/test_configuracao_central.py` + varredura por `/content/drive` e por `C:\` nos módulos novos |
| **Dependências** | — |
| **Critério de aceite** | Nenhum caminho literal fora da configuração; `.env.example` completo |
| **Evidência esperada** | `lib/config.py`; `.env.example` |
| **Status** | **Não iniciado** |
| **Responsável** | `ArchitectureAgent` |
| **Risco associado** | — |

## RNF-13 — Ausência de credenciais hardcoded

| Campo | Conteúdo |
|---|---|
| **Descrição** | Nenhum token, chave ou senha pode ser versionado. `HF_TOKEN` e afins vêm exclusivamente do ambiente; o `.env.example` contém apenas nomes e valores de exemplo inequivocamente falsos. |
| **Tipo** | Segurança |
| **Prioridade** | Obrigatório |
| **Justificativa** | Requisito explícito do desafio. Hoje `HF_TOKEN` já vem de `.env` no Drive `[CFG]`, mas não há `.env.example` nem verificação automática (LAC-25). |
| **Métrica e limiar** | 0 ocorrências de padrões de segredo (`hf_[A-Za-z0-9]{20,}`, `sk-`, `AKIA`, `password=`) em qualquer arquivo versionado |
| **Método de verificação** | Varredura por expressão regular no histórico e na árvore de trabalho, executada como teste (`tests/unit/test_sem_segredos.py`) |
| **Dependências** | RNF-12 |
| **Critério de aceite** | Zero ocorrências |
| **Evidência esperada** | Saída da varredura em `docs/seguranca/` |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent` |
| **Risco associado** | — |

## RNF-14 — Versionamento de modelos

| Campo | Conteúdo |
|---|---|
| **Descrição** | Todo modelo salvo deve vir acompanhado de `model_card.json` com nome, versão, `dataset_version`, limiar operacional, hiperparâmetros, métricas de teste, semente e timestamp. O carregamento de modelo com `dataset_version` de MAJOR incompatível deve falhar com erro explícito. |
| **Tipo** | Governança |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §6 e ML-AC-05. Um limiar não versionado junto do modelo é um número perdido: o mesmo artefato passa a classificar diferente. |
| **Métrica e limiar** | 100 % dos modelos com card completo (9 campos); 1 erro explícito ao carregar MAJOR incompatível; 0 modelos carregáveis sem versão |
| **Método de verificação** | `tests/unit/test_registry_compatibilidade.py` |
| **Dependências** | RF-25 |
| **Critério de aceite** | Todos os cards completos e o teste de incompatibilidade passando |
| **Evidência esperada** | `artifacts/models/*/model_card.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `MLOpsAndDeploymentAgent` |
| **Risco associado** | RIS-10 |

## RNF-15 — Versionamento de datasets

| Campo | Conteúdo |
|---|---|
| **Descrição** | O dataset gerado não é versionado no git (binário); o **manifesto** é. O manifesto contém SHA-256, semente, versão do contrato, timestamp, contagem por classe e por split, e versão do gerador. |
| **Tipo** | Governança |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-011. O gerador é determinístico por semente; o dataset é função pura do código versionado, então o manifesto basta — e torna a reprodutibilidade verificável em vez de declarada. |
| **Métrica e limiar** | Manifesto presente no git com 7 campos obrigatórios; `--verificar-dataset` recomputa e confere o hash com resultado idêntico |
| **Método de verificação** | `python scripts/train.py --verificar-dataset` |
| **Dependências** | RF-24 |
| **Critério de aceite** | Hash confere e o manifesto está completo |
| **Evidência esperada** | `artifacts/data/risco_gestacional_v1.manifest.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | RIS-11 |

## RNF-16 — Registro de métricas

| Campo | Conteúdo |
|---|---|
| **Descrição** | Toda métrica reportada deve ser gravada como arquivo estruturado, com identificação do modelo, do split, da versão do dataset e do timestamp da execução. Nenhum número pode ser digitado manualmente em documento. |
| **Tipo** | Governança |
| **Prioridade** | Obrigatório |
| **Justificativa** | ML-AC-07 em `DEFINICAO_DO_PROBLEMA.md` §9. É a contramedida direta ao que ocorreu na fase anterior (LAC-24): números publicados sem artefato de origem. |
| **Métrica e limiar** | 100 % das métricas citadas em `docs/ml/` com chave correspondente em `artifacts/metrics/`; 0 números sem origem |
| **Método de verificação** | Conferência cruzada documento × JSON, registrada em `docs/ml/METRICAS_E_RESULTADOS.md` |
| **Dependências** | RF-09 |
| **Critério de aceite** | Nenhum número publicado sem chave correspondente |
| **Evidência esperada** | `artifacts/metrics/*.json` |
| **Status** | **Não iniciado** |
| **Responsável** | `MachineLearningAgent` |
| **Risco associado** | RIS-16 |

## RNF-17 — Mensagens claras de falha

| Campo | Conteúdo |
|---|---|
| **Descrição** | Toda mensagem de erro voltada ao usuário deve dizer **o que** falhou, **onde** (campo, modelo, arquivo) e **o que fazer**. Mensagens genéricas do tipo "erro interno" são inaceitáveis. |
| **Tipo** | Usabilidade |
| **Prioridade** | Obrigatório |
| **Justificativa** | Decorre de LAC-18: como não há tratamento de erro, a única mensagem possível hoje é o traceback do framework. |
| **Métrica e limiar** | 100 % dos 5 erros de domínio (validação, campo obrigatório ausente, modelo indisponível, LLM divergente, versão incompatível) com mensagem contendo identificação do objeto e ação sugerida; 0 mensagens genéricas |
| **Método de verificação** | `tests/unit/test_mensagens_de_erro.py` — casa o texto de cada erro contra os elementos obrigatórios |
| **Dependências** | RNF-09 |
| **Critério de aceite** | Os 5 erros passam na verificação de conteúdo |
| **Evidência esperada** | `tests/unit/test_mensagens_de_erro.py`; catálogo de mensagens em `docs/arquitetura/CONTRATOS_DE_COMPONENTES.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `LangGraphAgent` |
| **Risco associado** | — |

## RNF-18 — Tratamento de dados incompletos

| Campo | Conteúdo |
|---|---|
| **Descrição** | Campo obrigatório ausente **nunca** é imputado. Campo opcional ausente é imputado pelo `Pipeline` e **declarado** em `dados_imputados`, no payload, na interface e na auditoria. |
| **Tipo** | Correção clínica |
| **Prioridade** | Obrigatório |
| **Justificativa** | `CONTRATO_DE_DADOS.md` §5. A recusa em imputar é deliberada: devolver probabilidade calculada sobre pressão arterial mediana, como se tivesse sido medida, é o tipo de silêncio que o sistema existe para evitar. |
| **Métrica e limiar** | 0 imputações de campo obrigatório; 100 % das imputações de campo opcional declaradas no payload |
| **Método de verificação** | `tests/unit/test_dados_incompletos.py` + inspeção do payload em caso com opcional ausente |
| **Dependências** | RF-03, RF-21 |
| **Critério de aceite** | Nenhuma imputação silenciosa em nenhum caminho |
| **Evidência esperada** | `tests/unit/test_dados_incompletos.py`; payload de exemplo |
| **Status** | **Não iniciado** |
| **Responsável** | `DataEngineeringAgent` |
| **Risco associado** | — |

## RNF-19 — Limites explícitos de uso clínico

| Campo | Conteúdo |
|---|---|
| **Descrição** | Toda saída — payload, interface, relatório técnico, documentação e apresentação — deve declarar que o resultado é apoio à decisão, não diagnóstico, e que o modelo foi treinado em dados **sintéticos**, sem validação clínica. |
| **Tipo** | Ética e conformidade |
| **Prioridade** | Obrigatório |
| **Justificativa** | `DEFINICAO_DO_PROBLEMA.md` §2.1 e §7; ADR-004. É a contramedida ao risco de maior impacto do projeto (RIS-02): apresentar métrica sintética como evidência clínica. |
| **Métrica e limiar** | 100 % dos payloads com `safety_notice` e `aviso_dados_sinteticos` preenchidos, em **todos** os modos; 100 % dos documentos de resultado com a declaração de dados sintéticos |
| **Método de verificação** | `tests/unit/test_avisos_obrigatorios.py` (parametrizado pelos 4 modos) + revisão de checklist documental |
| **Dependências** | RF-14 |
| **Critério de aceite** | Nenhum caminho de saída sem os dois avisos |
| **Evidência esperada** | `docs/ml/LIMITACOES_DO_MODELO.md`; capturas da interface; roteiro de vídeo |
| **Status** | **Não iniciado** |
| **Responsável** | `SecurityAndComplianceAgent`, `DocumentationAgent` |
| **Risco associado** | RIS-02 |

## RNF-20 — Retrocompatibilidade

| Campo | Conteúdo |
|---|---|
| **Descrição** | Após a evolução, os notebooks 05 a 10 devem continuar executando sem alteração, as 5 abas atuais devem manter o comportamento e as 9 ferramentas existentes devem manter assinatura e retorno. |
| **Tipo** | Compatibilidade |
| **Prioridade** | Obrigatório |
| **Justificativa** | ADR-001: a evolução é aditiva. O compromisso é verificado por teste de regressão, não por inspeção visual — que é a diferença entre uma promessa e uma garantia. |
| **Métrica e limiar** | 9 de 9 tools com assinatura e schema inalterados; 4 de 4 workflows existentes com estrutura de grafo inalterada; comportamento do obstétrico idêntico com `ML_RISCO_HABILITADO=false` |
| **Método de verificação** | `tests/regression/test_tools_existentes_intactas.py`; `tests/regression/test_grafos_existentes.py`; `tests/regression/test_obstetrico_flag_desligada.py` |
| **Dependências** | RF-12, RF-26 |
| **Critério de aceite** | Os três testes de regressão passam nos dois estados da flag |
| **Evidência esperada** | `tests/regression/`; relatório em `docs/testes/RELATORIO_DE_TESTES.md` |
| **Status** | **Não iniciado** |
| **Responsável** | `TestingAndValidationAgent`, `ArchitectureAgent` |
| **Risco associado** | RIS-08, RIS-13 |

---

## Consolidação

| Categoria | IDs |
|---|---|
| Estrutura e manutenibilidade | RNF-01, RNF-10, RNF-12, RNF-20 |
| Processo e reprodutibilidade | RNF-02, RNF-04, RNF-11 |
| Governança e rastreabilidade | RNF-03, RNF-08, RNF-14, RNF-15, RNF-16 |
| Segurança, privacidade e ética | RNF-05, RNF-06, RNF-13, RNF-19 |
| Robustez e operação | RNF-07, RNF-09, RNF-17, RNF-18 |

| Prioridade | Quantidade |
|---|---|
| Obrigatório | 20 |
| Desejável | 0 |
| Futuro | 0 |

**Status consolidado: 20 de 20 requisitos em `Não iniciado`.** Nenhum limiar deste documento foi
medido; todos os números citados são **alvos**, não resultados.
