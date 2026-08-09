from __future__ import annotations

from pathlib import Path

import streamlit as st

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
    headerCol1, headerCol2, headerCol3, headerCol4, headerCol5 = st.columns([3, 2, 1.4, 1.6, 1.4])
    headerCol1.markdown("**Nome do arquivo**")
    headerCol2.markdown("**Cliente**")
    headerCol3.markdown("**Data**")
    headerCol4.markdown("**Status**")
    headerCol5.markdown("**Acoes**")


def _renderListRow(document: dict[str, object]) -> None:
    rowContainer = st.container(border=True)
    fileName = str(document["file_name"])

    with rowContainer:
        nameCol, clientCol, dateCol, statusCol, actionCol = st.columns([3, 2, 1.4, 1.6, 1.4])
        nameCol.write(fileName)
        clientCol.write(str(document.get("client_name") or "-"))
        dateCol.write(str(document.get("created_at") or "-"))
        _renderStatusBadge(container=statusCol, status=str(document.get("status") or "Com Pendencia"))

        with actionCol:
            previewCol, deleteCol = st.columns(2)
            if previewCol.button(
                "Ver",
                key=f"view_{fileName}",
                icon=":material/visibility:",
                width="stretch",
            ):
                st.session_state["selected_document"] = fileName

            if deleteCol.button(
                "Excluir",
                key=f"delete_{fileName}",
                icon=":material/delete:",
                width="stretch",
            ):
                st.session_state["document_pending_delete"] = fileName

    pendingDelete = st.session_state.get("document_pending_delete")
    if pendingDelete == fileName:
        _renderDeleteDialog(document=document)


def _renderStatusBadge(container: st.delta_generator.DeltaGenerator, status: str) -> None:
    if status == "Processado":
        container.success(status)
        return

    container.warning(status)


@st.dialog("Confirmar exclusao")
def _renderDeleteDialog(document: dict[str, object]) -> None:
    fileName = str(document["file_name"])
    st.write(f"Deseja realmente excluir o arquivo `{fileName}`?")

    confirmCol, cancelCol = st.columns(2)
    if confirmCol.button("Confirmar exclusao", type="primary", width="stretch"):
        filePath = Path(str(document["file_path"]))
        if filePath.exists():
            filePath.unlink()

        documents = st.session_state.get("documents_by_name", {})
        documents.pop(fileName, None)
        st.session_state["documents_by_name"] = documents

        if st.session_state.get("selected_document") == fileName:
            st.session_state["selected_document"] = None
        st.session_state["document_pending_delete"] = None
        st.toast(f"Arquivo {fileName} excluido com sucesso.")
        st.rerun()

    if cancelCol.button("Cancelar", width="stretch"):
        st.session_state["document_pending_delete"] = None
        st.rerun()
