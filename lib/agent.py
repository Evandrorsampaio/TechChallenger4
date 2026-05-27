"""Agente LangGraph ReAct para o assistente clínico.

Une o LLM (base ou fine-tuned via [[llm]]) com as tools de [[tools]] e o
retriever Chroma (RAG) para responder consultas da equipe de saúde.

Uso típico:

    from lib.agent import build_agent, run_consulta
    from lib.llm   import load_finetuned, build_chat_model
    from lib.tools import build_langchain_tools

    model, tok = load_finetuned()
    chat       = build_chat_model(model, tok)
    tools_list = build_langchain_tools(conn, retriever)
    agent      = build_agent(chat, tools_list)

    out = run_consulta(agent, 'Conduta em LSIL em paciente <25a?', paciente_id=1)
    print(out['resposta'])
"""
from __future__ import annotations

from typing import Any


SYSTEM_PROMPT = """Você é um assistente clínico voltado para a EQUIPE DE SAÚDE de um hospital (médicos, enfermeiros, residentes, técnicos) especializado em SAÚDE DA MULHER. Você NÃO conversa com a paciente — você apoia o profissional que a atende.

REGRAS DE COMPORTAMENTO
- Linguagem técnica e objetiva em português brasileiro. Use siglas clínicas quando apropriado (CID, IG, DUM, LSIL, HSIL, BI-RADS, etc.).
- Responda no tom de protocolo clínico: cite conduta, dose, critério ou fluxo de forma direta e acionável.
- NUNCA oriente o usuário a "procurar um profissional de saúde" — o usuário JÁ é o profissional.
- Quando o protocolo não responder claramente a uma dúvida, diga isso explicitamente: "Os protocolos disponíveis não cobrem este cenário".

USO DAS FERRAMENTAS (escolha a apropriada antes de responder)
- `buscar_protocolo(query, categoria?)` — SEMPRE que a pergunta envolver conduta clínica, posologia, fluxo, critério diagnóstico ou encaminhamento. Cite trecho e fonte (`doc_id`) ao final da resposta.
- `consultar_prontuario(paciente_id)` — se a pergunta envolver uma paciente específica.
- `historico_exames(paciente_id, tipo?)` — para checar exames preventivos já realizados.
- `exames_atrasados(paciente_id)` — para alertar sobre rastreamento em atraso (papanicolau, mamografia).
- `consultar_medicamento(termo)` — para verificar princípio ativo, indicação, categoria gestacional/lactacional, contraindicações.
- `calendario_menstrual(paciente_id)` — para estimar próxima menstruação / janela fértil.
- `avaliar_padrao_violencia(sinais)` — quando o profissional descrever sinais clínicos sugestivos de violência. Use as chaves: lesoes_inexplicadas, lesoes_multiplas_fases, retardo_atendimento, discordancia_historia_exame, acompanhante_controlador, abortos_inexplicados, somatizacoes_cronicas, baixa_adesao, ideacao_suicida, gestacao_indesejada, isolamento_social, historico_violencia_familiar.
- `consultar_violencia(paciente_id, motivo)` — APENAS com motivo clínico explícito (acesso é auditado por LGPD).
- `registrar_violencia(paciente_id, tipo, encaminhamentos, observacoes?)` — somente quando houver confirmação clínica e o profissional pedir registro formal.

FORMATO DA RESPOSTA
1. Resposta direta à pergunta, em parágrafo curto.
2. Conduta / dose / fluxo (bullets se houver mais de um item).
3. Citação dos protocolos consultados (Fonte: `doc_id` chunk N), quando houver.
4. Em casos sensíveis (violência, ideação suicida): incluir orientações de notificação SINAN e serviços da rede que o profissional deve oferecer à paciente.

CONTEXTO DA SESSÃO
Quando o usuário enviar uma mensagem prefixada por "[Contexto: paciente_id=N]", use N como `paciente_id` nas tools relevantes sem perguntar de novo."""


def build_agent(chat_model, tools_list, system_prompt: str = SYSTEM_PROMPT,
                max_iterations: int = 6):
    """Constroi um agente ReAct (LangGraph) com tool calling.

    `chat_model` deve suportar `bind_tools` (ChatHuggingFace, ChatOpenAI etc).
    """
    try:
        from langgraph.prebuilt import create_react_agent
    except ImportError as e:
        raise ImportError('langgraph não instalado. Rode: pip install langgraph') from e

    return create_react_agent(
        model=chat_model,
        tools=tools_list,
        prompt=system_prompt,
    )


def run_consulta(agent, pergunta: str, paciente_id: int | None = None,
                 historico: list | None = None,
                 recursion_limit: int = 12) -> dict[str, Any]:
    """Executa uma consulta no agente.

    Retorna:
        {
          'resposta':   str,
          'tool_calls': List[{tool, args, result}],
          'mensagens':  List[BaseMessage]  (para uso como histórico na próxima chamada)
        }
    """
    from langchain_core.messages import HumanMessage

    if paciente_id is not None:
        pergunta = f'[Contexto: paciente_id={paciente_id}]\n{pergunta}'

    mensagens_in = list(historico) if historico else []
    mensagens_in.append(HumanMessage(content=pergunta))

    estado = agent.invoke(
        {'messages': mensagens_in},
        config={'recursion_limit': recursion_limit},
    )

    msgs = estado['messages']
    resposta = msgs[-1].content if msgs else ''

    tool_calls = []
    # Extrai chamadas de ferramenta e seus resultados percorrendo as mensagens.
    for i, m in enumerate(msgs):
        calls = getattr(m, 'tool_calls', None)
        if not calls:
            continue
        for c in calls:
            resultado = None
            # Procura próxima ToolMessage com o tool_call_id correspondente
            for n in msgs[i + 1:]:
                if getattr(n, 'tool_call_id', None) == c.get('id'):
                    resultado = n.content
                    break
            tool_calls.append({
                'tool': c.get('name'),
                'args': c.get('args'),
                'result': resultado,
            })

    return {'resposta': resposta, 'tool_calls': tool_calls, 'mensagens': msgs}
