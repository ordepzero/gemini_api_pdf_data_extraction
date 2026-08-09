from __future__ import annotations

import streamlit as st

from core.services.budget_db_service import deleteBudgetRecord

def renderDocumentList(documents: list[dict[str, object]]) -> None:
    """Render the master list of budget documents."""
    st.subheader("Documentos cadastrados")

    if not documents:
        st.info("Nenhum documento encontrado para os filtros selecionados.")
        return

    _renderListHeader()

    for document in documents:
        _renderListRow(document=document)


def _renderListHeader() -> None:
    headerCol1, headerCol2, headerCol3, headerCol4, headerCol5 = st.columns([4, 2, 2, 1, 1])
    headerCol1.markdown("**Nome do arquivo**")
    headerCol2.markdown("**Cliente**")
    headerCol3.markdown("**Data**")
    headerCol4.markdown("**👁️**")
    headerCol5.markdown("**🗑️**")


def _renderListRow(document: dict[str, object]) -> None:
    rowContainer = st.container(border=True)
    fileName = str(document["file_name"])

    with rowContainer:
        nameCol, clientCol, dateCol, viewCol, deleteCol = st.columns([4, 2, 2, 1, 1])
        nameCol.write(fileName)
        clientCol.write(str(document.get("client_name") or "-"))
        dateCol.write(f"{str(document.get('created_at') or '-')} • {str(document.get('status') or 'Com Pendencia')}")

        if viewCol.button(
            "👁️",
            key=f"view_{fileName}",
            help="Visualizar PDF e dados",
            use_container_width=True,
        ):
            st.session_state["selected_document"] = fileName

        if deleteCol.button(
            "🗑️",
            key=f"delete_{fileName}",
            help="Excluir registro",
            use_container_width=True,
        ):
            st.session_state["document_pending_delete"] = fileName

    pendingDelete = st.session_state.get("document_pending_delete")
    if pendingDelete == fileName:
        _renderDeleteDialog(document=document)


@st.dialog("Confirmar exclusao")
def _renderDeleteDialog(document: dict[str, object]) -> None:
    fileName = str(document["file_name"])
    st.write(f"Deseja realmente excluir o arquivo `{fileName}`?")

    confirmCol, cancelCol = st.columns(2)
    if confirmCol.button("Confirmar exclusao", type="primary", width="stretch"):
        deleteBudgetRecord(budgetId=int(document["id"]))
        if st.session_state.get("selected_document") == fileName:
            st.session_state["selected_document"] = None
        st.session_state["document_pending_delete"] = None
        st.toast(f"Arquivo {fileName} excluido com sucesso.")
        st.rerun()

    if cancelCol.button("Cancelar", width="stretch"):
        st.session_state["document_pending_delete"] = None
        st.rerun()
