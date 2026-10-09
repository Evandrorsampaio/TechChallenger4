from __future__ import annotations

from lib.llm_fake import FakeChatModel
from lib.mock_data import populate
from lib.rag_local import build_local_retriever
from lib.workflows.risco_ml import build_risco_ml_workflow
from tests.conftest import CASO_OK


def test_fluxo_ml_cpu_preenche_doc_id_real(conn_tmp):
    populate(conn_tmp, seed=42, verbose=False)
    wf = build_risco_ml_workflow(FakeChatModel(), conn_tmp, build_local_retriever())
    alto = dict(CASO_OK)
    alto.update({'idade': 41, 'has_cronica': True, 'pas_mmhg': 150, 'pad_mmhg': 95})
    state = wf.invoke({'dados_clinicos': alto, 'usuario': 'pytest'})
    out = state.get('resposta_estruturada') or {}
    fontes = out.get('retrieved_sources') or []
    assert fontes, out
    doc_ids = {f.get('doc_id') for f in fontes}
    assert None not in doc_ids
    assert '?' not in doc_ids
    assert 'ms_prenatal' not in doc_ids
    assert all(str(i).endswith('.pdf') for i in doc_ids)
