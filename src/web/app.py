from __future__ import annotations

import streamlit as st

from core.services.budget_db_service import initializeDatabase, listBudgetRecords
from web.components.sidebar_component import renderSidebarNavigation
from web.views.items_view import renderItemsView
from web.views.upload_view import renderUploadView


def ensureSessionState() -> None:
    """Initialize shared session state used by every application view."""
    if "selected_document" not in st.session_state:
        st.session_state["selected_document"] = None

    if "document_pending_delete" not in st.session_state:
        st.session_state["document_pending_delete"] = None

    if "current_uploaded_file" not in st.session_state:
        st.session_state["current_uploaded_file"] = None

    if "last_uploaded_signature" not in st.session_state:
        st.session_state["last_uploaded_signature"] = None

    if "uploader_key_index" not in st.session_state:
        st.session_state["uploader_key_index"] = 0

def renderPage() -> None:
    """Render the main application with sidebar navigation and central views."""
    st.set_page_config(
        page_title="Gestao de Orcamentos",
        page_icon=":material/description:",
        layout="wide",
    )

    ensureSessionState()
    initializeDatabase()

    selectedView = renderSidebarNavigation()
    allDocuments = listBudgetRecords()

    if selectedView == "📦 Itens e Materiais Extraidos":
        renderItemsView(allDocuments)
        return

    renderUploadView(allDocuments)


renderPage()
