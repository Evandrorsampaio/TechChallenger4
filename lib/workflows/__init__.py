"""Workflows LangGraph para cenários clínicos do assistente hospitalar.

Cada workflow é um StateGraph compilado, com nodes nomeados que correspondem
às etapas do enunciado da Tech Challenge Fase 3:

- triagem.py     → Triagem Ginecológica
- violencia.py   → Detecção de Violência Doméstica
- obstetrico.py  → Atendimento Obstétrico
- prevencao.py   → Prevenção e Rastreamento

Uso típico (cada workflow tem a mesma forma):

    from lib.workflows.triagem import build_triagem_workflow
    workflow = build_triagem_workflow(chat_model, conn, retriever)
    estado_final = workflow.invoke({'queixa': '...', 'paciente_id': 1})
"""
from .triagem import build_triagem_workflow, TriagemState
from .violencia import build_violencia_workflow, ViolenciaState
from .obstetrico import build_obstetrico_workflow, ObstetricoState
from .prevencao import build_prevencao_workflow, PrevencaoState

__all__ = [
    'build_triagem_workflow', 'TriagemState',
    'build_violencia_workflow', 'ViolenciaState',
    'build_obstetrico_workflow', 'ObstetricoState',
    'build_prevencao_workflow', 'PrevencaoState',
]
