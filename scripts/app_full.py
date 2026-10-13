"""Gradio do perfil Colab: Llama 3.2 3B + Chroma. Sem FakeChatModel.

Espelha o bootstrap de `08_app_gradio.ipynb`. Caminhos vêm do ambiente
(CHROMA_PATH, ADAPTER_DIR, HF_TOKEN, HOSPITAL_DB_PATH), não do Google Drive.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('PERFIL_EXECUCAO', 'full-gpu')


def _exigir_token() -> str:
    token = (os.environ.get('HF_TOKEN') or '').strip()
    if not token:
        raise SystemExit(
            'HF_TOKEN ausente. Copie .env.example para .env, aceite a licença do '
            'meta-llama/Llama-3.2-3B-Instruct na sua conta e preencha o token.'
        )
    return token


def _cuda_disponivel() -> bool:
    import torch

    return bool(torch.cuda.is_available())


def main() -> None:
    token = _exigir_token()
    from huggingface_hub import login

    login(token=token)

    from lib.runtime_full import (
        COLLECTION_PADRAO,
        EMBEDDING_PADRAO,
        chroma_dir_configurado,
        decidir_4bit,
        device_embeddings,
        hospital_db_full,
        origem_adapter,
        pedido_4bit,
        resolver_adapter,
    )
    from lib.chroma_store import diretorio_local

    cuda = _cuda_disponivel()
    use_4bit = decidir_4bit(cuda, pedido_4bit())
    device = device_embeddings(cuda)
    print(f'[full] cuda={cuda} use_4bit={use_4bit} embeddings={device}')
    if (os.environ.get('USE_4BIT') or '').strip() == '1' and not use_4bit:
        print('[full] USE_4BIT=1 ignorado: não há GPU CUDA neste contêiner.')

    adapter_dir, finetune_base = origem_adapter()
    adapter = resolver_adapter(adapter_dir, finetune_base)
    if adapter is None:
        print('[full] adapter LoRA não encontrado; carregando só o modelo base.')
    else:
        print(f'[full] adapter: {adapter}')

    from lib.llm import build_chat_model, load_finetuned

    model, tokenizer = load_finetuned(adapter_dir=adapter, use_4bit=use_4bit)
    chat = build_chat_model(model, tokenizer)
    print('[full] LLM pronto.')

    origem = chroma_dir_configurado()
    chroma_local = str(diretorio_local(origem))
    if not (Path(chroma_local) / 'chroma.sqlite3').is_file():
        raise SystemExit(
            f'Índice Chroma não encontrado em {origem}. Restaure files/chroma do Drive '
            '(chroma.sqlite3 e a pasta do segmento) na raiz do repositório.'
        )
    print('[full] Chroma aberto em', chroma_local)

    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_PADRAO,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = Chroma(
        collection_name=os.environ.get('CHROMA_COLLECTION', COLLECTION_PADRAO),
        embedding_function=embeddings,
        persist_directory=chroma_local,
    )
    n_chunks = vectorstore._collection.count()
    if n_chunks == 0:
        raise SystemExit(
            f'A coleção em {chroma_local} está vazia. Confira CHROMA_COLLECTION '
            f'(padrão {COLLECTION_PADRAO}) e se a pasta é a gerada pelo notebook 06.'
        )
    retriever = vectorstore.as_retriever(search_kwargs={'k': 4})
    print(f'[full] Chroma: {n_chunks} chunks.')

    from lib.agent import build_agent
    from lib.db import connect, init_schema
    from lib.mock_data import populate
    from lib.tools import build_langchain_tools
    from lib.ui import build_ui
    from lib.workflows.obstetrico import build_obstetrico_workflow
    from lib.workflows.prevencao import build_prevencao_workflow
    from lib.workflows.risco_ml import build_risco_ml_workflow
    from lib.workflows.triagem import build_triagem_workflow
    from lib.workflows.violencia import build_violencia_workflow

    db = hospital_db_full()
    conn = connect(db)
    init_schema(conn)
    n = conn.execute('SELECT COUNT(*) AS c FROM pacientes').fetchone()['c']
    if n == 0:
        populate(conn, seed=42, verbose=False)
        print('[full] prontuário sintético gerado em', db)

    tools = build_langchain_tools(conn, retriever)
    agent = build_agent(chat, tools)
    workflows = {
        'triagem': build_triagem_workflow(chat, conn, retriever),
        'violencia': build_violencia_workflow(chat, conn, retriever),
        'obstetrico': build_obstetrico_workflow(chat, conn, retriever),
        'prevencao': build_prevencao_workflow(chat, conn, retriever),
        'risco_ml': build_risco_ml_workflow(chat, conn, retriever),
    }
    print(f'[full] agente com {len(tools)} ferramentas; workflows: {list(workflows)}')

    app = build_ui(agent, conn, default_usuario='dr_residente_demo', workflows=workflows)
    app.launch(
        server_name='0.0.0.0',
        server_port=int(os.environ.get('PORT', '7860')),
        share=False,
        show_error=True,
    )


if __name__ == '__main__':
    main()
