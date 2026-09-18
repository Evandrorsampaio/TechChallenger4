# Diagramas de Sequência

**Agente responsável:** `ArchitectureAgent`
**Status:** As sequências 1 a 4 descrevem comportamento **projetado**. A sequência 5 descreve o
fluxo **existente**, derivado de `lib/ui.py`, `lib/agent.py` e `lib/tools.py`.
**Convenção:** participantes com sufixo `*` são componentes novos.

---

## Índice

| # | Sequência | Status |
|---|---|---|
| 1 | Predição completa de risco gestacional, ponta a ponta | projetado |
| 2 | Dados incompletos → human-in-the-loop | projetado |
| 3 | Emergência obstétrica com bypass do ML | projetado |
| 4 | Treinamento de modelo | projetado |
| 5 | Consulta livre com agente ReAct e tool calling | **existente** |

---

## 1. Predição completa de risco gestacional, ponta a ponta

```mermaid
sequenceDiagram
    autonumber
    actor P as Profissional
    participant UI as ui.py<br/>(aba ML)
    participant WF as risco_ml.py*
    participant SC as ml/schema.py*
    participant RG as SINAIS_ALARME_OBST
    participant PR as ml/predict.py*
    participant RY as ml/registry.py*
    participant EX as ml/explain.py*
    participant RA as common.rag_search
    participant CT as ml/llm_contract.py*
    participant LM as llm.py<br/>(chat_model)
    participant VA as validacao.py*
    participant DB as SQLite<br/>predicoes_ml*

    P->>UI: preenche formulário e submete
    UI->>WF: invoke({dados_clinicos, paciente_id, usuario})

    rect rgb(254, 243, 199)
    note over WF,SC: validar_dados
    WF->>SC: GestanteFeatures(**dados)
    SC->>SC: domínios · extra='forbid'
    SC->>SC: partos+abortos ≤ gestacoes
    SC->>SC: pad_mmhg < pas_mmhg
    SC-->>WF: features válidas (frozen)
    end

    rect rgb(254, 226, 226)
    note over WF,RG: regras_seguranca — PRECEDE o ML (ADR-006)
    WF->>RG: avaliar sinais de alarme
    RG-->>WF: regras_disparadas = []
    end

    rect rgb(224, 242, 254)
    note over WF,EX: executar_modelo_ml + gerar_explicabilidade
    WF->>PR: prever(features)
    PR->>RY: carregar()
    RY->>RY: verifica MAJOR de dataset_version
    RY-->>PR: (pipeline, model_card)
    PR->>PR: DataFrame 1 linha
    PR->>PR: imputa opcionais → dados_imputados
    PR->>PR: predict_proba
    PR->>PR: rótulo = p ≥ model_card.threshold
    PR->>PR: features_hash = SHA-256
    PR-->>WF: ResultadoPredicao
    WF->>EX: explicar(pipeline, linha, nomes)
    alt shap disponível e modelo é de árvores
        EX->>EX: TreeExplainer — local, exato
    else modelo linear
        EX->>EX: coef × valor padronizado — local
    else
        EX->>EX: permutation_importance — GLOBAL + aviso
    end
    EX-->>WF: ResultadoExplicacao(metodo, escopo, top_features)
    end

    WF->>RA: rag_search(retriever, query, 'ginecologia_obstetricia', k=3)
    RA-->>WF: [{trecho, doc_id, category, chunk_id}, ...]

    rect rgb(224, 242, 254)
    note over WF,VA: síntese sob contrato somente-leitura (ADR-007)
    WF->>CT: montar_payload(predicao, explicacao, fontes, regras)
    CT-->>WF: payload §5.2 (12 campos)
    WF->>LM: invoke(prompt com payload)
    LM-->>WF: texto clínico
    WF->>VA: verificar(texto, payload)
    VA->>VA: extrai numerais do texto
    VA->>VA: confere contra o payload (tolerância)
    VA->>VA: checa contradição de rótulo
    VA->>VA: regras clínicas do ValidadorDeterministico
    VA-->>WF: aprovada = True
    end

    WF->>WF: aplicar_avisos_seguranca<br/>safety_notice + aviso_dados_sinteticos

    rect rgb(220, 252, 231)
    note over WF,DB: auditar — obrigatório antes da resposta
    WF->>DB: INSERT predicoes_ml (modo='normal', features_hash, ...)
    DB-->>WF: id
    end

    WF-->>UI: resposta_estruturada
    UI->>UI: _render_risco_ml
    UI-->>P: rótulo · probabilidade · limiar ·<br/>fatores + método · imputados ·<br/>fontes · avisos
```

### Três ordens que não podem ser trocadas

| Ordem | Consequência de inverter |
|---|---|
| `regras_seguranca` **antes** de `executar_modelo_ml` | Uma probabilidade baixa poderia rebaixar um sinal de emergência (ADR-006) |
| Verificação **depois** da geração | Prompt não é controle; sem verificação posterior não há garantia |
| `auditar` **antes** de responder | Falha de renderização apagaria o rastro da decisão |

---

## 2. Dados incompletos → human-in-the-loop

```mermaid
sequenceDiagram
    autonumber
    actor P as Profissional
    participant UI as ui.py
    participant WF as risco_ml.py*
    participant SC as ml/schema.py*
    participant HDB as hospital.db
    participant PR as ml/predict.py*
    participant DB as predicoes_ml*

    P->>UI: seleciona paciente na sidebar<br/>e pede predição
    UI->>WF: invoke({paciente_id: 17, usuario})

    WF->>SC: features_de_paciente(conn, 17)
    SC->>HDB: SELECT prontuário e exames
    HDB-->>SC: idade, g_p_a, dum, ...
    note over SC,HDB: hospital.db NÃO tem PA, IMC<br/>nem comorbidades estruturadas
    SC-->>WF: (dados_parciais, campos_ausentes)

    rect rgb(254, 243, 199)
    note over WF,SC: validar_dados
    WF->>SC: GestanteFeatures(**dados_parciais)
    SC--xWF: DadosIncompletosError<br/>['pas_mmhg','pad_mmhg','imc_pre_gestacional']
    end

    WF->>WF: rota → dados_incompletos<br/>(≠ erro_validacao)
    WF->>WF: solicitar_complemento<br/>campos + significado clínico + faixa

    WF-xPR: NÃO chamado
    note right of PR: nenhuma imputação de campo obrigatório<br/>nenhuma probabilidade produzida

    WF->>WF: aplicar_avisos_seguranca
    rect rgb(220, 252, 231)
    WF->>DB: INSERT (modo='incompleto', predicao=null-equivalente)
    DB-->>WF: id
    end

    WF-->>UI: resposta com campos faltantes
    UI-->>P: formulário com 3 campos destacados<br/>"predição NÃO realizada"

    P->>UI: completa PA e IMC
    UI->>WF: nova invocação (Sequência 1)
```

### Por que o registro de auditoria acontece mesmo sem predição

Porque "houve uma tentativa e ela foi recusada" é informação de auditoria. Sem esse registro, a
taxa de dados incompletos — que é uma métrica de qualidade do processo assistencial, não do
modelo — seria invisível.

### Nota sobre human-in-the-loop sem estado

O ciclo de volta é feito pela UI: o workflow **termina**, o profissional completa, e uma nova
invocação começa. Não há `interrupt` nem `checkpointer` do LangGraph — nenhum workflow atual tem,
e introduzir persistência de estado seria escopo maior do que o problema exige.

---

## 3. Emergência obstétrica com bypass do ML

```mermaid
sequenceDiagram
    autonumber
    actor P as Profissional
    participant UI as ui.py
    participant WF as risco_ml.py*
    participant SC as ml/schema.py*
    participant RG as SINAIS_ALARME_OBST
    participant PR as ml/predict.py*
    participant EX as ml/explain.py*
    participant RA as common.rag_search
    participant CT as ml/llm_contract.py*
    participant LM as chat_model
    participant VA as validacao.py*
    participant DB as predicoes_ml*

    P->>UI: "Gestante 34a, IG 32s, cefaleia intensa,<br/>escotomas, epigastralgia em barra"
    UI->>WF: invoke(...)

    WF->>SC: GestanteFeatures(**dados)
    SC-->>WF: válido

    rect rgb(254, 226, 226)
    note over WF,RG: regras_seguranca
    WF->>RG: casar sinais na descrição
    RG-->>WF: 3 sinais:<br/>cefaleia · escotomas · epigastralgia
    WF->>WF: rota → bypass_ml
    end

    WF-xPR: NÃO consultado
    WF-xEX: NÃO consultado
    note right of PR: não há probabilidade a ser ignorada —<br/>ela nunca é produzida

    WF->>WF: bypass_ml<br/>encaminhamento IMEDIATO ao PS obstétrico

    WF->>RA: rag_search('pré-eclâmpsia grave conduta imediata')
    RA-->>WF: trechos do protocolo

    WF->>CT: montar_payload PARCIAL<br/>sem probabilities · sem top_features<br/>regras_disparadas preenchido
    CT-->>WF: payload
    WF->>LM: invoke(prompt de conduta)
    LM-->>WF: texto
    WF->>VA: verificar(texto, payload)
    note over VA: sem números no payload ⇒<br/>QUALQUER numeral no texto é órfão
    VA-->>WF: aprovada / reprovada

    WF->>WF: aplicar_avisos_seguranca
    rect rgb(220, 252, 231)
    WF->>DB: INSERT (modo='bypass_regra', regras_disparadas=[3 sinais])
    end

    WF-->>UI: resposta
    UI-->>P: 🚨 ENCAMINHAMENTO IMEDIATO<br/>+ sinais detectados<br/>+ "modelo de ML NÃO foi consultado:<br/>regra de segurança determinística"
```

### Observação sobre a verificação neste caminho

Como o payload parcial não contém `probabilities` nem `threshold`, a regra 1 da verificação fica
mais restritiva por consequência natural: **qualquer** numeral no texto é órfão. Isso é desejável
— num encaminhamento de emergência, o LLM não tem número legítimo a citar além do que vier
textualmente do protocolo recuperado. Se a prática mostrar rejeições espúrias por causa de
números presentes no trecho do protocolo (doses, prazos), a tolerância precisará considerar
também os numerais de `retrieved_sources`. Registrado como ponto a validar em
`docs/llm/POLITICA_ANTI_ALUCINACAO.md`.

### Contraste com o obstétrico existente

Em `obstetrico.py`, `_detectar_alertas_urgencia` roda **depois** de `_avaliar_risco_gestacional` e
não desvia o fluxo — apenas marca `eh_emergencia`, lida adiante por dois nós. Aqui, a regra vem
antes e **desvia**.

---

## 4. Treinamento de modelo

```mermaid
sequenceDiagram
    autonumber
    actor D as Desenvolvedor
    participant SH as scripts/train.py*
    participant CF as config.py*
    participant DS as ml/dataset.py*
    participant FS as sistema de arquivos
    participant FE as ml/features.py*
    participant SK as scikit-learn
    participant EV as ml/evaluate.py*
    participant RY as ml/registry.py*

    D->>SH: python scripts/train.py
    SH->>CF: resolver ARTIFACTS_PATH, RANDOM_SEED
    CF-->>SH: caminhos + seed=42

    SH->>DS: garantir_dataset()
    DS->>FS: Parquet existe?
    alt não existe
        DS->>DS: default_rng(42) → 8000 registros
        DS->>FS: escreve Parquet
        DS->>FS: escreve manifest.json (SHA-256)
    else existe
        DS->>FS: lê Parquet
        DS->>DS: recomputa SHA-256
        DS->>FS: lê manifest.json
        alt hash diverge
            DS--xSH: DatasetDivergenteError
            SH-->>D: ERRO — treino interrompido
        end
    end
    DS->>DS: REMOVE risco_latente, registro_id,<br/>dataset_version, split
    DS-->>SH: X, y

    SH->>SK: train_test_split estratificado 70/15/15, seed=42
    SK-->>SH: treino · validação · teste
    SH->>SH: registra hash do split

    loop para cada candidato
        SH->>FE: construir ColumnTransformer
        FE-->>SH: transformador não ajustado
        SH->>SK: Pipeline(transformador, estimador, class_weight='balanced')
        alt LogReg ou RandomForest
            SH->>SK: GridSearchCV(StratifiedKFold(5), 'average_precision')
            note right of SK: fit APENAS no treino —<br/>impede vazamento pelo escalonador
            SK-->>SH: melhor estimador
        else Dummy ou baseline determinístico
            SH->>SK: fit direto (sem busca)
        end
    end

    rect rgb(220, 252, 231)
    note over SH,SK: seleção de limiar — na VALIDAÇÃO
    SH->>SK: predict_proba(validacao)
    SH->>SH: menor limiar com recall ≥ 0.90
    SH->>SH: registra precisão resultante
    end

    rect rgb(254, 243, 199)
    note over SH,EV: TESTE — aberto uma única vez
    SH->>SK: predict_proba(teste)
    SH->>EV: avaliar(y_teste, probas, limiar)
    EV->>EV: confusão · P/R/F1 por classe e macro
    EV->>EV: ROC-AUC · PR-AUC · Brier · calibração
    EV->>EV: especificidade · NPV
    EV->>EV: bootstrap 1000× → IC
    EV->>EV: análise de erros: perfil dos FN e FP
    EV->>FS: artifacts/metrics/*.json + curvas
    end

    SH->>RY: salvar(pipeline, model_card)
    RY->>FS: *.joblib
    RY->>FS: model_card.json<br/>(nome, versão, dataset_version, threshold, hiperparâmetros)
    RY-->>SH: ok
    SH-->>D: resumo + caminhos dos artefatos
```

### Duas guardas que o diagrama torna explícitas

1. **`DatasetDivergenteError` interrompe o treino.** Não é aviso. Treinar sobre um dataset que
   não corresponde ao manifesto produziria métricas não reproduzíveis — exatamente o que a
   ADR-011 existe para impedir.
2. **O bloco do teste aparece uma única vez, no fim.** Se em alguma iteração futura aparecer uma
   seta de `teste` de volta para `seleção de limiar` ou para `GridSearchCV`, há vazamento.

---

## 5. Consulta livre com agente ReAct e tool calling  **(fluxo existente)**

Derivado de `lib/ui.py::on_chat`, `lib/agent.py::run_consulta` e `lib/tools.py`.

```mermaid
sequenceDiagram
    autonumber
    actor P as Profissional
    participant UI as ui.py::on_chat
    participant AG as agent.py::run_consulta
    participant RE as create_react_agent<br/>(LangGraph)
    participant LM as ChatHuggingFace<br/>Llama 3.2 3B + LoRA
    participant TL as StructuredTool
    participant DB as hospital.db
    participant CH as Chroma
    participant LG as log_acesso

    P->>UI: "Paciente tem exames em atraso?<br/>Qual a conduta?"
    UI->>UI: mensagem vazia? não
    UI->>AG: run_consulta(agent, pergunta,<br/>paciente_id=7, historico)

    alt paciente_id informado
        AG->>AG: prefixa "[Contexto: paciente_id=7]"
    end
    AG->>AG: historico + HumanMessage
    AG->>RE: invoke({messages}, recursion_limit=12)

    RE->>LM: mensagens + SYSTEM_PROMPT + tools vinculadas
    LM-->>RE: tool_call: exames_atrasados(paciente_id=7)
    RE->>TL: exames_atrasados
    TL->>DB: SELECT data_nascimento / exames<br/>(SQL parametrizado)
    DB-->>TL: linhas
    TL->>TL: alertas.exames_atrasados<br/>(regra determinística)
    TL-->>RE: ToolMessage com a lista

    RE->>LM: mensagens + resultado da tool
    LM-->>RE: tool_call: buscar_protocolo(query='rastreamento ...')
    note right of TL: única tool SEM args_schema —<br/>assinatura inferida pelo LangChain
    RE->>TL: buscar_protocolo
    TL->>CH: retriever.invoke(query)
    CH-->>TL: Documents
    TL->>TL: filtra categoria em pós-processamento<br/>corta em k=4
    TL-->>RE: [{trecho, doc_id, category, chunk_id}]

    RE->>LM: mensagens + trechos do protocolo
    LM-->>RE: resposta final em texto
    RE-->>AG: estado com todas as mensagens

    AG->>AG: percorre mensagens casando<br/>tool_call.id ↔ ToolMessage.tool_call_id
    AG-->>UI: {resposta, tool_calls, mensagens}

    UI->>UI: anexa bloco &lt;details&gt;<br/>"🔧 Ferramentas usadas"
    UI->>UI: historico_estado['mensagens'] = mensagens
    UI-->>P: Chatbot renderiza

    opt se a tool fosse consultar_violencia
        TL->>TL: motivo tem ≥ 5 caracteres?
        TL->>LG: INSERT (usuario, tabela, paciente_id, motivo)
        note right of LG: usuario vem de _USUARIO_ATUAL —<br/>global de módulo, não de sessão
    end
```

### O que este diagrama revela sobre o desenho atual

| Observação | Implicação |
|---|---|
| Não há participante de tratamento de erro | Exceção em qualquer ponto sobe até o Gradio |
| `historico_estado` é escrito no fim | Duas sessões concorrentes sobrescrevem o histórico uma da outra |
| `_USUARIO_ATUAL` é global de módulo | Auditoria de LGPD pode registrar o profissional errado sob concorrência |
| `buscar_protocolo` sem `args_schema` | Ponto mais frágil do tool calling num modelo de 3B |
| Nenhuma escrita em auditoria, exceto violência | A consulta em si não deixa rastro |

Nenhum desses pontos será alterado (ADR-001). Estão documentados para que a decisão de não mexer
seja deliberada.

### Onde a evolução entra

Num único ponto: a lista de tools passa a ter 10 itens. Se o modelo escolher
`predizer_risco_gestacional`, a sequência ganha uma chamada a `ml/predict.py` e um `INSERT` em
`predicoes_ml`. Caso contrário, é idêntica à atual.

---

## Comparação das cinco sequências

| Dimensão | 1 Normal | 2 Incompleto | 3 Bypass | 4 Treino | 5 ReAct |
|---|---|---|---|---|---|
| Participantes | 12 | 6 | 11 | 7 | 8 |
| Chama o LLM | sim | **não** | sim | **não** | sim |
| Chama o modelo de ML | sim | **não** | **não** | treina | só se a tool for escolhida |
| Escreve auditoria | sim | sim | sim | não | só tools de violência |
| Requer GPU | só no perfil `full-gpu` | não | só no `full-gpu` | **não** | sim |
| Executável em CI | sim (`demo-cpu`) | sim | sim | **sim** | não |

A penúltima linha é a que sustenta a ADR-005: quatro das cinco sequências são verificáveis sem
GPU. É por isso que "Dockerfile testado" pode deixar de ser afirmação e virar evidência — desde
que o log de `docker build` e `docker run` seja anexado em `docs/deploy/EXECUCAO_DOCKER.md`.
