from __future__ import annotations

from lib.rag_local import CORPUS_PADRAO, build_local_retriever, carregar_corpus


def test_corpus_versionado_tem_doc_id_estavel():
    chunks = carregar_corpus()
    ids = {c['doc_id'] for c in chunks}
    assert CORPUS_PADRAO.exists()
    assert 'ms_manual_tecnico_gestacao_alto_risco.pdf' in ids
    assert 'ms_prenatal' not in ids
    assert all(c.get('text') and c.get('category') for c in chunks)


def test_busca_hipertensao_cita_fonte_real():
    retr = build_local_retriever()
    docs = retr.invoke('hipertensão pré-eclâmpsia gestação alto risco')
    ids = [d.metadata['doc_id'] for d in docs]
    assert ids
    assert all(i != 'ms_prenatal' for i in ids)
    assert any('hipertens' in i or 'alto_risco' in i or 'gestacao' in i for i in ids)


def test_busca_violencia_cita_sinan():
    retr = build_local_retriever()
    docs = retr.invoke('violência doméstica notificação SINAN Ligue 180')
    assert any(d.metadata['category'] == 'violencia_domestica' for d in docs)
    assert any('violencia' in d.metadata['doc_id'] for d in docs)
