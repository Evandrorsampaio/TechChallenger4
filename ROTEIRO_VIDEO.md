# Roteiro de treino e gravação do vídeo (15 min)

## Guardiã AI — Inteligência Artificial para Saúde e Segurança da Mulher

**Duração-alvo:** 14 minutos e 20 segundos (40 segundos de margem sobre o limite de 15 minutos).  
**Formato:** screencast com narração, 1080p, 30 fps (OBS Studio ou Loom).  
**Quem fala:** uma pessoa do grupo, em primeira pessoa. O texto abaixo está na voz do Evandro Rosa Sampaio. Se outra pessoa gravar, troque só a primeira frase.  
**Grupo:** Evandro Rosa Sampaio, Gustavo Brasil Pires Octaviano, Paulo Roberto Gonçalves, Wallace Gomes da Silva.

**Como usar este teleprompter**

- Ritmo de fala: cerca de **135 palavras por minuto**, pausado, como quem explica para a banca e não como quem lê um relatório.
- Cada bloco traz o texto **inteiro** para o tempo da tabela. A contagem já inclui as pausas curtas entre parágrafos. Se sobrar até cinco segundos, respire e siga. Não acelere o bloco seguinte.
- Linhas em *itálico* são ação de tela. Não se fala.
- Números estão escritos como se pronunciam.
- Não dizer “validado clinicamente”. O projeto **não** passou por validação clínica.
- Não dizer que o Docker está “funcionando em produção”. A imagem existe; o Llama não entra nela.

---

## Cronograma

| Bloco | Duração | Minutagem | O que mostrar | Foco da fala |
|---|---|---|---|---|
| **1. Abertura** | 0:30 | 0:00–0:30 | Cabeçalho do `README.md` | Quem somos, o que é a Guardiã AI, dado sintético, apoio e não decisão |
| **2. Arquitetura** | 1:30 | 0:30–2:00 | Diagrama no `README.md` | Quatro camadas, cinco fluxos, dez ferramentas, LLM que não classifica risco |
| **3. ML e fine-tuning** | 2:30 | 2:00–4:30 | `comparacao.json` e trecho do README sobre QLoRA | 8 mil gestantes, regressão logística, limiar, e o ajuste do Llama |
| **4. Ferramentas e templates** | 1:10 | 4:30–5:40 | `lib/tools.py` e `lib/templates/` | Dez tools, quatro documentos clínicos, ponte para a demo |
| **5. Demo Gradio** | 6:00 | 5:40–11:40 | `http://localhost:7860` | Jornada nas seis abas (tempos abaixo) |
| **6. LGPD e gestão** | 1:20 | 11:40–13:00 | `log_acesso` e notebook 10 | Auditoria, `predicoes_ml`, relatório do serviço |
| **7. Encerramento** | 1:20 | 13:00–14:20 | Limitações no `README.md` | O que a gente não promete, e o repositório |
| **Total** | **14:20** | | | Margem de 40 s até 15:00 |

Os sub-blocos da demo somam **6:00**. A versão anterior deles somava 6:45 e estouraria o limite.

| Demo | Duração | Minutagem |
|---|---|---|
| 5.0 Barra lateral | 0:25 | 5:40–6:05 |
| 5.1 Consulta livre | 0:40 | 6:05–6:45 |
| 5.2 Triagem | 0:55 | 6:45–7:40 |
| 5.3 Violência | 1:20 | 7:40–9:00 |
| 5.4 Obstétrico | 0:55 | 9:00–9:55 |
| 5.5 Prevenção | 0:40 | 9:55–10:35 |
| 5.6 Risco gestacional | 1:05 | 10:35–11:40 |

---

## Fala por bloco

### Bloco 1 — Abertura (0:00–0:30)

*Tela: cabeçalho do `README.md`, com o nome do projeto e o aviso de dado sintético.*

Olá. Eu sou o Evandro Rosa Sampaio, da Pós Tech FIAP em IA para Devs, com o Gustavo Octaviano, o Paulo Gonçalves e o Wallace Gomes.

A Guardiã AI é o nosso Tech Challenge da Fase cinco. Apoia médico, enfermeiro e residente na saúde e na segurança da mulher. Os dados são sintéticos. Não substitui a avaliação clínica, e quem decide é a pessoa que atende.

---

### Bloco 2 — Arquitetura (0:30–2:00)

*Tela: diagrama de arquitetura no `README.md`. Aponte cada faixa enquanto fala dela. Não role rápido.*

Aqui está o caminho de um atendimento, de cima para baixo.

No topo, a interface Gradio, com seis abas.

Embaixo dela, a orquestração. São cinco fluxos em LangGraph: triagem ginecológica, violência, atendimento obstétrico, prevenção e o risco gestacional, que é a jornada principal desta fase. A consulta livre usa um agente ReAct, do LangChain, que escolhe a ferramenta na hora.

Esses fluxos chamam dez ferramentas. Elas falam com três lugares. O SQLite guarda o prontuário sintético, o log de acesso e cada predição. O módulo de machine learning calcula o risco e mostra quais variáveis pesaram. O RAG busca o protocolo. Sem GPU, essa busca é lexical, num recorte dos textos. No Colab, o índice completo fica no Chroma.

Nesta gravação o texto sai de um dublê, o FakeChatModel, porque não há GPU. O Llama três ponto dois com QLoRA fica no Colab.

E tem uma regra que a gente não negocia. A LLM não classifica risco. Ela só explica número que o modelo já calculou. Se o texto dela mudar probabilidade ou limiar, um validador joga a frase fora e devolve um template fixo. Emergência não espera um segundo passe de modelo.

---

### Bloco 3 — Machine learning e fine-tuning (2:00–4:30)

*Tela: `artifacts/metrics/comparacao.json`, depois a tabela de resultados no `README.md`. Segure o cursor no PR-AUC e no limiar quando citar os números.*

Agora os números.

O dataset tem oito mil gestantes sintéticas, vinte e quatro variáveis, semente quarenta e dois. A divisão é cinco mil e seiscentos para treino, mil e duzentos para validação e mil e duzentos para teste. O manifesto ao lado guarda o SHA-256 desse arquivo.

No mesmo teste a gente comparou quatro caminhos: um dummy pela prevalência, uma regra clínica, a regressão logística e a random forest. A regressão logística foi a escolhida. O PR-AUC dela é zero vírgula cinco nove zero. O recall de alto risco é zero vírgula nove cinco cinco, com limiar de zero vírgula dois sete oito. Esse limiar não é zero vírgula cinco. Na validação, pegamos o menor corte que ainda segura pelo menos noventa por cento de recall.

A acurácia enganaria aqui. Alto risco é minoria. Um modelo que respondesse sempre “risco habitual” acertaria uns setenta e nove por cento e não acharia ninguém. O erro que mais nos preocupa é o falso negativo: atrasar o encaminhamento de quem precisa. No teste, onze de duzentos e quarenta e sete casos de alto risco passaram batido. O custo aparece na precisão, zero vírgula dois seis cinco. Mais ou menos três em cada quatro alertas são falso positivo, e o profissional revisa cada um.

No texto, reaproveitamos o fine-tuning da fase três. São seis mil quatrocentos e catorze pares, a partir de trinta e nove documentos do Ministério da Saúde, da FEBRASGO, da OMS e do INCA, em cinco categorias. O ajuste é QLoRA em quatro bits, no Llama três ponto dois de três bilhões.

Numa comparação com trinta exemplos, a citação da rede de apoio — SINAN, Ligue cento e oitenta, CVV, CAPS — saiu de cerca de trinta e três por cento no modelo base para cerca de cem por cento no modelo ajustado. São trinta exemplos, então eu trato isso como sinal, não como prova.

---

### Bloco 4 — Ferramentas e documentos (4:30–5:40)

*Tela: `lib/tools.py`, role só o bastante para mostrar a lista. Depois abra `lib/templates/`.*

A lógica que a interface chama está nestas dez ferramentas. Tem consulta de prontuário, exame atrasado, categoria de medicamento na gestação, predição de risco e a busca no protocolo. O profissional não monta SQL nem prompt. Ele descreve o caso, e a ferramenta devolve dado estruturado.

Na pasta de templates ficam os documentos que o fluxo preenche: laudo de mamografia no padrão BI-RADS, receita de terapia hormonal com o checklist da FEBRASGO, ficha SINAN de notificação e o relatório de atendimento à violência, no formato da norma técnica do Ministério da Saúde. São rascunhos. Quem assina continua sendo o profissional.

Nenhuma ferramenta prescreve remédio nem fecha diagnóstico. Ela devolve fato: exame, protocolo, escore, texto de documento. A conduta fica fora do modelo. É esse contrato que a tela vai cumprir agora.

Vou para o navegador. O resto do vídeo é o sistema em uso.

---

### Bloco 5 — Demonstração na Gradio (5:40–11:40)

*Tela: Gradio já aberto em `http://localhost:7860`, com a barra lateral visível. Deixe os textos da seção “colar na hora” num bloco de notas ao lado.*

#### 5.0 Barra lateral (5:40–6:05)

*Ação: abrir o dropdown e escolher uma paciente sintética. Espere os alertas renderizarem.*

Na barra lateral eu escolho uma paciente. O nome sai do Faker, então não é uma pessoa real. No mesmo instante a tela monta o contexto: exame preventivo atrasado aparece em vermelho, e um registro de violência, quando existe, fica marcado com cadeado. O profissional vê o alerta antes de abrir qualquer aba.

#### 5.1 Consulta livre (6:05–6:45)

*Ação: aba Consulta livre. Colar a pergunta e enviar. Se a resposta demorar, continue a fala; não fique em silêncio.*

Na primeira aba a pergunta é livre, do jeito que um residente escreveria. Vou colar: quais os critérios para repetir a citologia numa paciente com menos de vinte e cinco anos e LSIL.

O agente escolhe a ferramenta de protocolos, busca o trecho do Ministério da Saúde e responde citando a fonte. Não é um palpite. Se eu abrir o detalhe da execução, aparece qual ferramenta rodou. Se a tela demorar, é esse caminho acontecendo: ferramenta, trecho, resposta.

#### 5.2 Triagem ginecológica (6:45–7:40)

*Ação: aba Triagem. Colar o relato e clicar em Realizar triagem.*

Segunda aba. O relato é este: paciente de trinta e dois anos, sangramento intenso há três dias, dor pélvica forte irradiando para o ombro, atraso menstrual de oito semanas. Está estável hemodinamicamente.

Clico em realizar triagem. Enquanto a tela trabalha, o grafo extrai os achados do texto e escolhe a rota. Não pergunta ao modelo qual é a gravidade.

Atraso menstrual com dor no ombro é um clássico de suspeita de gestação ectópica. O sistema não espera exame para classificar: marca emergência e pede encaminhamento imediato. Estar estável não apaga o sinal. Só diz que ainda dá tempo de agir rápido, com a paciente consciente. O encaminhamento sai escrito na resposta, para ninguém depender da memória do protocolo.

#### 5.3 Violência e segurança (7:40–9:00)

*Ação: aba Detecção de Violência, workflow completo. Colar o caso, marcar Confirmação clínica e clicar em Avaliar e registrar. Mostre protocolo e id na resposta. Não mostre dado além do que a tela devolver.*

Esta aba eu percorro com mais calma, porque é a de segurança da mulher.

O caso: paciente de vinte e oito anos, manchas roxas em região coberta pela roupa, dorso e coxas, em fases diferentes. O acompanhante não deixa ela falar a sós.

Se ela estivesse na sala, o primeiro gesto seria pedir um instante a sós, antes de qualquer ficha. O sistema só organiza o que o protocolo já manda. Não denuncia no lugar de ninguém.

Juntos, esses achados sobem o score de suspeita. O fluxo orienta tirar o acompanhante da sala, fazer escuta qualificada e acionar a rede: SINAN e, quando couber, o Ligue cento e oitenta. A notificação não sai sozinha. Eu marco a confirmação clínica. Sem esse sim do profissional, o banco não grava.

Clico em avaliar e registrar. A tela devolve protocolo e identificador. Consultar esse registro, em outro momento, exige um motivo clínico de pelo menos cinco caracteres e gera uma linha no log de acesso. O sigilo aqui não é um aviso. É uma trilha.

#### 5.4 Atendimento obstétrico (9:00–9:55)

*Ação: aba Atendimento Obstétrico. Colar o relato e clicar em Avaliar gestação.*

No obstétrico, a gestante tem trinta e quatro anos, terceira gestação, dois partos, nenhuma perda, trinta e duas semanas. Cefaleia intensa há vinte e quatro horas, pontos luminosos na visão e dor no estômago em barra.

Clico em avaliar. Antes de qualquer modelo, uma regra lê o relato e procura sinal de alarme descrito nas diretrizes. Dor de cabeça com alteração visual e dor em barra fecha o alerta de pré-eclâmpsia grave. O fluxo entra em bypass e indica o pronto-atendimento obstétrico. Ele não gasta tempo discutindo risco habitual versus alto risco quando a emergência já está escrita no relato. O machine learning fica para o caso sem alarme na porta.

#### 5.5 Prevenção (9:55–10:35)

*Ação: aba Prevenção, com a mesma paciente da barra lateral. Clicar em Gerar plano preventivo.*

Aqui eu não digito um caso novo. A paciente da barra já traz idade e histórico. Clico em gerar o plano preventivo.

O fluxo compara esse perfil com as diretrizes do Ministério da Saúde. Se a mamografia está atrasada, a conduta aparece com o exame e o prazo. Junto, sai um texto curto de convocação, para SMS ou WhatsApp, em linguagem de chamada e não de laudo. O mesmo fato clínico vira duas peças: uma para o prontuário e outra para chamar a paciente.

#### 5.6 Risco gestacional (10:35–11:40)

*Ação: aba Risco Gestacional (ML). Clicar em carregar os dados da paciente da barra e, em seguida, em Estratificar risco. Se der tempo, aponte probabilidade, limiar e as variáveis de maior peso. Não force o modo degradado nesta tomada.*

Última aba, e é a jornada desta fase. Carrego os dados da paciente selecionada. Entram as variáveis clínicas estruturadas. O modelo foi treinado em vinte e quatro delas, não num texto solto.

Estratifico o risco. A regressão logística devolve uma probabilidade, a tela aplica o limiar de zero vírgula dois sete oito e lista as variáveis que mais pesaram na conta. Se a descrição clínica trouxer um sinal de alarme, a regra corta o caminho e o ML nem roda. Se faltar campo obrigatório, o fluxo pede o complemento, em vez de inventar valor. Ao lado, as variáveis de maior peso explicam a conta, sem caixa-preta. A resposta sempre lembra: isto é apoio à decisão, com dado sintético. A conduta é de quem está na frente da paciente. Cada análise dessa também fica registrada para auditoria, e eu mostro isso já já.

---

### Bloco 6 — LGPD, auditoria e relatório (11:40–13:00)

*Tela: menção ao `log_acesso` no README, seção Segurança. Se o banco estiver aberto, mostre só as colunas (timestamp, usuário, paciente, motivo), sem varrer linhas. Depois o título do notebook `10_relatorio_utilizacao.ipynb`.*

Privacidade, na prática.

Abrir um registro de violência pede justificativa clínica, com no mínimo cinco caracteres, e grava no `log_acesso` o horário, o usuário, a paciente e o motivo. Não é um campo opcional escondido. Sem o motivo, a consulta não segue.

A análise de risco tem outra trilha, a tabela `predicoes_ml`. Cada chamada guarda quem pediu, qual modelo e versão, o hash das variáveis, a probabilidade, o limiar e o modo daquela execução: normal, bypass de emergência, dados incompletos ou modo degradado, quando o modelo não está disponível. A gente persiste o hash, não o valor cru de novo. Dá para auditar a conta sem copiar o prontuário para um segundo lugar.

O prontuário inteiro é sintético. O CPF, quando aparece, está como hash, e o registro de violência mora em tabela separada.

O notebook dez olha o serviço, não um caso só: cobertura de exame preventivo, adesão e indicadores de acolhimento. É o relatório que a gestão lê depois que o consultório já fechou.

---

### Bloco 7 — Limitações e encerramento (13:00–14:20)

*Tela: seção Limitações do `README.md`. Role um item por frase. No final, mostre a URL do repositório.*

Fecho pelo que a gente não promete, porque isso também faz parte da entrega.

Não houve validação clínica. Métrica de dado sintético não descreve paciente real. Nesta máquina, a linguagem é o FakeChatModel, um dublê com resposta estável por padrão de texto. O Llama com QLoRA roda no Colab, com GPU. O RAG local é uma busca lexical num recorte. O índice Chroma, com mil trezentos e noventa e dois trechos de trinta e nove documentos, fica no Drive, fora do Git.

A precisão do alerta é baixa de propósito. O limiar privilegia não perder o caso grave, e cerca de três em cada quatro alertas de alto risco são falso positivo. Quem filtra é o profissional.

Na emergência, a arquitetura não espera um segundo passe de LLM. O sinal de alarme é regra, antes do modelo, para a resposta não depender de latência. Se o texto gerado alterar um número, o validador devolve o template.

O código, os artefatos, os notebooks e a documentação estão no repositório do grupo. Obrigado pelo tempo de vocês.

---

## Textos para colar na gravação

Deixe isto aberto ao lado da Gradio.

| Aba | Colar este texto |
|---|---|
| Consulta livre | `Quais critérios para repetir citologia em paciente <25a com LSIL?` |
| Triagem | `Paciente 32 anos, sangramento intenso há 3 dias, dor pélvica forte irradiando para ombro, atraso menstrual de 8 semanas. Estável hemodinamicamente.` |
| Violência | `Paciente 28a comparece com lesões equimóticas em locais não-expostos (dorso, coxas) em múltiplas fases. Acompanhante não permite que a paciente fale a sós.` |
| Obstétrico | `Gestante 34a, G3P2A0, IG 32 semanas. Cefaleia intensa há 24h, escotomas e dor epigástrica em barra.` |
| Prevenção | Só o botão, com a paciente já escolhida na barra. |
| Risco ML | Carregar os dados da paciente da barra e, em seguida, Estratificar risco. |

Na fala, “G3P2A0” vira “terceira gestação, dois partos, nenhuma perda”, e “escotomas” vira “pontos luminosos na visão”. O texto colado na tela permanece técnico. A narração traduz.

---

## Antes de gravar

1. Leia o bloco 3 em voz alta com um cronômetro. Se passar de dois minutos e trinta, não corte número: corte um adjetivo.
2. Diga “dados sintéticos” na abertura e de novo no encerramento.
3. Se a interface demorar, narre o que o fluxo está fazendo. Silêncio no meio da demo parece falha.
4. Grave a demo numa tomada só, da barra lateral até o risco gestacional. Corte de arquitetura pode ser separado.
