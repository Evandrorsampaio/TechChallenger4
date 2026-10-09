# LGPD e Privacidade

**Agente responsável:** `SecurityAndComplianceAgent`
**Base normativa:** Lei nº 13.709/2018 (LGPD)
**Escopo:** enquadramento legal do tratamento de dados neste projeto, controles existentes,
controles ausentes e decisões de privacidade da nova fase de ML.
**Vinculado a:** RNF-06 (privacidade), RNF-13 (sem credenciais), RF-15 (auditoria),
ADR-011, `ARQUITETURA_ALVO.md` §5.3, `POLITICA_DE_AUDITORIA.md`

---

> ## Banner de estado
>
> Nenhum controle da nova fase está implementado: `predicoes_ml` não existe, `lib/ml/` não existe,
> nenhum teste foi escrito. Os controles marcados **`[COD]`** são os que **já existem** no código
> da Fase 3 e foram verificados por leitura direta do fonte. Todo o resto é projeto.
>
> Este documento **não é** uma declaração de conformidade. É um enquadramento: o que se aplica, o
> que já existe, o que falta e o que seria juridicamente exigido se o sistema tratasse dado real.

---

## 1. O fato que condiciona todo o documento

> **Este projeto não trata nenhum dado pessoal.**

Não é uma atenuante, é uma questão de escopo material da lei. O art. 1º da LGPD delimita seu objeto
ao "tratamento de dados pessoais", e o art. 5º, I define dado pessoal como "informação relacionada
a **pessoa natural identificada ou identificável**". Os registros de `hospital.db` são gerados
programaticamente por `Faker('pt_BR')` com semente fixa (`lib/mock_data.py`), a partir de listas de
nomes e de geradores pseudoaleatórios. Não existe pessoa natural a que eles se relacionem.

A consequência técnica é direta e vale registrar com precisão, porque é frequentemente confundida:

| Situação | Enquadramento | Efeito |
|---|---|---|
| **Dado pessoal** | Art. 5º, I — relaciona-se a pessoa identificada ou identificável | LGPD aplica-se integralmente |
| **Dado pessoal sensível** | Art. 5º, II — inclui dado referente a **saúde** e a **vida sexual** | Regime reforçado do art. 11 |
| **Dado anonimizado** | Art. 12 — perdeu a possibilidade de associação, direta ou indireta | Não é dado pessoal, **desde que** a anonimização seja irreversível |
| **Dado sintético** | Não há titular em nenhum momento do ciclo de vida | Fora do escopo material: não há o que anonimizar |

Dado sintético é uma posição **mais forte** que dado anonimizado. A anonimização é sempre uma
afirmação sobre a dificuldade de reverter um vínculo que existiu — e o art. 12, §1º prevê que o
dado volta a ser pessoal se a reversão for possível com esforço razoável. Dado sintético não tem
vínculo a reverter.

### 1.1 A ressalva honesta

Um gerador de nomes pode produzir, por coincidência, o nome de uma pessoa real. Isso **não** cria
um vínculo de titularidade: os atributos clínicos associados àquele nome não se referem a essa
pessoa nem foram coletados dela. A coincidência não torna o registro "informação relacionada" a
ela, no sentido do art. 5º, I. Vale, no entanto, uma consequência prática de bom senso: os nomes
gerados não devem ser exibidos fora do contexto de demonstração como se fossem casos clínicos, e
capturas de tela publicadas em `docs/demo/` devem trazer a legenda de dados sintéticos definida em
`AVISOS_DE_USO_CLINICO.md` §3.3.

O mesmo raciocínio se aplica ao dataset de ML: as 8 000 gestações de
`risco_gestacional_sintetico v1.0.0` são produto de um modelo latente logístico com amostragem de
Bernoulli (ADR-004). Não há coorte de origem — as faixas de valores são clinicamente plausíveis,
mas as **frequências** foram escolhidas por nós e não foram medidas em nenhuma população
(`CONTRATO_DE_DADOS.md` §2).

---

## 2. O que os dados deste sistema seriam, se fossem reais

O enquadramento hipotético importa porque define o padrão de controle que o sistema **deveria**
atender, e é contra esse padrão que a §5 mede a distância.

| Dado no sistema | Onde vive | Classificação hipotética | Artigo |
|---|---|---|---|
| Nome, data de nascimento, CPF | `pacientes` (`db.py:31-38`) | Dado pessoal | Art. 5º, I |
| Convênio | `pacientes` | Dado pessoal | Art. 5º, I |
| Prontuário ginecológico, menarca, G/P/A, DUM, método contraceptivo | `prontuario_gineco` | **Sensível** — saúde e vida sexual | Art. 5º, II |
| Exames preventivos e resultados | `exames` | **Sensível** — saúde | Art. 5º, II |
| Ciclos menstruais e sintomas | `ciclos_menstruais` | **Sensível** — saúde e vida sexual | Art. 5º, II |
| **Registros de violência** | `registros_violencia` | **Sensível** — saúde; e dado cuja divulgação pode causar **dano físico direto** | Art. 5º, II |
| Features de risco gestacional (PA, IMC, hemoglobina, comorbidades) | payload de inferência | **Sensível** — saúde | Art. 5º, II |
| Predição de risco + probabilidade | `predicoes_ml` (projetado) | **Sensível** — é inferência sobre saúde | Art. 5º, II |
| `usuario` da auditoria | `log_acesso`, `predicoes_ml` | Dado pessoal do **profissional**, não da paciente | Art. 5º, I |

Duas linhas merecem destaque.

**`registros_violencia` é a tabela de maior gravidade do sistema** — não por ser mais sensível em
abstrato, mas porque a consequência do vazamento é qualitativamente diferente. Um resultado de
mamografia exposto causa dano à privacidade; um registro de violência doméstica exposto ao agressor
causa dano físico. Isso justifica que seja a única tabela com exigência de justificativa de acesso
no código atual, e justifica que o achado da §4.1 seja tratado como o mais relevante deste
documento.

**A predição do modelo é, ela própria, dado pessoal sensível.** Uma probabilidade de alto risco
gestacional é informação sobre a saúde da titular, ainda que inferida e não medida. Ela não é menos
protegida por ser produto de um modelo; o art. 5º, II não distingue dado coletado de dado inferido.
É por isso que `predicoes_ml` foi projetada com as restrições da §3, e não como uma tabela de log
comum.

---

## 3. Bases legais que se aplicariam em uso real

Nenhuma base legal é invocada neste projeto, porque não há tratamento de dado pessoal. O quadro
abaixo é o que seria necessário sustentar em um cenário assistencial real.

### 3.1 Dados pessoais comuns (art. 7º)

| Base legal | Aplicabilidade | Observação |
|---|---|---|
| Art. 7º, VIII — **tutela da saúde**, em procedimento realizado por profissionais de saúde ou entidade sanitária | **Principal** para o cadastro da paciente no contexto assistencial | É a base natural de um prontuário |
| Art. 7º, II — cumprimento de obrigação legal ou regulatória | Aplicável a notificação compulsória | Notificação SINAN de violência (Lei nº 10.778/2003, Portaria MS/GM nº 1.271/2014) |
| Art. 7º, I — consentimento | **Não** é a base adequada para prontuário | Consentimento em relação assistencial é frágil: há assimetria de poder e o tratamento não pode ser interrompido sem prejuízo ao cuidado |
| Art. 7º, IX — legítimo interesse | **Inaplicável** a dado sensível | O art. 11 não admite legítimo interesse |

### 3.2 Dados pessoais sensíveis (art. 11)

| Base legal | Aplicabilidade | Observação |
|---|---|---|
| Art. 11, II, "f" — **tutela da saúde**, exclusivamente em procedimento realizado por profissionais de saúde, serviços de saúde ou autoridade sanitária | **Base principal** de todo o tratamento clínico do sistema | Note o "exclusivamente": o tratamento precisa ocorrer **no** procedimento de saúde, por profissional. Isso é relevante para um sistema de apoio à decisão — ele só se sustenta nessa base se operado por profissional no contexto assistencial, o que reforça a exigência de autenticação (§5) |
| Art. 11, II, "a" — cumprimento de obrigação legal | Notificação compulsória de violência | Base independente do consentimento — e é o que permite registrar sem autorização da vítima |
| Art. 11, II, "e" — proteção da vida ou da incolumidade física | Situações de emergência obstétrica | Sustentaria o caminho `bypass_ml` |
| Art. 11, I — consentimento **específico e destacado** | Seria exigível para uso **secundário**, como treinar modelo com dados reais de pacientes | É a base que **faltaria** se o dataset viesse de prontuário real |
| Art. 11, II, "c" — estudos por órgão de pesquisa, com anonimização sempre que possível | Base de um cenário de pesquisa | Exigiria aprovação em CEP/CONEP, o que este projeto não tem |

**A conclusão prática desta seção:** a linha de risco não é o uso assistencial do sistema — essa
tem base legal clara no art. 11, II, "f". A linha de risco é o **uso secundário para treinamento**.
Treinar um modelo com prontuários reais é finalidade distinta do atendimento que os originou, e
exigiria consentimento específico (art. 11, I) ou enquadramento como pesquisa (art. 11, II, "c")
com anonimização e aprovação ética. Este projeto contorna integralmente esse problema ao gerar o
dataset — e essa é a razão **ética**, não apenas prática, da escolha registrada na ADR-004 e em
`CONTRATO_DE_DADOS.md` §1.

### 3.3 O artigo que mais importa para um sistema de ML: art. 20

O art. 20 garante ao titular o direito de solicitar **revisão de decisões tomadas unicamente com
base em tratamento automatizado** que afetem seus interesses, incluindo decisões destinadas a
definir seu perfil pessoal ou profissional. O §1º acrescenta o dever do controlador de fornecer,
quando solicitado, **informações claras e adequadas sobre os critérios e procedimentos** da decisão
automatizada.

Três elementos da arquitetura alvo correspondem, por coincidência de bom desenho, ao que o art. 20
exigiria:

| Elemento da arquitetura | Correspondência com o art. 20 |
|---|---|
| A decisão **não** é unicamente automatizada: há profissional no circuito, e a regra determinística precede e pode anular o modelo (ADR-006) | Afasta a hipótese central do art. 20 *caput* |
| `top_features` com contribuição e direção por variável; `explanation_method` declarado (RF-10, ADR-008) | Atende materialmente ao dever de informação do §1º |
| `predicoes_ml` registra modelo, versão, limiar, `features_hash` e modo (RF-15) | Permite **reconstruir** a decisão para revisá-la — pré-requisito de qualquer revisão útil |
| Caminho human-in-the-loop com dados incompletos (RF-21) | Impede decisão automatizada sobre base insuficiente |

Isso deve ser lido com cuidado: a arquitetura é **compatível** com o art. 20, não conforme a ele.
Conformidade exigiria canal de atendimento ao titular, prazo de resposta e processo de revisão
documentado — nenhum dos três existe (§5).

---

## 4. Princípios do art. 6º aplicados a este projeto

| Princípio (art. 6º) | Como se manifesta aqui | Situação |
|---|---|---|
| **Finalidade** (I) | Finalidade única e declarada: apoio à decisão clínica em saúde da mulher, em demonstração acadêmica. O dataset de ML tem finalidade declarada em `CONTRATO_DE_DADOS.md` §2 | **Atendido por declaração** |
| **Adequação** (II) | As 24 features são variáveis de estratificação de risco obstétrico segundo protocolos MS/FEBRASGO; nenhuma é coletada "por poder ser útil" | **Atendido no desenho** |
| **Necessidade / minimização** (III) | Ver §4.2 — é o princípio com maior número de decisões concretas nesta fase | **Atendido no desenho, com uma exceção `[COD]`** |
| **Livre acesso** (IV) | Não há mecanismo de acesso do titular | **Ausente** — aceitável sem titular; bloqueante em uso real |
| **Qualidade dos dados** (V) | Validação Pydantic com domínio por campo, validadores cruzados obstétricos, `extra='forbid'` (RF-02) | **Projetado** |
| **Transparência** (VI) | `explanation_method` no payload; fontes RAG citadas; limiar exibido; avisos estruturados | **Projetado** |
| **Segurança** (VII) | Ver `CONTROLES_DE_SEGURANCA.md`. SQL parametrizado `[COD]`; sem criptografia em repouso | **Parcial** |
| **Prevenção** (VIII) | Regra determinística precedendo o ML; caminhos de exceção explícitos | **Projetado** |
| **Não discriminação** (IX) | Análise de subgrupo obrigatória (RSC-13); nenhuma feature de raça, religião ou origem no contrato de dados | **Projetado** |
| **Responsabilização e prestação de contas** (X) | `log_acesso` `[COD]` + `predicoes_ml` projetado | **Parcial — ver ressalva em §5.3** |

### 4.1 O achado concreto de minimização — e é um achado real

`lib/ui.py:63-66`:

```63:70:lib/ui.py
    n_viol = conn.execute(
        'SELECT COUNT(*) AS c FROM registros_violencia WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()['c']
    if n_viol > 0:
        linhas.append(
            f'\n🔒 **{n_viol} registro(s) prévio(s) em `registros_violencia`** '
            f'(acesso requer motivo clínico — auditoria LGPD).'
        )
```

A sidebar lê a **contagem** de registros de violência de uma paciente diretamente pelo `conn`, sem
passar por `tools.consultar_violencia`. Três consequências, todas verificáveis:

1. **Contorna a exigência de justificativa.** `consultar_violencia` rejeita acesso sem `motivo` de
   pelo menos 5 caracteres (`lib/tools.py:188-190`). Esta consulta não pede motivo nenhum.
2. **Não gera registro de auditoria.** `_log_acesso` (`lib/tools.py:33-39`) não é chamado. O acesso
   não existe em `log_acesso`, portanto é indistinguível de um acesso que nunca ocorreu.
3. **Divulga a informação mais sensível do sistema por efeito colateral.** O texto renderizado
   informa que **existe** histórico de violência. Para esse dado, a existência é a informação: saber
   que há dois registros já revela que a paciente foi atendida por violência. E a mensagem exibida
   afirma, na própria tela, que "acesso requer motivo clínico — auditoria LGPD" — enquanto o acesso
   que a produziu não teve nem motivo nem auditoria.

É o tipo de defeito que só aparece com leitura do código, porque o comportamento observável parece
correto: o aviso de LGPD está lá. O controle é que não está.

**Registrado como:** LAC-11 (`docs/03_LACUNAS_E_RISCOS.md`), RSC-07 (`ANALISE_DE_RISCOS.md`),
vinculado a RNF-05 e RNF-06. **Correção:** ou a contagem passa por função auditada — com motivo
fixo do tipo `"visualização de painel de alertas"` gravado em `log_acesso` —, ou o indicador sai da
sidebar. A segunda opção é a mais alinhada à minimização: um painel de alertas não precisa revelar
existência de histórico de violência para cumprir sua função.

### 4.2 Minimização na nova fase: três decisões concretas

Estas são as decisões de privacidade específicas desta fase, todas registradas em
`ARQUITETURA_ALVO.md` §5.3 e verificáveis no DDL de `predicoes_ml`.

**(a) `features_hash` em vez dos valores das features.**

A auditoria precisa provar que duas predições partiram das mesmas entradas — é requisito de
reprodutibilidade e de rastreabilidade (RNF-03). A forma óbvia de fazer isso seria gravar as 24
features. Isso criaria um **segundo prontuário**: uma tabela de auditoria contendo pressão arterial,
IMC, hemoglobina, glicemia e comorbidades de cada paciente avaliada, com finalidade diferente da
tabela clínica e sem as proteções que ela tem. O hash SHA-256 das features entrega a propriedade
desejada — igualdade de entradas é verificável — sem duplicar o dado sensível.

O que se perde: não é possível reconstruir os valores a partir da auditoria. Isso é intencional. A
reconstrução, quando necessária, parte do prontuário, que é a fonte legítima.

**(b) `top_features` persistido sem o campo `value`.**

O payload entregue ao LLM e à interface inclui o valor da variável — `{"feature": "has_cronica",
"value": true, "contribution": 0.31, "direction": "aumenta"}` — porque a explicação precisa dele
para fazer sentido clínico. A auditoria persiste apenas `feature`, `contribution` e `direction`.

A razão é que gravar os valores explicativos anularia parcialmente o ganho de (a): as 5 variáveis
mais influentes são justamente as mais informativas sobre a paciente. Guardar 24 valores atrás de um
hash e 5 valores em claro na mesma linha seria uma proteção decorativa. Este ponto estava
explicitamente **em aberto** em `ESTRATEGIA_DE_SEGURANCA.md` §5.1, com recomendação do
`ArchitectureAgent`; **esta é a decisão que o fecha**, e ela é vinculante para o DDL.

O que se perde: a auditoria diz "a hemoglobina contribuiu +0,18 para o risco" sem dizer qual era a
hemoglobina. Para revisão de decisão isso basta, porque a direção e a magnitude da contribuição são
o que se audita; o valor está no prontuário.

**(c) `probabilidade` e `threshold` anuláveis.**

Decisão de integridade que também é de privacidade, por um caminho indireto: recusar o valor
sentinela evita gravar um número que afirma algo falso sobre a paciente. Em três dos quatro modos
não houve inferência — `bypass_regra`, `degradado`, `incompleto` — e um `0.0` gravado como
probabilidade é uma afirmação clínica inventada sobre um dado sensível. `NULL` significa "não houve
inferência", que é a verdade. Ver `POLITICA_DE_AUDITORIA.md` §3.2.

### 4.3 O que a auditoria deliberadamente não armazena

| Não armazenado | Razão |
|---|---|
| Valores das 24 features | Minimização: `features_hash` entrega a propriedade sem o dado (§4.2a) |
| `value` em `top_features` | Minimização: anularia o ganho do hash (§4.2b) |
| Texto gerado pelo LLM | Não é dado de decisão; a decisão está nos campos estruturados. Armazená-lo criaria um registro narrativo sobre saúde sem finalidade definida |
| Prompt enviado ao LLM | Contém os valores clínicos do payload. Mesmo motivo de (a) |
| Descrição em texto livre do caso | Idem |
| Nome ou CPF da paciente | Apenas `paciente_id` (chave estrangeira). O vínculo à identidade fica na tabela que já o tem |
| Chaves dos sinais de alarme disparados | Ponto que estava em aberto em `ESTRATEGIA_DE_SEGURANCA.md` §5.2. **Decisão:** `regras_disparadas` grava as **chaves** (ex.: `["epigastralgia"]`), porque sem elas é impossível auditar *por que* houve bypass — e um bypass não auditável derrota o propósito do registro. A alternativa conservadora (`n_regras`) foi rejeitada: registrar que "2 regras dispararam" sem dizer quais torna o registro inútil para revisão. O log **estruturado** (`lib/observabilidade.py`), que tem retenção e controle de acesso mais fracos, continua limitado à contagem |

---

## 5. Controles existentes, controles ausentes

### 5.1 Controles que existem hoje — verificados no código

| # | Controle | Evidência | Efeito de privacidade |
|---|---|---|---|
| 1 | **Dados 100 % sintéticos** | `lib/mock_data.py` — `Faker('pt_BR')`, semente 42 | Elimina o escopo material da LGPD. É o controle mais forte do projeto |
| 2 | **Tabela de auditoria de acesso** | `log_acesso` (`lib/db.py:74-82`): timestamp, usuario, tabela, paciente_id, motivo | Registro das operações de tratamento, análogo ao art. 37 |
| 3 | **Justificativa obrigatória de acesso a dado sensível** | `lib/tools.py:188-190` — `motivo` com ≥ 5 caracteres, sob pena de recusa | Vincula acesso a finalidade declarada, por acesso |
| 4 | **Log antes da escrita** | `lib/tools.py:168` — `_log_acesso` precede o `INSERT` em `registrar_violencia` | Se o `INSERT` falhar, a tentativa fica registrada. A ordem importa |
| 5 | **CPF não armazenado em claro** | `lib/mock_data.py:100-101` — SHA-256 truncado em 16 hexadecimais | Pseudonimização do identificador direto. Ver ressalva em §5.3 |
| 6 | **Isolamento da tabela mais sensível** | `registros_violencia` em tabela própria (`lib/db.py:63-72`), não colunas de `prontuario_gineco` | Permite controle de acesso e retenção diferenciados |
| 7 | **Acesso sempre por `paciente_id` explícito, nunca por nome** | Docstring e assinatura de todas as tools em `lib/tools.py` | Impede busca exploratória e vazamento cruzado por inferência de nome |
| 8 | **SQL 100 % parametrizado** | Auditado em `ESTRATEGIA_DE_SEGURANCA.md` §3.1: 20 chamadas a `execute` em `lib/`, todas com parâmetros vinculados. A única interpolação é `f'DROP TABLE IF EXISTS {t}'` (`lib/db.py:118`), onde `t` itera uma lista literal de 7 nomes declarada 3 linhas acima — **não é injetável** | Impede extração de dado por injeção |
| 9 | **`log_acesso` sem FK para `pacientes`** | `lib/db.py:74-82` — ausência deliberada de `FOREIGN KEY` | O registro de auditoria sobrevive à remoção da paciente. É pré-requisito para qualquer política de eliminação (art. 16) |
| 10 | **Segredos fora do repositório** | `.gitignore` linhas 1-8: `.env`, `.env.*`, `!.env.example`, `*.token`, `*.key`, `**/credentials.json`, `**/secrets.json` | `HF_TOKEN` nunca versionado; a exceção `!.env.example` é o que a ADR-009 precisa |

### 5.2 Controles ausentes

Declaração explícita, para que a ausência seja decisão registrada e não omissão.

| Ausente | Estado atual | Consequência hoje | Exigência em uso real |
|---|---|---|---|
| **Autenticação** | `_USUARIO_ATUAL` é variável global de módulo (`lib/tools.py:21`) escrita por uma caixa de texto (`lib/ui.py:318`) | A auditoria registra o nome digitado, não a identidade. Ver §5.3 | **Bloqueante.** Sem ela o art. 11, II, "f" não se sustenta: não há como demonstrar que o tratamento ocorreu por profissional de saúde |
| **Autorização / RBAC** | Não há papéis; qualquer usuário acessa qualquer paciente e qualquer tabela | Acesso a `registros_violencia` é auditado, mas não restrito | **Necessário.** Acesso a dado de violência deveria ser restrito por perfil, com dupla justificativa |
| **Criptografia em repouso** | `hospital.db` é arquivo SQLite em claro | Nenhuma — os dados são sintéticos | **Necessário.** SQLCipher ou criptografia de volume (art. 46) |
| **Criptografia em trânsito sob nosso controle** | O túnel do Gradio usa HTTPS, mas a terminação não é nossa | Baixa, no escopo | **Necessário.** TLS próprio |
| **Política de retenção e expurgo** | Nenhum mecanismo de expiração em `log_acesso`; nenhum previsto em `predicoes_ml` | Crescimento indefinido | **Necessário.** Art. 15/16 exigem término do tratamento e eliminação. Ver `POLITICA_DE_AUDITORIA.md` §5 |
| **Atendimento aos direitos do titular (art. 18)** | Não existe nenhum mecanismo | Sem titular, não há direito a exercer | **Bloqueante.** Ver §6 |
| **Processo de revisão de decisão automatizada (art. 20)** | Os dados para revisar existem; o processo não | — | **Necessário** |
| **Pipeline de remoção de identificadores (de-identification)** | Não existe. Não é necessário: não há dado real entrando | — | **Necessário** se houvesse ingestão de prontuário real, com verificação de quase-identificadores, não só de identificadores diretos |
| **Registro das operações de tratamento (art. 37)** | `log_acesso` cobre acesso a `registros_violencia`; `predicoes_ml` cobrirá decisões de ML | Nenhuma outra leitura de prontuário é registrada | **Necessário** ampliar a todas as leituras de dado sensível |
| **Encarregado (DPO), RIPD, resposta a incidentes** | Inexistentes | — | **Necessário.** Um sistema de ML sobre dado sensível de saúde é caso típico de Relatório de Impacto (art. 38) |
| **Varredura de dependências** | Não há `requirements.txt` hoje | — | Recomendado. Com os três arquivos de requisitos, `pip-audit` passa a ser viável (RNF-05) |

### 5.3 As duas fragilidades que precisam ser ditas sempre

**(a) A auditoria registra uma string, não uma identidade.**

`log_acesso.usuario` e `predicoes_ml.usuario` recebem o valor de `_USUARIO_ATUAL`, uma variável
global de módulo alimentada por um campo de texto livre. Não há verificação de nada. E porque o
Gradio cria uma thread por requisição — fato reconhecido em `lib/db.py:22-24`, que usa
`check_same_thread=False` por isso —, duas sessões simultâneas **compartilham** a variável: a
última escrita vence, e um acesso pode ser atribuído ao usuário errado.

A consequência é que a trilha de auditoria deste sistema é um **rastro de sessão**, não um
mecanismo de responsabilização. Ela responde "o que foi acessado e com que justificativa declarada",
e não responde "por quem". Toda vez que a auditoria for apresentada como controle de conformidade —
na interface, no relatório, no vídeo — essa limitação precisa aparecer na mesma frase. Registrado
como LAC-10 e RSC-14.

**(b) O hash de CPF não protegeria um CPF real.**

`hash_cpf` (`lib/mock_data.py:100-101`) aplica SHA-256 e trunca em 16 hexadecimais. Duas
propriedades o tornam inadequado para dado real: é **sem sal**, e o espaço de entrada é pequeno e
enumerável — existem ~10¹⁰ CPFs sintaticamente possíveis, o que é trivialmente varrível em hardware
comum. Um hash sem sal sobre espaço enumerável é pseudonimização fraca: dado o hash, recupera-se o
CPF.

No escopo atual isso é irrelevante, porque os CPFs são gerados pelo Faker e não pertencem a ninguém.
Em uso real o correto seria HMAC-SHA-256 com chave gerenciada fora do banco, ou tokenização com
mapeamento em cofre separado. O mesmo raciocínio se aplica ao `features_hash` de `predicoes_ml`: o
espaço de combinações de features é grande, mas não astronômico, e um ataque de dicionário sobre
perfis plausíveis é concebível. Em uso real, `features_hash` deveria ser HMAC com chave, não SHA-256
puro. Registrado como RSC-08.

---

## 6. Direitos do titular (art. 18) — o que faltaria

Nenhum dos mecanismos abaixo existe, e nenhum é exigível no escopo atual, por ausência de titular.
A tabela existe para que a lacuna seja dimensionada, não escondida.

| Direito (art. 18) | Viabilidade técnica no schema atual | O que faltaria |
|---|---|---|
| **Confirmação e acesso** (I, II) | Alta — `paciente_id` indexa todas as tabelas | Endpoint ou relatório por paciente; identificação do requerente |
| **Correção** (III) | Alta — `UPDATE` simples | Processo, autorização e registro da correção |
| **Anonimização, bloqueio ou eliminação de dado desnecessário ou excessivo** (IV) | Média | Critério de "excessivo" definido; o indicador de `ui.py:63-66` seria o primeiro candidato |
| **Portabilidade** (V) | Média | Formato interoperável; nada padronizado hoje |
| **Eliminação de dado tratado com consentimento** (VI) | **Baixa — e é um conflito real, não uma limitação técnica** | Ver §6.1 |
| **Informação sobre compartilhamento** (VII) | Alta — não há compartilhamento com terceiros | Declaração formal |
| **Informação sobre a possibilidade de não consentir** (VIII) | — | Aviso de privacidade, inexistente |
| **Revogação do consentimento** (IX) | — | Depende de o consentimento ser a base, o que não é o caso no prontuário |
| **Revisão de decisão automatizada** (art. 20) | **Alta** — `predicoes_ml` guarda modelo, versão, limiar, hash e modo, o que permite reconstruir a decisão | Canal, prazo e processo de revisão |

### 6.1 O conflito entre eliminação e auditoria, dito com honestidade

Pedido de eliminação (art. 18, VI) e obrigação de auditoria colidem, e a colisão tem resposta
jurídica conhecida: o art. 16 admite a conservação de dados para cumprimento de obrigação legal ou
regulatória, e o art. 18, §4º ressalva a hipótese de conservação. Registros de saúde têm prazo
mínimo de guarda por norma própria — a Resolução CFM nº 1.821/2007 estabelece 20 anos para o
prontuário —, e notificação compulsória de violência não é eliminável a pedido, porque não depende
de consentimento (art. 11, II, "a").

Consequência de desenho: a decisão de **não** colocar `FOREIGN KEY` em `log_acesso` (`lib/db.py:74-82`)
é o que permitiria eliminar o cadastro da paciente preservando o rastro de quem acessou o quê.
`predicoes_ml`, em contraste, **tem** FK para `pacientes` (`ARQUITETURA_ALVO.md` §5.3) — o que é
correto para integridade referencial e cria, em uso real, exatamente esse conflito. A saída seria
desvincular (`ON DELETE SET NULL`) em vez de apagar a linha de auditoria. Não é decisão desta fase,
e fica registrada aqui como consequência conhecida do DDL.

---

## 7. O que é aceitável nesta demonstração e o que não seria em produção

| Dimensão | Aceitável aqui | Por quê | Inaceitável em produção |
|---|---|---|---|
| Sem autenticação | **Sim** | Usuário único, dados sintéticos, ambiente local | **Sim.** É a primeira ausência a corrigir — sem ela o art. 11, II, "f" não se sustenta e a auditoria é ficção |
| Sem criptografia em repouso | **Sim** | Não há dado pessoal a proteger | **Sim.** Art. 46 |
| Hash de CPF sem sal e truncado | **Sim** | CPFs são do Faker | **Sim.** Pseudonimização reversível por força bruta |
| Sem retenção definida | **Sim** | Banco descartável, regenerável por `mock_data` | **Sim.** Art. 15/16 |
| Sem canal para direitos do titular | **Sim** | Não há titular | **Sim.** Art. 18 |
| Sem RIPD / DPO | **Sim** | Sem tratamento de dado pessoal | **Sim.** Art. 38 e 41 — ML sobre dado sensível de saúde é caso típico |
| Métricas obtidas em dado sintético | **Sim, se declarado** | É o único dado disponível (`CONTRATO_DE_DADOS.md` §1) | **Não se apresentadas como validação clínica.** Ver RSC-03 |
| Modelo sem validação clínica | **Sim, se declarado** | Demonstração de pipeline, não de produto | **Sim.** Exigiria coorte prospectiva, aprovação ética e possivelmente registro sanitário |
| `share=True` no perfil `full-gpu` | **Com ressalva** | Conveniente para gravar o vídeo; dados sintéticos | **Sim.** Publica a aplicação sem autenticação por ~72 h |
| Indicador de violência na sidebar sem auditoria | **Não** | É defeito, não escopo. Ver §4.1 | **Sim** |

A última linha é a única em que a resposta é "não" nas duas colunas, e é por isso que o achado de
`ui.py:63-66` é tratado como o item de maior prioridade deste documento. Todas as demais ausências
são **decisões de escopo declaradas**; essa é uma **falha de implementação** de um controle que o
próprio código afirma ter.

---

## 8. Checklist de privacidade para a implementação

| # | Verificação | Como | Teste |
|---|---|---|---|
| 1 | `predicoes_ml` não tem nenhuma coluna de valor clínico | Revisão do DDL | `tests/unit/test_schema_auditoria.py` |
| 2 | `top_features` persistido sem a chave `value` | Inspeção do JSON gravado | `tests/unit/test_schema_auditoria.py` |
| 3 | `features_hash` é SHA-256 de representação canônica e ordenada das features | Revisão de `lib/ml/predict.py` | `tests/unit/test_features_hash_estavel.py` |
| 4 | Nenhum valor clínico no log estruturado | Execução com valor sentinela e busca na saída | `tests/unit/test_observabilidade.py` |
| 5 | `HF_TOKEN` nunca aparece em log nem em mensagem de erro | Forçar falha de carga e inspecionar a saída | `tests/unit/test_sem_segredos.py` |
| 6 | 100 % dos dados de origem sintética; nenhum caminho de importação de dado real | Revisão de `lib/ml/dataset.py` e `lib/mock_data.py` | `tests/unit/test_dataset_reprodutivel.py` |
| 7 | `predicoes_ml` só recebe `INSERT` parametrizado; sem `UPDATE` nem `DELETE` no caminho da aplicação | Busca por `UPDATE`/`DELETE` nos módulos novos | Revisão + RNF-05 |
| 8 | O indicador de `ui.py:63-66` foi corrigido ou removido | Revisão | Teste de caminho auditado |
| 9 | O dump de exemplo publicado em `docs/seguranca/` não contém valor clínico legível | Inspeção manual do dump | Revisão |

---

## 9. Documentos relacionados

| Documento | Conteúdo |
|---|---|
| `docs/seguranca/POLITICA_DE_AUDITORIA.md` | O que é auditado, DDL completo, invariante de uma linha por execução, receitas de consulta, retenção |
| `docs/seguranca/CONTROLES_DE_SEGURANCA.md` | Catálogo `CTR-xx` com tipo, camada, status e teste |
| `docs/seguranca/ANALISE_DE_RISCOS.md` | RSC-07 (violência), RSC-08 (reidentificação), RSC-14 (identidade não verificada) |
| `docs/arquitetura/ESTRATEGIA_DE_SEGURANCA.md` | Fronteiras de confiança, superfície de ataque, §5.1 (ponto que este documento fecha) |
| `docs/arquitetura/ARQUITETURA_ALVO.md` §5.3 | DDL de `predicoes_ml` e as três justificativas de desenho |
| `docs/dados/CONTRATO_DE_DADOS.md` §1 e §2 | Declaração de ausência de dado real e natureza sintética do dataset |
