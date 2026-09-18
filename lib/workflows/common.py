"""Helpers compartilhados pelos 4 workflows LangGraph.

- llm_json: pede ao LLM uma saída JSON e parse com fallbacks
- llm_text: pede texto livre
- rag_search: wrapper de retriever que devolve dicts limpos
- citar_fontes: formata lista de fontes para resposta final
"""
from __future__ import annotations

import json
import re
from typing import Any


def _strip_fences(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def llm_json(chat_model, user_prompt: str, system_prompt: str | None = None,
             default: Any = None) -> Any:
    """Pede ao LLM uma saída JSON. Resiliente a markdown fences e texto extra."""
    from langchain_core.messages import HumanMessage, SystemMessage
    msgs = []
    if system_prompt:
        msgs.append(SystemMessage(content=system_prompt))
    msgs.append(HumanMessage(content=user_prompt))

    response = chat_model.invoke(msgs)
    text = response.content if hasattr(response, 'content') else str(response)
    cleaned = _strip_fences(text)

    # Tenta JSON direto
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Tenta extrair primeiro {...} ou [...]
    for pattern in (r'\{.*\}', r'\[.*\]'):
        m = re.search(pattern, cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                continue

    return default if default is not None else {}


def llm_text(chat_model, user_prompt: str, system_prompt: str | None = None) -> str:
    """Pede ao LLM texto livre."""
    from langchain_core.messages import HumanMessage, SystemMessage
    msgs = []
    if system_prompt:
        msgs.append(SystemMessage(content=system_prompt))
    msgs.append(HumanMessage(content=user_prompt))
    response = chat_model.invoke(msgs)
    return (response.content if hasattr(response, 'content') else str(response)).strip()


def rag_search(retriever, query: str, categoria: str | None = None,
               k: int = 4) -> list[dict]:
    """Busca no Chroma. Prefere filtro nativo; cai para pós-processamento."""
    docs = []
    if categoria:
        try:
            if hasattr(retriever, 'vectorstore') and hasattr(retriever.vectorstore, 'similarity_search'):
                docs = retriever.vectorstore.similarity_search(
                    query, k=k, filter={'category': categoria}
                )
            elif hasattr(retriever, 'invoke'):
                docs = retriever.invoke(query)
        except Exception:
            docs = retriever.invoke(query) if hasattr(retriever, 'invoke') else []
    else:
        docs = retriever.invoke(query)
    out = []
    for d in docs[: k * 2]:
        meta = getattr(d, 'metadata', None) or {}
        if categoria and meta.get('category') and meta.get('category') != categoria:
            continue
        out.append({
            'trecho': getattr(d, 'page_content', '') if not isinstance(d, dict) else d.get('trecho', ''),
            'doc_id': meta.get('doc_id', '?') if meta else (d.get('doc_id', '?') if isinstance(d, dict) else '?'),
            'category': meta.get('category', '?') if meta else (d.get('category', '?') if isinstance(d, dict) else '?'),
            'chunk_id': meta.get('chunk_id', '?') if meta else (d.get('chunk_id', '?') if isinstance(d, dict) else '?'),
        })
        if len(out) >= k:
            break
    return out


def citar_fontes(fontes: list[dict]) -> str:
    """Formata fontes de RAG para incluir na resposta final do fluxo."""
    if not fontes:
        return ''
    unicas: dict[str, dict] = {}
    for f in fontes:
        key = f.get('doc_id', '?')
        if key not in unicas:
            unicas[key] = f
    linhas = ['\n**Fontes consultadas:**']
    for f in unicas.values():
        linhas.append(f"- `{f['doc_id']}` ({f['category']})")
    return '\n'.join(linhas)


# Nível de confiança baseado em quantidade/qualidade de evidência usada
def estimar_confianca(n_fontes: int, n_decisoes_llm: int,
                     dados_paciente_disponiveis: bool) -> str:
    """Heurística simples: alta/media/baixa."""
    score = 0
    if n_fontes >= 3:
        score += 2
    elif n_fontes >= 1:
        score += 1
    if dados_paciente_disponiveis:
        score += 1
    if n_decisoes_llm <= 2:
        score += 1
    return 'alta' if score >= 4 else ('media' if score >= 2 else 'baixa')
