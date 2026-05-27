# Roteiro do Vídeo Demo — Assistente Clínico Hospitalar

**Duração-alvo:** 13 minutos (margem para 15 do limite FIAP).
**Formato:** screencast com narração; sem cortes elaborados, foco na engenharia da aplicação.
**Ferramenta sugerida:** OBS Studio (gratuito) ou Loom; gravar em 1080p, 30fps.
**Estilo do vídeo:** demonstração dirigida pela UI Gradio — o avaliador vê o profissional usando a aplicação, não scripts rodando isolados.

---

## Estrutura macro

| Bloco | Duração | Conteúdo |
|---|---|---|
| 1. Abertura | 0:30 | Identificação + contexto + público-alvo |
| 2. Arquitetura | 1:30 | Diagrama do README + camadas |
| 3. Fine-tuning | 2:30 | Dataset, treino, avaliação (foco na análise honesta) |
| 4. Stack overview | 1:10 | Tools + agente + workflows + **templates clínicos** + RAG |
| 5. Demo UI (★) | 6:00 | 5 tabs em sequência, com paciente em contexto |
| 6. LGPD + relatórios | 1:20 | log_acesso na UI + **notebook 10 (relatório gerencial)** |
| 7. Encerramento | 1:20 | Limitações + justificativa da validação LLM + próximos passos + repo |
| **Total** | **14:20** (margem 0:40 sobre limite de 15) | |

★ = coração do vídeo. Toda a demo acontece na UI Gradio, com o profissional clicando tabs reais.

---

## Bloco 1 — Abertura (0:00 – 0:30)

**O que mostrar:** README.md aberto, cabeçalho do projeto

**Roteiro falado:**
> "Olá, sou [SEU NOME], aluno da Pós Tech FIAP em IA para Devs. Este é o Tech Challenge da Fase 3: um assistente clínico hospitalar especializado em saúde da mulher, voltado para a equipe de saúde do hospital — médicos, enfermeiros, residentes — não para a paciente. O projeto integra fine-tuning de um Llama 3.2 3B com RAG, ferramentas estruturadas no LangChain, e quatro fluxos automatizados em LangGraph, tudo entregue numa interface Gradio que vou demonstrar agora."

---
## Bloco 3 — Fine-tuning (2:00 – 4:30)

### 3.1 Dataset (45s)

**Tela:** `02_gerar_dataset_sft.ipynb` no VSCode. Mostre:
1. Célula `prompts` (PROMPT_PADRAO e PROMPT_SENSITIVE)
2. Célula com output "Total de exemplos válidos: 6414"
3. Célula com "Train: 5134  Val: 640  Test: 640"

**Narração:**
> "Geramos seis mil quatrocentos e catorze pares Q&A a partir de trinta e nove PDFs em cinco categorias. Os prompts são deliberadamente diferenciados: violência e saúde mental usam template que força inclusão de SINAN, Ligue 180, CVV — porque essas categorias exigem encaminhamento, não diagnóstico. As perguntas simulam dúvidas do profissional durante atendimento, não da paciente."

### 3.2 Treino QLoRA (45s)

**Tela:** `03_treinar_qlora.ipynb`. Mostre:
1. Célula `config` — LoRA r=16, alpha=32, todas as 7 projeções lineares
2. Output do treino com `eval_loss` decrescendo
3. Estrutura final em Drive: `files/finetune/llama32-3b-saude-mulher_20260524_0217/adapter_final/`

**Narração:**
> "QLoRA em quatro bits NF4, sobre todas as projeções lineares do modelo. Três epochs, batch efetivo dezesseis, learning rate cosine. Treino completou em duas horas e meia em A100. Adapter final tem cerca de trinta megabytes e fica persistido no Drive."

### 3.3 Avaliação — análise honesta (1:00)

**Tela:** `eval_sidebyside.md` aberto, mostrando 1 exemplo padrão e 1 sensitive (base vs FT vs gold)

**Narração:**
> "A avaliação trouxe um resultado nuançado que vou ser transparente sobre. Em trinta amostras do test set, comparando o modelo base com o fine-tuned: ganho claro em citação de serviços da rede em casos sensitive — de cerca de trinta e três por cento para quase cem por cento. Mas também regressões: ROUGE-L caiu seis por cento, e cerca de sessenta por cento das respostas FT entraram em loops repetitivos."

> "Mitigamos os loops aplicando `repetition_penalty` de 1.2 e `no_repeat_ngram_size` 4 na inferência — sem retreinar. O relatório técnico tem a análise completa: cinco problemas mensuráveis, três vitórias, e cinco recomendações pra iteração 2."

---

## Bloco 4 — Stack overview (4:30 – 5:40)

**O que mostrar:** rápida navegação no VSCode mostrando estrutura `lib/`

```
lib/
├── db.py            ← SQLite + 7 tabelas + log_acesso LGPD
├── tools.py         ← 9 StructuredTools LangChain
├── llm.py           ← load_finetuned + ChatHuggingFace wrapper
├── agent.py         ← LangGraph create_react_agent
├── ui.py            ← Gradio Blocks (5 tabs)
├── workflows/
│   ├── triagem.py       ← StateGraph 7 nodes
│   ├── violencia.py     ← StateGraph 7 nodes
│   ├── obstetrico.py    ← StateGraph 7 nodes
│   └── prevencao.py     ← StateGraph 6 nodes
└── templates/       ← 4 modelos clínicos auto-preenchíveis
    ├── laudo_mamografia_birads.md
    ├── receita_terapia_hormonal.md
    ├── ficha_notificacao_sinan_violencia.md
    └── relatorio_atendimento_violencia.md
```

**Narração:**
> "Toda a lógica está em `lib/`. Nove ferramentas estruturadas — prontuário, exames, exames atrasados, medicamentos com categoria gestacional, calendário menstrual, avaliar padrão de violência, registrar violência com SINAN, consultar violência com auditoria obrigatória, e buscar protocolo via RAG. Quatro workflows LangGraph com StateGraph explícito."

> "E ainda dentro de `lib/templates/`, quatro modelos especializados de documentos clínicos — laudo BI-RADS, receita de terapia hormonal com checklist FEBRASGO, ficha SINAN de notificação compulsória e relatório de atendimento à violência seguindo a Norma Técnica do Ministério. Atendem o requisito de modelos de documentos do enunciado, e ficam disponíveis para integração futura aos workflows, alimentando os campos via placeholders."

> "Tudo orquestrado por uma UI Gradio com cinco tabs que vou demonstrar agora."

**Ação visual rápida (10s):** Abrir `lib/templates/laudo_mamografia_birads.md` no VSCode pra mostrar a estrutura com placeholders. Depois fechar e voltar pro browser do Gradio.

---

## Bloco 5 — Demo na UI Gradio ★ (5:40 – 11:40)

**O coração do vídeo.** Browser com a URL pública do Gradio aberto. Sidebar à esquerda visível durante toda a demo.

### 5.0 Sidebar — selecionar paciente (30s)

**Ação:** dropdown de pacientes → selecionar uma com mamografia atrasada (sidebar mostra alerta 🔴) e idealmente também com flag de violência (🔒). Ex.: Maria Silva, 52a.

**Narração:**
> "A sidebar à esquerda mantém o contexto: profissional logado, paciente em atendimento. Selecionando uma paciente, o painel auto-renderiza alertas — mamografia em atraso há 4 anos em vermelho, e indicação de que existem registros prévios de violência sem mostrar conteúdo. Esse contexto se propaga para todas as cinco tabs."

### 5.1 Tab Consulta livre (45s)

**Tela:** Tab 💬 Consulta livre

**Ação:** Digitar:
```
Quais critérios para repetir citologia em paciente <25a com LSIL?
```
Aguardar resposta. Expandir `🔧 Ferramentas usadas`.

**Narração:**
> "Primeira tab: chat livre com o agente LangChain. O modelo decide quais ferramentas chamar — neste caso, busca no protocolo RAG, retorna a conduta com citação da fonte. O dropdown expansível mostra exatamente quais tools foram invocadas — transparência total."

### 5.2 Tab Triagem Ginecológica (1:00)

**Tela:** Tab 🩺 Triagem Ginecológica

**Ação:** Colar queixa:
```
Paciente 32 anos, sangramento intenso há 3 dias, dor pélvica forte
irradiando para ombro, atraso menstrual de 8 semanas.
Estável hemodinamicamente.
```
Clicar **Realizar triagem**. Aguardar render do output.

**Narração:**
> "Tab dois: triagem ginecológica pelo workflow LangGraph. Cole a queixa, clique. O fluxo extrai sintomas, busca diferenciais no protocolo via RAG, classifica urgência por regras determinísticas — atraso menstrual mais dor irradiando para ombro é sinal de gestação ectópica rota, então emergência. Pula a etapa de exames ambulatoriais e encaminha direto pro pronto-socorro ginecológico."

> "Expandindo o bloco de raciocínio, vejo cada node que executou — explicabilidade nativa pra auditoria."

### 5.3 Tab Detecção de Violência (1:30)

**Tela:** Tab 🛡️ Detecção de Violência → sub-aba "Workflow completo"

**Ação:** Colar descrição:
```
Paciente 28a comparece com lesões equimóticas em locais não-expostos
(face medial das coxas, dorso), em múltiplas fases de cicatrização.
Acompanhante recusou deixar a paciente sozinha, respondendo por ela.
Histórico de 3 atendimentos prévios por queixas inespecíficas.
Relato de isolamento social progressivo nos últimos meses.
```
Marcar checkbox **Confirmação clínica**. Clicar **Avaliar e registrar**.

**Narração:**
> "Tab três é o coração da segurança do projeto. Descrição livre vai pro workflow de violência: o LLM mapeia o texto pros sinais canônicos do protocolo do Ministério, aplica a matriz determinística — esses sinais somam score 6, nível alta suspeita. Ativa protocolo de segurança: ambiente reservado sem acompanhante. Aciona assistência social, psicologia, enfermagem para a notificação SINAN obrigatória."

> "Com a confirmação clínica marcada, gera o registro de fato — id no banco, log_acesso atualizado com o profissional logado e timestamp. Tudo rastreável para LGPD."

**Bonus se sobrar 15s:** Clicar na sub-aba "Checklist heurístico" pra mostrar a alternativa rápida.

### 5.4 Tab Atendimento Obstétrico (1:00)

**Tela:** Tab 🤰 Atendimento Obstétrico

**Ação:** Colar:
```
Gestante 34a, G3P2A0, IG 32 semanas pela DUM. Cefaleia intensa há 24h,
escotomas, edema súbito de face, dor epigástrica em barra.
HAS gestacional diagnosticada na semana 28.
```
IG: deixar vazio (workflow extrai da descrição). Clicar **Avaliar gestação**.

**Narração:**
> "Tab quatro: workflow obstétrico. Cefaleia, escotomas e dor em barra numa gestante com HAS são clássicos de pré-eclâmpsia/HELLP. O regex de sinais de alarme da FEBRASGO pega isso, marca como emergência obstétrica, encaminha imediatamente ao pronto-socorro com a equipe definida — obstetra de plantão, anestesia, neonatologia. A rotina normal de pré-natal cede prioridade ao quadro agudo."

### 5.5 Tab Prevenção (45s)

**Tela:** Tab 📅 Prevenção e Rastreamento

**Ação:** Paciente já está selecionada na sidebar (Maria, 52a, mamografia atrasada). Clicar **Gerar plano preventivo**.

**Narração:**
> "Tab cinco: prevenção, totalmente baseada no perfil da paciente em contexto. O workflow carrega o histórico, identifica a mamografia atrasada usando as regras do Ministério — bienal para 50 a 69 anos. Gera orientação preventiva via RAG, propõe agendamento na mastologia em até quatorze dias por ser prioridade alta, e redige mensagens de lembrete já formatadas pra SMS, WhatsApp ou e-mail. Ponta a ponta, sem o profissional digitar nada além do clique."

---

## Bloco 6 — LGPD, auditoria e relatórios gerenciais (11:40 – 13:00)

Esse bloco virou um pouco mais longo (1:20) pra acomodar o notebook de utilização.

### 6.1 LGPD em ação na UI (45s)

**O que mostrar:** voltar pra Tab 💬 Consulta livre, ainda com a paciente Maria selecionada

**Ação:** Digitar no chat:
```
Quais registros de violência essa paciente tem?
```
Aguardar resposta — o agente deve pedir motivo clínico ou recusar. Depois, mostrar uma célula do notebook que consulta `log_acesso`:

```python
conn.execute('SELECT * FROM log_acesso ORDER BY id DESC LIMIT 5').fetchall()
```

**Narração:**
> "Importante mostrar a camada de privacidade. Pedi ao agente o histórico de violência. A tool `consultar_violencia` exige motivo clínico mínimo de cinco caracteres — sem isso, retorna erro. Quando atende, registra automaticamente em `log_acesso` com timestamp, usuário, tabela, paciente, motivo."

> "O system prompt do agente codifica os limites do enunciado: nunca prescreve, nunca diagnostica definitivamente, sempre encaminha suspeitas de violência, sempre sugere consulta presencial para sintomas alarmantes."

### 6.2 Relatório gerencial — notebook 10 (45s)

**O que mostrar:** abrir `10_relatorio_utilizacao.ipynb` no VSCode (ou em aba do Colab se tiver com Drive ativo). Rodar as células 4 (cobertura preventiva), 5 (auditoria LGPD) e 7 (resumo executivo).

**Narração:**
> "Pra fechar a camada de governança, o notebook 10 gera o relatório gerencial atendendo o item 'relatórios de utilização por especialidade' do enunciado."

> "Aqui: cobertura de rastreamento populacional — quanto da população elegível está em dia com papanicolau e mamografia, seguindo os intervalos do Ministério. Indicador direto de qualidade do serviço."

> "Aqui: auditoria LGPD agregada — acessos por usuário e por tabela. Dá pra ver quem acessou o quê e quando, sem expor o conteúdo individual dos registros."

> "Aqui: indicadores epidemiológicos de violência — distribuição por tipo, percentual de notificação SINAN, encaminhamentos mais comuns. Insumo pra dimensionamento de equipe especializada."

---

## Bloco 7 — Encerramento (13:00 – 14:20)

**O que mostrar:** README.md seção "Limitações" + URL do repositório GitHub

**Roteiro falado:**
> "Resumindo: fine-tuning ponta a ponta, RAG sobre protocolos brasileiros, nove ferramentas estruturadas, quatro fluxos LangGraph explícitos, UI Gradio com cinco tabs, quatro templates de documentos clínicos, relatório gerencial de utilização, e auditoria LGPD funcional. Atende os quatro requisitos técnicos da Fase 3."

> "Limitações reconhecidas no relatório: validação clínica formal pendente, anonimização de dados reais não implementada como pipeline, criptografia at-rest ausente, sem análise quantitativa de disparidade por subgrupo demográfico. Tudo documentado."

> "Sobre o item de validação da resposta pelo LLM antes do retorno: a leitura literal — um segundo passe do LLM revisando a saída do primeiro — foi avaliada e descartada por custo de latência. Os workflows já respondem entre cinco e quinze segundos no fine-tuned, que é mais verboso que o base. Dobrar isso num cenário clínico onde triagem e avaliação obstétrica precisam ser quase instantâneas era inaceitável. Em vez disso, a função de validação foi distribuída em mecanismos determinísticos sem custo de latência: system prompt com regras de não-prescrição e não-diagnóstico, edges condicionais que forçam encaminhamento em emergências, matriz determinística que ativa o protocolo SINAN independente do texto gerado, e o estado estruturado com raciocínio, fontes e confiança que permite revisão a posteriori pelo profissional. Está justificado na seção 4.5 do relatório técnico."

> "Repositório no GitHub: [link]. Relatório técnico, roteiro e arquitetura no repo. Obrigado."

---

## Checklist de gravação

### Antes de gravar

- [ ] **App Gradio rodando** com `share=True` ativo, link público copiado
- [ ] **Paciente já testada na UI** — verificar que tem mamografia atrasada + algum registro prévio (idealmente mesma paciente serve nas tabs Sidebar, Prevenção e LGPD)
- [ ] **Smoke test dos 4 workflows** na UI — cada tab respondendo em <30s sem travar
- [ ] Notebooks 02, 03 e `eval_sidebyside.md` abertos em abas separadas no VSCode
- [ ] VSCode tema escuro + zoom 150% pra legibilidade
- [ ] Browser com a URL do Gradio em aba dedicada (sem dock/marcadores poluindo)
- [ ] Microfone testado (gravar 30s de teste, ouvir)
- [ ] Notificações silenciadas (Slack, Teams, e-mail, WhatsApp web)
- [ ] Resolução de tela 1920x1080
- [ ] Mouse Highlighter ativado (ou cursor grande)

### Durante a gravação

- [ ] Falar pausado — palavras técnicas pedem clareza
- [ ] Para cada bloco, gravar do início ao fim sem cortar; se errar grosseiro, refazer só o bloco
- [ ] **Não rodar treino ou eval ao vivo** — usar outputs já gerados/cacheados
- [ ] Workflows da UI: aceitar latência (5-10s de inferência) — comentar enquanto carrega ("o LLM agora está processando a queixa, extraindo sintomas via JSON estruturado...")

### Pós-edição (mínima — engenharia não pede produção)

- [ ] Cortar gaps de silêncio >3s
- [ ] Título no canto: "FIAP Tech Challenge — Fase 3 — Assistente Clínico Saúde da Mulher"
- [ ] Cartelas de 1s entre blocos (opcional): "1. Arquitetura", "2. Fine-tuning", "3. Demo UI", "4. LGPD"
- [ ] Conferir duração final ≤15min
- [ ] Exportar 1080p MP4, ≤500MB
- [ ] Upload no YouTube (não-listado) ou Google Drive — colocar link no README

---

## Plano B — Se algo travar na gravação

| Problema | Fallback |
|---|---|
| Colab desconecta antes de gravar | Re-rodar `08_app_gradio.ipynb` (10 min) ou usar print/JSON dos workflows de execuções anteriores |
| Workflow demora >30s na UI | Comentar a latência como "o modelo executa cada node do StateGraph sequencialmente, vai chamar RAG agora..."; se travar mesmo, mostrar o output equivalente no `09_demo_workflows.ipynb` que já está cacheado |
| Workflow retorna texto degenerado | `repetition_penalty` já foi ajustado; se ainda assim sair feio, mencionar como ponto de melhoria honesto |
| SINAN não registra (paciente sem id) | Selecionar uma paciente válida na sidebar antes; ou aceitar e narrar "aqui o fluxo identifica corretamente que não há registro formal possível sem confirmação clínica" |
| Áudio ruim na primeira tomada | Re-gravar só o áudio com slides estáticos do README/relatório de fundo |

---

## Material complementar a anexar na entrega

Junto com o vídeo:

- Link do repositório GitHub (commit final da terça)
- `README.md` (overview + estrutura)
- `RELATORIO_TECNICO.md` (executivo, ~3 páginas) + `RELATORIO_TECNICO_DETALHADO.md` (com números do `eval_report.json` preenchidos)
- `ARQUITETURA.md` (decisões técnicas detalhadas)
- `ROTEIRO_VIDEO.md` (este arquivo, mostra o planejamento)
- Print da estrutura `/MyDrive/AssistenteHospitalar/files/finetune/` mostrando o adapter persistido
- Print do log de execução do `04_avaliar_modelo.ipynb` mostrando as métricas
