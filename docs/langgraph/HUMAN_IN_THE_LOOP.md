# Human-in-the-Loop

**Agente responsável:** `LangGraphAgent`
**Status:** Especificação. O único gate humano **existente** é o checkbox `confirmacao_clinica` do
fluxo de violência (`[COD]`). Tudo o mais é projeto.
**Vinculado a:** `WORKFLOW_ML.md` · `ESTADOS_E_TRANSICOES.md` · `TRATAMENTO_DE_ERROS.md` ·
`ARQUITETURA_ALVO.md` §4 · ADR-006

---

> ### Banner de estado
> Nenhum workflow usa `interrupt`, `checkpointer` ou qualquer mecanismo formal de HIL do LangGraph
> (`00_INVENTARIO_PROJETO.md` §6, achado 5). Nada do que é especificado aqui está implementado.

---

## 1. O que existe hoje `[COD]`

Um gate, no fluxo de violência.

### 1.1 O mecanismo

```python
# lib/ui.py:384-396
def on_wf_violencia(descricao, paciente_id, confirmacao):
    ...
    state = wf_violencia.invoke({
        'descricao_caso': descricao,
        'paciente_id': paciente_id,
        'profissional': prof,
        'confirmacao_clinica': bool(confirmacao),
    })
    return _render_violencia_wf(state)
```

```python
# lib/ui.py:523-527 — o controle
gr.Checkbox(
    label='Confirmação clínica (autoriza registro SINAN no DB)',
    value=False,
)
```

```python
# lib/workflows/violencia.py:142-145 — o efeito
def _documentar_seguro(state, conn):
    nivel = state.get('nivel', 'sem_alerta')
    deve_registrar = (nivel == 'alta_suspeita'
                      and state.get('confirmacao_clinica', False))
```

O registro em `registros_violencia` e a notificação SINAN só ocorrem com **três** condições
simultâneas: `nivel == 'alta_suspeita'`, `confirmacao_clinica is True` e `paciente_id` presente.

### 1.2 O que esse desenho acerta

| Acerto | Por quê |
|---|---|
| Gate **antes** do efeito colateral irreversível | Notificação SINAN é ato formal; não deve decorrer de inferência de um LLM de 3B |
| Default `False` | Omissão não autoriza. O modo de falha seguro é não registrar |
| Ausência de autorização é **declarada** | `ui.py:182-183` mostra "não foi gerado registro formal — fazer notificação em ficha física" |
| Registra na auditoria quem autorizou | `tools_mod.set_usuario_atual(profissional)` antes do `INSERT` |

### 1.3 O que esse desenho não faz

| Limitação | Efeito |
|---|---|
| A confirmação é dada **antes** de ver o resultado | O profissional marca o checkbox sem saber ainda qual será o `nivel`. Autoriza no escuro |
| Não há pausa: o grafo roda até o fim numa invocação | Não é HIL no sentido de interromper e retomar; é um parâmetro de entrada |
| Não há registro do que foi apresentado ao humano no momento da decisão | A auditoria grava o registro, não o contexto da autorização |
| Não há como o humano **discordar** do resultado e registrar isso | Só pode autorizar ou não autorizar |

A primeira limitação é a mais séria e define o padrão a não repetir: **um gate que pede autorização
antes de mostrar o que está sendo autorizado é um gate fraco.**

---

## 2. Princípios do HIL neste sistema

| # | Princípio | Consequência |
|---|---|---|
| **H-1** | O humano decide, o sistema apoia | Nenhum ponto de HIL pede ao humano que "confirme se o modelo está certo" — pede uma decisão clínica |
| **H-2** | O humano vê antes de decidir | O contexto da decisão é apresentado **junto** com o pedido, não antes dele |
| **H-3** | Não decidir é uma opção, e é o default seguro | A ausência de decisão nunca autoriza uma ação irreversível |
| **H-4** | Nem todo HIL é uma pergunta | Em emergência, o humano é **informado**, não consultado (ADR-006) |
| **H-5** | Toda decisão humana entra na auditoria | Quem, quando, o que foi apresentado, o que foi decidido |
| **H-6** | Interromper tem custo | Um sistema que pergunta demais é ignorado. Cada ponto de HIL precisa justificar a fricção |

H-6 é o que impede a proliferação de pontos de parada. Cada um dos cinco pontos de §3 precisa
responder: *o que aconteceria de ruim se o sistema decidisse sozinho aqui?*

---

## 3. Os cinco pontos de HIL do workflow novo

### 3.1 HIL-1 — Dados obrigatórios incompletos

| Aspecto | Definição |
|---|---|
| **Gatilho** | `campos_faltantes != []` em `validar_dados` → nó `dados_incompletos` |
| **Tipo** | Bloqueante. **O sistema não prediz** |
| **O que é apresentado** | Lista dos campos faltantes com nome clínico, unidade, faixa aceita e onde obter (aferição, exame, anamnese). Mais o que **já** foi informado, para o profissional não reinserir |
| **O que o humano decide** | Completar os campos, ou abandonar a avaliação |
| **Opção de "não sei"** | **Sim, e é essencial.** Campo obrigatório sem valor mantém o bloqueio. Não há "seguir mesmo assim" |
| **Registro na auditoria** | `modo='incompleto'`, `features_hash` dos dados parciais, `probabilidade=NULL`, `usuario` |
| **Por que não decidir sozinho** | Imputar campo obrigatório é o "silêncio perigoso" proibido por `CONTRATO_DE_DADOS.md` §5. Uma PA imputada pela mediana populacional produziria predição com aparência normal sobre dado inventado |

**Frequência esperada: alta.** Das 11 features obrigatórias, 5 são extraíveis de `hospital.db`
(`DICIONARIO_DE_DADOS.md` §9.4). Toda invocação a partir do prontuário chega aqui. O formulário de
complemento **é** a interface principal do fluxo, não uma tela de exceção — o que muda a prioridade
de implementação dela.

### 3.2 HIL-2 — Predição na banda de incerteza

| Aspecto | Definição |
|---|---|
| **Gatilho** | `abs(p_alto_risco - threshold) <= BANDA`, com `BANDA` constante versionada junto ao modelo |
| **Tipo** | **Não bloqueante.** A resposta é entregue; o pedido de confirmação acompanha |
| **O que é apresentado** | Probabilidade, limiar, distância entre os dois, fatores que pesaram, e a frase: "a probabilidade está próxima do limiar de decisão; pequena variação nos dados muda a classificação" |
| **O que o humano decide** | Aceitar a estratificação, ou sobrepô-la com justificativa |
| **Registro na auditoria** | A predição é auditada normalmente. A sobreposição, se houver, é **outra** linha, com `modo='normal'` e nota de sobreposição — ver §5 |
| **Por que não decidir sozinho** | Um limiar é um corte numa variável contínua. Tratar 0,309 e 0,311 como categorias diferentes, sem sinalizar a arbitrariedade, é apresentar precisão que não existe |

**O valor de `BANDA` não é definido aqui.** Ele depende da calibração medida do modelo escolhido, e
nenhum modelo foi treinado. Fixá-lo agora seria inventar parâmetro. Fica registrado como:
constante do `model_card.json`, definida em `docs/ml/METRICAS_E_RESULTADOS.md` a partir da curva de
calibração, **após** o treino.

### 3.3 HIL-3 — Bypass por emergência: informar, não perguntar

| Aspecto | Definição |
|---|---|
| **Gatilho** | `regras_disparadas != []` em `regras_seguranca` |
| **Tipo** | **Notificação. Não há pergunta.** |
| **O que é apresentado** | Sinal de alarme detectado, encaminhamento imediato, conduta de protocolo |
| **O que o humano decide** | Nada, no sistema. A decisão clínica é dele, fora do sistema, e é imediata |
| **Registro na auditoria** | `modo='bypass_regra'`, `regras_disparadas` preenchido, `probabilidade=NULL` |
| **Por que não perguntar** | ADR-006: regra determinística precede e anula o ML. Perguntar "deseja executar o modelo mesmo assim?" ofereceria ao usuário a chance de rebaixar um alarme de emergência com uma probabilidade — exatamente o que a decisão arquitetural proíbe |

Este ponto está no catálogo **porque a ausência de pergunta é a decisão de projeto**. Um leitor que
procurasse "onde está o HIL da emergência" precisa encontrar a resposta explícita: não há, e por
quê.

### 3.4 HIL-4 — Registro SINAN (já existente, preservado)

| Aspecto | Definição |
|---|---|
| **Gatilho** | `nivel == 'alta_suspeita'` no fluxo de violência |
| **Tipo** | Bloqueante para o efeito colateral. O restante da resposta é entregue |
| **O que é apresentado hoje** | Apenas o rótulo do checkbox, **antes** da avaliação (§1.3) |
| **O que deveria ser apresentado** | Nível de suspeita, score, sinais identificados, encaminhamentos — e só então o pedido de autorização |
| **O que o humano decide** | Autorizar ou não o registro formal e a notificação |
| **Registro na auditoria** | `registros_violencia` + `log_acesso` com `usuario` (`tools_mod.set_usuario_atual`) |
| **Escopo desta fase** | **Preservado como está.** `violencia.py` e `ui.py::on_wf_violencia` estão na lista "não tocar" (ADR-001) |

A melhoria — avaliar primeiro, autorizar depois, em duas interações — é registrada e **não
implementada**. Ela exigiria alterar o fluxo de violência, que é justamente o módulo com a decisão
ética mais sensível do projeto (ADR-002) e o que menos convém mexer sem necessidade.

### 3.5 HIL-5 — Modelo discorda da regra determinística

| Aspecto | Definição |
|---|---|
| **Gatilho** | `resultado_predicao.predicao == 'habitual'` **e** o baseline `CRITERIOS_ALTO_RISCO` classificaria como `alto_risco` (ou o inverso) |
| **Tipo** | **Não bloqueante.** Divergência é exibida junto com a resposta |
| **O que é apresentado** | As duas classificações lado a lado, com a origem de cada uma, os critérios que a regra atendeu e os fatores que o modelo ponderou |
| **O que o humano decide** | Qual estratificação adotar. O sistema **não escolhe** por ele neste caso |
| **Registro na auditoria** | A predição do modelo é auditada com `modo='normal'`; `regras_disparadas` recebe os critérios do baseline, tornando a divergência recuperável a posteriori |
| **Por que não decidir sozinho** | ADR-006 dá precedência à regra apenas para **regras de alarme de emergência** (`SINAIS_ALARME_OBST`), não para `CRITERIOS_ALTO_RISCO`, que é estratificação eletiva. Aplicar a mesma precedência aqui anularia o ML em todo caso com algum critério presente — e tornaria o modelo decorativo |

Este ponto é o que dá conteúdo real à comparação modelo × baseline de
`DEFINICAO_DO_PROBLEMA.md` §4: a discordância deixa de ser uma linha de tabela de métrica e passa a
ser um caso concreto na tela, com as duas justificativas visíveis.

**Exige avaliar o baseline em toda execução**, além do modelo. Custo desprezível — é uma disjunção
booleana sobre features já validadas — e é o mesmo `lib/ml/baseline.py` usado pelo
`modo_degradado` (`WORKFLOW_ML.md` §5.8).

### 3.6 Resumo

| ID | Gatilho | Bloqueia? | Humano decide o quê | Frequência esperada |
|---|---|---|---|---|
| HIL-1 | Campos obrigatórios ausentes | **Sim** | Completar os dados | **Alta** |
| HIL-2 | Probabilidade na banda do limiar | Não | Aceitar ou sobrepor | Baixa |
| HIL-3 | Sinal de alarme obstétrico | Não (informa) | Nada, no sistema | Baixa |
| HIL-4 | Alta suspeita de violência | Sim (para o registro) | Autorizar SINAN | Baixa |
| HIL-5 | Modelo × regra divergem | Não | Qual adotar | Média |

---

## 4. O mecanismo: `interrupt` + checkpointer, ou estado de intervenção?

### 4.1 O que o LangGraph oferece

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

def _solicitar_complemento(state):
    resposta = interrupt({'campos': state['campos_faltantes']})
    return {'dados_clinicos': {**state['dados_clinicos'], **resposta}}

grafo = g.compile(checkpointer=MemorySaver())
grafo.invoke(entrada, config={'configurable': {'thread_id': 'abc'}})
# ... pausa ...
grafo.invoke(Command(resume={'pas_mmhg': 130}), config={'configurable': {'thread_id': 'abc'}})
```

O `interrupt` pausa a execução no meio do nó; o checkpointer persiste o estado; a retomada continua
**de onde parou**, sem reexecutar os nós anteriores.

### 4.2 Por que isso é desconfortável com Gradio

| Atrito | Detalhe |
|---|---|
| **Modelo de requisição** | `ui.py` usa `btn.click(fn, inputs, outputs)`: cada clique é uma chamada síncrona que recebe widgets e devolve Markdown. Não há noção de "sessão de execução pendente" |
| **`thread_id`** | Precisaria ser criado, guardado em `gr.State` e devolvido ao cliente. Hoje não existe estado de sessão em `ui.py`; todos os handlers são funções puras dos widgets |
| **Ciclo de vida do checkpointer** | `MemorySaver` vive no processo. Reinício da célula do Colab perde todas as execuções pendentes. `SqliteSaver` resolveria, ao custo de mais uma tabela e mais um ciclo de vida a gerenciar |
| **Execuções órfãs** | Se o profissional fecha a aba com uma execução pausada, o checkpoint fica. Sem expiração, acumula estado clínico parcial indefinidamente — o que tem implicação de LGPD |
| **Concorrência** | Gradio serve múltiplos usuários. `thread_id` por usuário exigiria identidade de sessão, que hoje se resume a `tools_mod.get_usuario_atual()`, uma variável global de módulo |
| **Testabilidade** | Testar `interrupt` exige orquestrar duas invocações com checkpointer. Testar retorno de estado exige um `assert` |

A quinta linha é a mais séria: `_USUARIO_ATUAL` é global de módulo, não de sessão. Construir HIL com
retomada por `thread_id` sobre uma base sem identidade de sessão convidaria a um bug de
cruzamento de dados entre usuários — exatamente a categoria de bug que não se quer num sistema que
manipula prontuário.

### 4.3 A alternativa pragmática

Em vez de pausar, o grafo **completa** e devolve um estado que pede intervenção:

```python
{
    'requer_intervencao_humana': True,
    'intervencao': {
        'tipo': 'complementar_dados',
        'campos': [
            {'nome': 'pas_mmhg', 'rotulo': 'Pressão arterial sistólica',
             'unidade': 'mmHg', 'faixa': [80, 200], 'tipo': 'int'},
            {'nome': 'imc_pre_gestacional', 'rotulo': 'IMC pré-gestacional',
             'unidade': 'kg/m²', 'faixa': [15.0, 55.0], 'tipo': 'float'},
        ],
        'ja_informados': {'idade': 32, 'ig_semanas': 28},
        'pergunta': 'Complete os campos obrigatórios para que a estratificação seja calculada.',
    },
    'resposta_estruturada': {...},
    'modo': 'incompleto',
    'auditoria_id': 142,
}
```

A UI renderiza `intervencao` como formulário. Ao submeter, chama o grafo **de novo**, desde
`START`, com `dados_clinicos` mesclado.

### 4.4 Comparação

| Critério | `interrupt` + checkpointer | Retorno de estado |
|---|---|---|
| Reexecuta nós anteriores | Não | **Sim** |
| Exige `thread_id` e estado de sessão | **Sim** | Não |
| Funciona com o modelo de `ui.py` atual | Com reescrita | **Direto** |
| Estado clínico parcial persistido entre requisições | **Sim** — risco de LGPD | Não |
| Execuções órfãs | **Sim** | Não |
| Testabilidade | Duas invocações + checkpointer | Um `assert` |
| Auditoria da tentativa barrada | Só ao final, depois da retomada | **Imediata** — a tentativa já audita como `incompleto` |
| Adequado a HIL de longa duração (horas) | **Sim** | Não |

A penúltima linha é um ganho não óbvio do retorno de estado: **a tentativa barrada já é auditada**.
Com `interrupt`, o grafo não chegou a `auditar`, então uma execução abandonada não deixa rastro de
que houve uma tentativa de predizer sobre dados incompletos. Com retorno de estado, deixa.

A reexecução é barata no caminho relevante: HIL-1 dispara em `validar_dados`, o **segundo** nó. Não
há nada caro antes dele. Nenhum dos cinco pontos de HIL ocorre depois do LLM.

### 4.5 Decisão

| Ponto | Mecanismo nesta fase |
|---|---|
| HIL-1 | Retorno de estado (`requer_intervencao_humana`) |
| HIL-2 | Exibição junto com a resposta; nova invocação se houver sobreposição |
| HIL-3 | Notificação; sem interação |
| HIL-4 | Preservado como está (checkbox pré-invocação) |
| HIL-5 | Exibição junto com a resposta |

**`interrupt` + checkpointer fica fora do escopo desta fase.** Não por ser inferior em abstrato —
para HIL de longa duração, com humanos que respondem horas depois, ele é a solução correta — mas
porque nenhum dos cinco pontos tem essa natureza, e porque adotá-lo exigiria construir identidade
de sessão, ciclo de vida de checkpoint e expiração de estado clínico parcial. Três problemas novos
para resolver um que o retorno de estado resolve.

Registrado como **alternativa disponível**, não como dívida escondida. Se aparecer um ponto de HIL
assíncrono — aprovação por um segundo profissional, por exemplo — a decisão se reabre.

---

## 5. Registro da decisão humana na auditoria

### 5.1 O que precisa ser registrado

| # | Elemento | Por quê |
|---|---|---|
| A-1 | Quem decidiu | Responsabilização |
| A-2 | Quando | Correlação temporal |
| A-3 | O que foi apresentado | Uma decisão só é avaliável em função da informação disponível no momento |
| A-4 | O que foi decidido | O ato |
| A-5 | Justificativa, quando houver sobreposição | Distingue discordância clínica de erro de digitação |

### 5.2 O que a tabela atual comporta

`predicoes_ml` (`ARQUITETURA_ALVO.md` §5.3) tem `usuario` (A-1), `timestamp` (A-2),
`features_hash`, `predicao`, `modo` e `top_features` — que cobrem A-3 **parcialmente**: dá para
saber o que o modelo produziu, não o que a tela mostrou.

**Não há coluna para A-4 nem A-5.** Não há como registrar "o profissional sobrepôs a estratificação
para alto risco, justificando X".

### 5.3 A solução dentro do DDL publicado

Uma **segunda linha** em `predicoes_ml`, não uma coluna nova:

| Linha | `modo` | `predicao` | `features_hash` | Interpretação |
|---|---|---|---|---|
| 1ª | `normal` | `habitual` | `abc123…` | O modelo predisse habitual |
| 2ª | `normal` | `alto_risco` | `abc123…` | O humano sobrepôs para alto risco |

O `features_hash` idêntico amarra as duas: mesmas entradas, duas decisões, em ordem cronológica. A
segunda tem `probabilidade=NULL` (não houve nova inferência) e `regras_disparadas` com a
justificativa.

| Vantagem | Desvantagem |
|---|---|
| Não altera o DDL publicado | `regras_disparadas` passa a carregar algo que não é regra — impróprio semanticamente |
| Preserva a imutabilidade dos registros (sem `UPDATE`) | Uma consulta ingênua conta duas predições onde houve uma |
| A ordem cronológica é natural | Distinguir a sobreposição exige olhar o par, não a linha |

**A solução limpa seria `predicoes_ml.decisao_humana TEXT` e `justificativa TEXT`**, e ela é
registrada aqui como a alteração de DDL recomendada, a formalizar por ADR antes da implementação.
A solução de duas linhas é o contorno viável enquanto o DDL não muda — e o contorno tem defeito
declarado, que é o uso impróprio de `regras_disparadas`.

### 5.4 A-3 continua não coberto

Nenhuma das duas soluções registra **o que a tela mostrou**. Registrar isso exigiria persistir o
payload ou um hash dele, e o payload contém valores clínicos em claro — o que colide frontalmente
com a decisão de guardar apenas `features_hash` (`ARQUITETURA_ALVO.md` §5.3).

Meio-termo possível: persistir o **hash do payload** e o `auditoria_id`, permitindo provar que duas
decisões partiram da mesma apresentação, sem guardar o conteúdo. Não resolve A-3 plenamente —
prova identidade, não reconstrói a tela. Registrado como limitação.

---

## 6. Contrato do estado de intervenção

```python
# lib/workflows/risco_ml.py  — PROJETADO

TipoIntervencao = Literal[
    'complementar_dados',      # HIL-1
    'confirmar_banda',         # HIL-2
    'resolver_divergencia',    # HIL-5
]

class DescritorIntervencao(TypedDict):
    tipo:          TipoIntervencao
    pergunta:      str                  # texto para o profissional
    campos:        list[dict]           # HIL-1: nome, rotulo, unidade, faixa, tipo
    ja_informados: dict                 # o que não precisa ser reinserido
    opcoes:        list[dict]           # HIL-2/5: [{valor, rotulo, consequencia}]
    contexto:      dict                 # o que foi apresentado, para A-3
```

### 6.1 Obrigações da UI

| # | Obrigação |
|---|---|
| U-1 | `requer_intervencao_humana is True` ⟹ o formulário é a informação mais visível da tela |
| U-2 | `ja_informados` é exibido como leitura, não reinserido |
| U-3 | Cada campo mostra unidade e faixa aceita |
| U-4 | Existe um caminho de saída: "não é possível completar agora" encerra sem predição |
| U-5 | HIL-2 e HIL-5 exibem a **consequência** de cada opção, não só o rótulo |
| U-6 | A resposta parcial (avisos, protocolos, conduta genérica) é exibida junto, não substituída pelo formulário |

U-6 evita o pior comportamento possível: o profissional preenche seis campos e só então descobre
que o sistema não tinha nada útil a dizer.

### 6.2 O que a UI não deve fazer

| Proibido | Por quê |
|---|---|
| Preencher campo obrigatório com valor sugerido | Sugestão vira default aceito sem leitura |
| Oferecer "pular" que produza predição mesmo assim | Anula HIL-1 |
| Esconder a resposta parcial atrás do formulário | Ver U-6 |
| Reaproveitar o checkbox de violência para outro gate | Semânticas distintas colidiriam num só controle |

---

## 7. Testes de HIL exigidos

| ID | Cenário | Verifica | Arquivo planejado |
|---|---|---|---|
| HIL-T-01 | 6 obrigatórias ausentes | `requer_intervencao_humana is True`; `intervencao.campos` com os 6 | `tests/integration/test_hil_dados_incompletos.py` |
| HIL-T-02 | Reinvocação com dados completos | Predição ocorre; `modo='normal'`; **duas** linhas em `predicoes_ml` (a barrada e a efetiva) | idem |
| HIL-T-03 | Reinvocação ainda incompleta | Continua bloqueado; nova linha `incompleto` | idem |
| HIL-T-04 | Tentativa barrada é auditada | `modo='incompleto'`, `probabilidade IS NULL` | `tests/integration/test_auditoria_sempre.py` |
| HIL-T-05 | `p` dentro da banda | Resposta entregue **e** `intervencao.tipo == 'confirmar_banda'` | `tests/integration/test_hil_banda.py` |
| HIL-T-06 | `p` fora da banda | Sem pedido de intervenção | idem |
| HIL-T-07 | Emergência | `requer_intervencao_humana is False`; notificação presente | `tests/integration/test_hil_bypass.py` |
| HIL-T-08 | Modelo × baseline divergem | `intervencao.tipo == 'resolver_divergencia'`; as duas classificações na resposta | `tests/integration/test_hil_divergencia.py` |
| HIL-T-09 | Sobreposição humana | Segunda linha em `predicoes_ml` com o mesmo `features_hash` | idem |
| HIL-T-10 | Violência sem confirmação | Nenhum `INSERT` em `registros_violencia`; aviso de registro físico | `tests/regression/test_violencia_gate.py` |
| HIL-T-11 | Violência com confirmação | `INSERT` ocorre; `log_acesso` registra o usuário | idem |

HIL-T-10 e HIL-T-11 são **regressão**: verificam que o gate existente continua funcionando
exatamente como hoje. Estão aqui porque é o tipo de comportamento que se quebra por acidente ao
mexer em outra coisa.

---

## 8. O que fica fora do escopo

| Fora de escopo | Motivo |
|---|---|
| `interrupt` + checkpointer | §4.5 |
| HIL assíncrono (segundo profissional aprova depois) | Exige identidade de sessão e persistência de execução pendente |
| Fila de revisão de predições | Exige tabela de fila e política de expiração |
| Reescrita do gate de violência para duas etapas | `violencia.py` e `ui.py::on_wf_violencia` estão na lista "não tocar" (ADR-001). Melhoria registrada em §3.4 |
| Aprendizado a partir das sobreposições humanas | Retreino com rótulo humano exigiria pipeline de rotulagem e cuidado com viés de confirmação. Registrado como extensão futura |
| Colunas `decisao_humana` e `justificativa` em `predicoes_ml` | Alteração de DDL publicado; requer ADR (§5.3) |

A penúltima linha merece nota: usar as sobreposições como rótulo de retreino é tentador e seria
metodologicamente perigoso. O profissional que sobrepõe viu a predição do modelo antes de decidir;
treinar com esse rótulo ensinaria o modelo a prever suas próprias correções, não o desfecho
clínico.

---

## 9. Estado atual

| Item | Estado |
|---|---|
| `confirmacao_clinica` no fluxo de violência | `[COD]` — existe e funciona |
| `interrupt` ou checkpointer em qualquer workflow | **Nenhum** |
| `requer_intervencao_humana` / `intervencao` | **Não existem** |
| Formulário de complemento na UI | **Não existe** |
| Detecção de banda de incerteza | **Não existe** (e `BANDA` não pode ser definida antes do treino) |
| Detecção de divergência modelo × baseline | **Não existe** |
| Registro de decisão humana na auditoria | **Não existe** — contorno de duas linhas proposto em §5.3 |
| Testes HIL-T-01 a HIL-T-11 | **Nenhum** |
