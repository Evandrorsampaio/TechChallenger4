# Estados e Transições

**Agente responsável:** `LangGraphAgent`
**Status:** Descrição dos quatro estados **existentes** (`[COD]`, lidos de `lib/workflows/`) +
contrato completo do estado **projetado** `RiscoMLState`.
**Vinculado a:** `WORKFLOW_ML.md` · `docs/arquitetura/DIAGRAMA_LANGGRAPH.md`

---

> ### Banner de estado
> As tabelas dos §§2 a 4 descrevem código que existe e foi lido. A tabela do §5 descreve um
> `TypedDict` que **não existe**. Nenhuma transição do workflow novo foi executada.

---

## 1. Convenção comum aos cinco estados

Todos usam `TypedDict` com `total=False` e **nenhum redutor** (`Annotated[..., operator.add]`).
Os quatro existentes organizam os campos nos mesmos quatro grupos, em comentários:

```python
class XState(TypedDict, total=False):
    # Inputs
    # Intermediários
    # Explainability   →  raciocinio, fontes, confianca
    # Output           →  resposta_estruturada
```

A consistência é notável e vale preservar: `raciocinio`, `fontes`, `confianca` e
`resposta_estruturada` têm o mesmo nome e o mesmo papel nos quatro. É o que permite a
`lib/ui.py::_render_trace_e_fontes` ser uma função só, usada por todas as abas.

`RiscoMLState` mantém `raciocinio`, `fontes` e `resposta_estruturada` com a mesma semântica. Ele
**não** tem `confianca`: `estimar_confianca` é uma heurística de contagem de fontes
(`common.py:99-111`) e coexistir com uma probabilidade calibrada de modelo seria confuso — dois
números de "confiança" com origens incomparáveis na mesma tela. Quem cumpre esse papel é
`probabilities` e o limiar.

---

## 2. `TriagemState` — `lib/workflows/triagem.py` `[COD]`

| Campo | Tipo | Grupo | Escrito por |
|---|---|---|---|
| `queixa` | `str` | entrada | invocador |
| `paciente_id` | `int \| None` | entrada | invocador |
| `sintomas_extraidos` | `list[str]` | intermediário | `parse_sintomas` |
| `diferenciais` | `list[str]` | intermediário | `analisar_risco` |
| `sinais_alarme` | `list[str]` | intermediário | `classificar_urgencia` |
| `urgencia` | `str` | intermediário | `classificar_urgencia` |
| `justificativa_urgencia` | `str` | intermediário | `classificar_urgencia` |
| `exames_sugeridos` | `list[str]` | intermediário | `sugerir_exames` |
| `orientacoes_iniciais` | `str` | intermediário | `orientacoes_iniciais` |
| `agendamento` | `dict` | intermediário | `agendamento` |
| `raciocinio` | `list[str]` | trace | **todos os 7 nós** |
| `fontes` | `list[dict]` | trace | `analisar_risco`, `sugerir_exames` |
| `confianca` | `str` | trace | `compilar_resposta` |
| `resposta_estruturada` | `dict` | saída | `compilar_resposta` |

`urgencia ∈ {'emergencia','urgente','agendado','rotina'}`; `agendamento = {especialidade, prazo}`.

**Campo com dois escritores:** `fontes`. `analisar_risco` escreve; `sugerir_exames` reescreve com
`fontes_existentes + novas` (`triagem.py:171`). Funciona porque o segundo nó lê o valor atual antes
de sobrescrever — mesmo padrão manual de `raciocinio`. Ver §6.

---

## 3. `ViolenciaState` e `ObstetricoState` `[COD]`

### 3.1 `ViolenciaState` — `lib/workflows/violencia.py`

| Campo | Tipo | Grupo | Escrito por |
|---|---|---|---|
| `descricao_caso` | `str` | entrada | invocador |
| `paciente_id` | `int \| None` | entrada | invocador |
| `profissional` | `str` | entrada | invocador (UI: `tools_mod.get_usuario_atual()`) |
| `confirmacao_clinica` | `bool` | entrada | invocador (UI: checkbox) |
| `sinais_identificados` | `list[str]` | intermediário | `extrair_sinais` |
| `score` | `int` | intermediário | `avaliar_risco` |
| `nivel` | `str` | intermediário | `avaliar_risco` |
| `conduta_sugerida` | `str` | intermediário | `avaliar_risco` |
| `encaminhamentos` | `list[str]` | intermediário | `avaliar_risco` |
| `protocolo_seguranca_ativado` | `bool` | intermediário | `protocolo_seguranca` |
| `equipe_acionada` | `list[str]` | intermediário | `acionar_equipe` |
| `notificacao_sinan` | `bool` | intermediário | `documentar_seguro` |
| `registro_id` | `int \| None` | intermediário | `documentar_seguro` |
| `seguimento` | `dict` | intermediário | `definir_seguimento` |
| `raciocinio` | `list[str]` | trace | todos |
| `fontes` | `list[dict]` | trace | **ninguém** |
| `confianca` | `str` | trace | `compilar_resposta` |
| `resposta_estruturada` | `dict` | saída | `compilar_resposta` |

**`fontes` é declarado e nunca preenchido.** Este fluxo usa matriz determinística, não RAG;
`_compilar_resposta` chama `estimar_confianca(n_fontes=0, ...)` explicitamente
(`violencia.py:234`). Campo morto no estado, mantido por simetria com os outros três.

**Defeito confirmado — campo que deveria existir e não existe.** `_protocolo_seguranca`
(`violencia.py:105-119`) monta uma lista local `medidas` com seis itens de conduta:

```python
medidas = [
    'Conduzir atendimento em ambiente reservado, SEM acompanhante',
    'Garantir presença de profissional do mesmo gênero (preferencialmente)',
    'Aplicar perguntas-chave da Norma Técnica (...)',
    'Documentar achados em prontuário com linguagem objetiva e descritiva',
    'Avaliar segurança imediata: paciente pode voltar para casa em segurança?',
    'Avaliar risco para crianças/dependentes',
]
return {
    'protocolo_seguranca_ativado': True,
    'raciocinio': ...,
}
```

`medidas` **não está no dicionário de retorno** e não há campo `medidas_seguranca` em
`ViolenciaState`. Seis condutas clínicas de um caso de alta suspeita de violência são construídas e
descartadas a cada execução. Só a flag booleana chega à interface.

A correção é de duas linhas: acrescentar `medidas_seguranca: list[str]` ao `TypedDict` e
`'medidas_seguranca': medidas` ao retorno. **Não é feita nesta fase** porque `violencia.py` está na
lista "não tocar" de `ARQUITETURA_ALVO.md` §1 (ADR-001). Registrado em
`00_INVENTARIO_PROJETO.md` §6 achado 6, em `DIAGRAMA_LANGGRAPH.md` §2, e aqui.

Vale observar o que o defeito revela sobre o desenho: **um campo que não existe no `TypedDict` não
pode ser escrito por engano, mas também não protege contra o inverso** — construir o dado e
esquecer de devolvê-lo. Nem `TypedDict`, nem `total=False`, nem o LangGraph detectam isso. Só um
teste que asserisse o conteúdo do estado após o nó pegaria, e não há testes.

### 3.2 `ObstetricoState` — `lib/workflows/obstetrico.py`

| Campo | Tipo | Grupo | Escrito por |
|---|---|---|---|
| `descricao_caso` | `str` | entrada | invocador |
| `paciente_id` | `int \| None` | entrada | invocador |
| `ig_semanas` | `int \| None` | entrada **e** intermediário | invocador; sobrescrito por `coletar_dados_gestante` |
| `dados_gestante` | `dict` | intermediário | `coletar_dados_gestante` |
| `classificacao_risco` | `str` | intermediário | `avaliar_risco_gestacional` (**LLM**) |
| `fatores_risco_identificados` | `list[str]` | intermediário | `avaliar_risco_gestacional` |
| `alertas_urgencia` | `list[str]` | intermediário | `detectar_alertas_urgencia` |
| `eh_emergencia` | `bool` | intermediário | `detectar_alertas_urgencia` |
| `orientacoes_especificas` | `str` | intermediário | `orientacoes_especificas` |
| `exames_agendados` | `list[dict]` | intermediário | `agendar_exames` |
| `acompanhamento` | `dict` | intermediário | `definir_acompanhamento` |
| `raciocinio` | `list[str]` | trace | todos |
| `fontes` | `list[dict]` | trace | `orientacoes_especificas` |
| `confianca` | `str` | trace | `compilar_resposta` |
| `resposta_estruturada` | `dict` | saída | `compilar_resposta` |

**`ig_semanas` é entrada e intermediário ao mesmo tempo.** O invocador pode fornecê-lo
(`ui.py:405`); `coletar_dados_gestante` o sobrescreve com o valor extraído pelo LLM, usando o valor
do invocador como fallback (`obstetrico.py:109`). Funciona, mas o estado não distingue "informado
pelo profissional" de "extraído pelo LLM" — informação que teria valor clínico. `RiscoMLState`
evita isso separando `dados_clinicos` (bruto, imutável) de `features` (validado).

**`classificacao_risco` é o campo que o ML substitui** (ADR-002). No nó opcional de
`WORKFLOW_ML.md` §9, ele passa a ser escrito por `predizer_risco_ml`, acompanhado de
`classificacao_origem`.

---

## 4. `PrevencaoState` — `lib/workflows/prevencao.py` `[COD]`

| Campo | Tipo | Grupo | Escrito por |
|---|---|---|---|
| `paciente_id` | `int` | entrada | invocador |
| `perfil` | `dict` | intermediário | `carregar_historico` |
| `exames_historicos` | `list[dict]` | intermediário | `carregar_historico` |
| `exames_atrasados` | `list[dict]` | intermediário | `identificar_exames_devidos` |
| `exames_devidos` | `list[dict]` | intermediário | `identificar_exames_devidos` |
| `orientacoes_preventivas` | `str` | intermediário | `orientacoes_preventivas` |
| `agendamentos_propostos` | `list[dict]` | intermediário | `agendar_automaticamente` |
| `lembretes` | `list[dict]` | intermediário | `gerar_lembretes` |
| `raciocinio` | `list[str]` | trace | todos |
| `fontes` | `list[dict]` | trace | `orientacoes_preventivas` |
| `confianca` | `str` | trace | `compilar_resposta` |
| `resposta_estruturada` | `dict` | saída | `compilar_resposta` |

**`perfil` carrega um erro disfarçado de dado.** Sem `paciente_id`, `_carregar_historico` devolve
`{'perfil': {'erro': 'paciente_id obrigatório'}, ...}` (`prevencao.py:64-68`) e o fluxo **segue**.
Os nós seguintes tratam esse dicionário como perfil normal: `perfil.get('idade', 0)` devolve `0`, o
que faz as duas faixas etárias (`50 <= idade <= 69` e `25 <= idade <= 64`) não casarem, e a
execução termina com uma resposta vazia mas de aparência normal.

É o padrão exato que `TRATAMENTO_DE_ERROS.md` §3 classifica como **falha silenciosa** e que o
workflow novo não repete: no `RiscoMLState`, condição de erro tem campo próprio (`erros_validacao`,
`falhas`) e aresta própria.

---

## 5. `RiscoMLState` — contrato completo `[PROJ]`

Definição em `WORKFLOW_ML.md` §4. Aqui, o contrato por campo: quem escreve, quem lê, quando existe.

### 5.1 Entrada

| Campo | Tipo | Obrigatório | Escrito por | Lido por |
|---|---|---|---|---|
| `dados_clinicos` | `dict` | **sim** | invocador | `validar_dados` |
| `paciente_id` | `int \| None` | não | invocador | `auditar` |
| `usuario` | `str` | não (default `'sessao_demo'`) | invocador | `auditar` |
| `descricao_clinica` | `str \| None` | não | invocador | `regras_seguranca`, `recuperar_protocolos_rag` |
| `publico` | `'clinico' \| 'tecnico'` | não (default `'clinico'`) | invocador | `sintetizar_com_llm` |

**`dados_clinicos` nunca é modificado.** É o registro do que entrou. `features` é o derivado
validado. A distinção permite ao `erro_validacao` mostrar o valor recebido ao lado da faixa aceita.

### 5.2 Validação

| Campo | Tipo | Escrito por | Lido por | Existe quando |
|---|---|---|---|---|
| `features` | `GestanteFeatures \| None` | `validar_dados` | `regras_seguranca`, `executar_modelo_ml`, `gerar_explicabilidade`, `modo_degradado`, `auditar` | sempre; `None` se inválido |
| `campos_faltantes` | `list[str]` | `validar_dados` | `_rota_validacao`, `dados_incompletos` | sempre; `[]` no caminho feliz |
| `erros_validacao` | `list[dict]` | `validar_dados` | `_rota_validacao`, `erro_validacao` | sempre; `[]` no caminho feliz |

### 5.3 Regras, ML e explicabilidade

| Campo | Tipo | Escrito por | Lido por |
|---|---|---|---|
| `regras_disparadas` | `list[str]` | `regras_seguranca`, `modo_degradado` | `_rota_regras`, `bypass_ml`, `sintetizar_com_llm`, `auditar` |
| `eh_emergencia` | `bool` | `regras_seguranca` | `aplicar_avisos_seguranca`, `compilar_resposta` |
| `resultado_predicao` | `ResultadoPredicao \| None` | `executar_modelo_ml` | `_rota_modelo`, `gerar_explicabilidade`, `sintetizar_com_llm`, `auditar` |
| `dados_imputados` | `list[str]` | `executar_modelo_ml` | `sintetizar_com_llm`, `aplicar_avisos_seguranca` |
| `falha_modelo` | `str \| None` | `executar_modelo_ml` | `modo_degradado`, `compilar_resposta` |
| `resultado_explicacao` | `ResultadoExplicacao \| None` | `gerar_explicabilidade` | `recuperar_protocolos_rag`, `sintetizar_com_llm`, `auditar` |

**`regras_disparadas` tem dois escritores** — `regras_seguranca` (sinais de alarme) e
`modo_degradado` (critérios de alto risco atendidos). Eles nunca executam na mesma passagem:
`modo_degradado` só é alcançável quando `regras_disparadas` estava vazio. A exclusividade mútua é
garantida pela topologia, não por convenção, e é verificável no grafo.

### 5.4 RAG, LLM e HIL

| Campo | Tipo | Escrito por | Lido por |
|---|---|---|---|
| `fontes` | `list[dict]` | `recuperar_protocolos_rag` | `sintetizar_com_llm`, `compilar_resposta` |
| `fontes_sem_filtro` | `bool` | `recuperar_protocolos_rag` | `aplicar_avisos_seguranca` |
| `falha_rag` | `str \| None` | `recuperar_protocolos_rag` | `aplicar_avisos_seguranca`, `compilar_resposta` |
| `payload_llm` | `dict` | `sintetizar_com_llm` | `validar_resposta_llm`, `usar_resposta_estruturada` |
| `variante_prompt` | `str` | `sintetizar_com_llm` | `validar_resposta_llm` |
| `texto_llm` | `str` | `sintetizar_com_llm` | `validar_resposta_llm` |
| `falha_llm` | `str \| None` | `sintetizar_com_llm` | `validar_resposta_llm` |
| `verificacao` | `ResultadoVerificacao \| None` | `validar_resposta_llm` | `_rota_validacao_llm`, `usar_resposta_estruturada`, `compilar_resposta` |
| `texto_descartado` | `bool` | `validar_resposta_llm`, `usar_resposta_estruturada` | `compilar_resposta` |
| `resposta_texto` | `str` | `validar_resposta_llm`, `usar_resposta_estruturada`, `erro_validacao`, `solicitar_complemento`, `aplicar_avisos_seguranca` | `compilar_resposta` |
| `requer_intervencao_humana` | `bool` | `dados_incompletos` | UI, `compilar_resposta` |
| `intervencao` | `dict` | `dados_incompletos` | UI, `solicitar_complemento` |
| `decisao_humana` | `dict \| None` | invocador na reinvocação | `solicitar_complemento` |

**`resposta_texto` tem cinco escritores** e é o campo de maior risco do estado. Disciplina que o
torna seguro: os cinco nós são **mutuamente exclusivos por caminho**, exceto
`aplicar_avisos_seguranca`, que é o único a **acrescentar** em vez de substituir, e é sempre o
último a escrever. A ordem é garantida pela topologia (ele é o ponto de convergência obrigatório).

### 5.5 Controle, trace, auditoria e saída

| Campo | Tipo | Escrito por | Lido por |
|---|---|---|---|
| `modo` | `ModoExecucao` | `validar_dados`, `bypass_ml`, `executar_modelo_ml`, `modo_degradado`, `dados_incompletos` | `sintetizar_com_llm`, `validar_resposta_llm`, `auditar`, `compilar_resposta` |
| `correlation_id` | `str` | `validar_dados` (primeiro nó) | todos os nós, no log estruturado |
| `falhas` | `list[dict]` | qualquer nó que capture erro | `compilar_resposta`, log |
| `raciocinio` | `list[str]` | **todos** | `compilar_resposta`, UI |
| `auditoria_id` | `int \| None` | `auditar` | `compilar_resposta` |
| `auditoria_falhou` | `bool` | `auditar` | `compilar_resposta`, `aplicar_avisos_seguranca` |
| `resposta_estruturada` | `dict` | `compilar_resposta` | UI |

**`modo` tem cinco escritores, um por caminho.** Cada um escreve exatamente uma vez, e a topologia
garante que só um caminho é percorrido. O valor final é sempre o do último nó de caminho
atravessado, que é o correto por construção.

**`correlation_id` é escrito no primeiro nó**, não pelo invocador, para que exista mesmo quando a
invocação vem de um lugar que não sabe gerá-lo. Ele amarra rastro, log e linha de auditoria.

---

## 6. Semântica de merge do LangGraph e o padrão de concatenação manual

### 6.1 O que o código faz hoje `[COD]`

Nos quatro workflows, cada nó que acrescenta ao trace escreve:

```python
'raciocinio': state.get('raciocinio', []) + ['nova linha']
```

Isso aparece em `triagem.py:88,111-114,133,150,172,192,216`,
`violencia.py:86,100,117,136,150,197,228`, `obstetrico.py:117,140,179,213,271,314` e
`prevencao.py:74,138,175,208,248`. Sem exceção.

### 6.2 Por que funciona

`StateGraph` atualiza o estado por **merge raso de dicionário**. O retorno de um nó é aplicado sobre
o estado como `estado.update(retorno)`: as chaves presentes no retorno **substituem** as do estado;
as ausentes ficam intactas.

Sem redutor declarado, `{'raciocinio': ['x']}` **substituiria** o histórico inteiro por `['x']`. A
concatenação manual — ler o valor atual e devolver a lista completa — devolve o resultado já
acumulado, e a substituição passa a ser inofensiva porque o novo valor contém o antigo.

Funciona, e funciona por três razões que valem ser nomeadas:

| # | Razão |
|---|---|
| 1 | Os grafos são **sequenciais**. Nenhum nó executa em paralelo, então nunca há dois retornos disputando a mesma chave na mesma superstep |
| 2 | A ordem de leitura e escrita é local e evidente: quem lê `state.get(...)` lê o estado no momento em que o nó começou |
| 3 | O padrão é **uniforme**. Todos os 27 nós dos quatro workflows fazem igual, o que torna o desvio visível em revisão |

### 6.3 Por que é frágil

A garantia não é estrutural — é convencional. O modo de falha:

```python
# Nó novo, escrito por alguém que não conhece a convenção:
return {'raciocinio': ['classifiquei o caso']}
# Efeito: o trace de todos os nós anteriores desaparece, sem erro.
```

Nada avisa. `TypedDict` valida tipo, não semântica de acumulação; `list[str]` é `list[str]` tanto
para o histórico quanto para uma linha só. O rastro de explicabilidade — que é a coisa que o campo
existe para preservar — some silenciosamente.

O mesmo vale para `fontes` em `triagem.py:171` (`fontes_existentes + novas`).

### 6.4 O que redutores `Annotated` dariam

```python
from typing import Annotated
import operator

class RiscoMLState(TypedDict, total=False):
    raciocinio: Annotated[list[str], operator.add]
    fontes:     Annotated[list[dict], operator.add]
    falhas:     Annotated[list[dict], operator.add]
```

Com o redutor, o nó devolve **só o delta**:

```python
return {'raciocinio': ['classifiquei o caso']}   # concatenado, não substituído
```

| Aspecto | Concatenação manual | Redutor `Annotated` |
|---|---|---|
| Perda acidental de histórico | **Possível**, silenciosa | **Impossível** — o merge é `+` |
| Verbosidade no nó | `state.get('raciocinio', []) + [...]` | `[...]` |
| Acoplamento do nó ao estado anterior | O nó **lê** o estado para escrever | O nó não precisa ler |
| Nós paralelos (`add_edge` múltiplo a partir de um nó) | **Perde** atualizações concorrentes | Funciona corretamente |
| Testabilidade do nó isolado | Precisa montar estado com histórico | Basta o delta |
| Consistência com os 4 existentes | Total | Divergente |

A quarta linha é a mais relevante para o futuro. O grafo novo tem convergências
(`bypass_ml`, `modo_degradado` e `gerar_explicabilidade` → `recuperar_protocolos_rag`), mas elas são
**alternativas**, não paralelas: só um caminho executa. Se alguma iteração futura introduzir
paralelismo real — por exemplo, rodar RAG e explicabilidade ao mesmo tempo, que é a otimização
natural — a concatenação manual passa a perder atualizações, e o sintoma será rastro incompleto,
que é difícil de diagnosticar.

### 6.5 Decisão

**`RiscoMLState` mantém a concatenação manual**, alinhado ao que `DIAGRAMA_LANGGRAPH.md` §
"Observação técnica" já declara: *"O workflow novo mantém a mesma convenção, por consistência."*

Razões, e o custo:

| Razão | Peso |
|---|---|
| Consistência com 27 nós existentes; um só padrão a aprender | Alto |
| ADR-001 privilegia evolução aditiva sobre mudança de padrão sem necessidade técnica | Alto |
| Não há paralelismo no grafo projetado; o benefício principal do redutor não se materializa hoje | Médio |
| `Annotated` exigiria decidir se os quatro existentes migram junto (e eles estão na lista "não tocar") | Alto |

**Custo aceito:** um nó novo escrito sem a convenção apaga o trace silenciosamente. Mitigação
proposta, e é barata:

```python
# tests/unit/test_convencao_estado.py  — PROJETADO
def test_todo_no_preserva_raciocinio():
    """Cada nó, recebendo estado com raciocinio=['anterior'], deve devolver
    raciocinio que comece por 'anterior' — ou não devolver a chave."""
```

Transforma uma convenção não verificada num invariante testado. Se essa proteção se mostrar
insuficiente na prática, a migração para `Annotated` no workflow novo é isolada e reversível —
registrada aqui como alternativa disponível, não como dívida escondida.

---

## 7. Tabela de transições — `risco_ml`

`Σ` = estado atual (nó) · evento · `Σ'` = próximo nó. Eventos são condições sobre o estado, não
mensagens.

| # | Estado atual | Evento | Próximo estado | Efeito no estado |
|---|---|---|---|---|
| T-01 | `START` | invocação com `dados_clinicos` | `validar_dados` | `correlation_id` gerado |
| T-02 | `validar_dados` | `erros_validacao != []` | `erro_validacao` | `modo='incompleto'` |
| T-03 | `validar_dados` | `erros_validacao == []` e `campos_faltantes != []` | `dados_incompletos` | `modo='incompleto'` |
| T-04 | `validar_dados` | `features` construído | `regras_seguranca` | `features` preenchido |
| T-05 | `erro_validacao` | — | `aplicar_avisos_seguranca` | `resposta_texto` com erro por campo |
| T-06 | `dados_incompletos` | — | `solicitar_complemento` | `requer_intervencao_humana=True`, `intervencao` |
| T-07 | `solicitar_complemento` | — | `aplicar_avisos_seguranca` | `resposta_texto` com pedido de complemento |
| T-08 | `regras_seguranca` | `regras_disparadas != []` | `bypass_ml` | `eh_emergencia=True` |
| T-09 | `regras_seguranca` | `regras_disparadas == []` | `executar_modelo_ml` | — |
| T-10 | `bypass_ml` | — | `recuperar_protocolos_rag` | `modo='bypass_regra'`, `variante_prompt='bypass'` |
| T-11 | `executar_modelo_ml` | `ModeloIndisponivelError` | `modo_degradado` | `resultado_predicao=None`, `falha_modelo` |
| T-12 | `executar_modelo_ml` | predição obtida | `gerar_explicabilidade` | `resultado_predicao`, `dados_imputados`, `modo='normal'` |
| T-13 | `modo_degradado` | — | `recuperar_protocolos_rag` | `modo='degradado'`, `regras_disparadas` (critérios) |
| T-14 | `gerar_explicabilidade` | sempre (nunca falha) | `recuperar_protocolos_rag` | `resultado_explicacao` |
| T-15 | `recuperar_protocolos_rag` | busca com filtro devolveu itens | `sintetizar_com_llm` | `fontes` |
| T-16 | `recuperar_protocolos_rag` | filtro vazio, sem filtro devolveu itens | `sintetizar_com_llm` | `fontes`, `fontes_sem_filtro=True` |
| T-17 | `recuperar_protocolos_rag` | nada encontrado | `sintetizar_com_llm` | `fontes=[]` |
| T-18 | `recuperar_protocolos_rag` | exceção do Chroma | `sintetizar_com_llm` | `fontes=[]`, `falha_rag` |
| T-19 | `sintetizar_com_llm` | geração ok | `validar_resposta_llm` | `payload_llm`, `texto_llm` |
| T-20 | `sintetizar_com_llm` | exceção na geração | `validar_resposta_llm` | `texto_llm=''`, `falha_llm` |
| T-21 | `validar_resposta_llm` | `verificacao.aprovada` | `aplicar_avisos_seguranca` | `resposta_texto = texto_llm` |
| T-22 | `validar_resposta_llm` | reprovada ou `verificacao is None` | `usar_resposta_estruturada` | `texto_descartado=True` |
| T-23 | `usar_resposta_estruturada` | — | `aplicar_avisos_seguranca` | `resposta_texto` estruturado + faixa |
| T-24 | `aplicar_avisos_seguranca` | — | `auditar` | `resposta_texto` com avisos anexados |
| T-25 | `auditar` | `INSERT` bem-sucedido | `compilar_resposta` | `auditoria_id` |
| T-26 | `auditar` | `INSERT` falhou | `compilar_resposta` | `auditoria_falhou=True`, log crítico, `falhas` |
| T-27 | `compilar_resposta` | — | `END` | `resposta_estruturada` |

### 7.1 Propriedades verificáveis da tabela

| # | Propriedade | Verificação |
|---|---|---|
| P-1 | Todo caminho de `START` a `END` passa por T-24, T-25 ou T-26, e T-27 | Inspeção do grafo compilado |
| P-2 | `modo` é definido exatamente uma vez por execução | T-02, T-03, T-10, T-12, T-13 são mutuamente exclusivos |
| P-3 | T-08 precede T-09 na avaliação: regra antes de ML | `_rota_regras` é chamada em `regras_seguranca`, que precede `executar_modelo_ml` na topologia |
| P-4 | Nenhuma transição volta atrás: o grafo é acíclico | Inspeção |
| P-5 | T-22 é o destino padrão de `validar_resposta_llm` em caso de estado inesperado | `_rota_validacao_llm` retorna descarte quando `verificacao is None` |
| P-6 | T-18 e T-20 não interrompem o fluxo | Ambas roteiam para o nó seguinte normal |

P-4 merece nota: **o grafo é acíclico por decisão**, o que significa que não há retry dentro dele.
A política de retry de `TRATAMENTO_DE_ERROS.md` §6 fica **dentro** dos nós, não como aresta de
volta — um ciclo no grafo exigiria contador de iteração no estado e criaria risco de laço infinito
num sistema sem timeout.

---

## 8. Comparativo dos cinco estados

| | `TriagemState` | `ViolenciaState` | `ObstetricoState` | `PrevencaoState` | `RiscoMLState` |
|---|---|---|---|---|---|
| Campos | 14 | 18 | 15 | 12 | **34** |
| Campos de entrada | 2 | 4 | 3 | 1 | 5 |
| Campos de controle de erro | 0 | 0 | 0 | 0 | **7** |
| Campos de HIL | 0 | 1 (`confirmacao_clinica`) | 0 | 0 | **3** |
| Campos de auditoria | 0 | 1 (`registro_id`) | 0 | 0 | **2** |
| Tem `confianca` | sim | sim | sim | sim | **não** (§1) |
| Campos declarados e nunca escritos | 0 | 1 (`fontes`) | 0 | 0 | 0 |
| Dados construídos e não devolvidos | 0 | **1** (`medidas`) | 0 | 0 | 0 |
| Redutores `Annotated` | não | não | não | não | não (§6.5) |

A linha "campos de controle de erro" é a diferença estrutural entre os quatro estados existentes e o
novo. Zero contra sete não é sofisticação: é a diferença entre um estado que só representa o
caminho feliz e um que representa também o que deu errado.

---

## 9. Estado atual

| Item | Estado |
|---|---|
| `TriagemState`, `ViolenciaState`, `ObstetricoState`, `PrevencaoState` | `[COD]` — existem |
| `RiscoMLState` | **Não existe** |
| Campos novos em `ObstetricoState` (`classificacao_origem` etc.) | **Não existem** |
| `medidas_seguranca` em `ViolenciaState` | **Não existe** — defeito registrado, não corrigido (ADR-001) |
| Redutores `Annotated` em qualquer workflow | **Nenhum** |
| `tests/unit/test_convencao_estado.py` | **Não existe** |
| Qualquer transição do workflow novo executada | **Nenhuma** |
