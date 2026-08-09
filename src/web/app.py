from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from core.config import getSettings
from core.schemas.budget_schema import OrcamentoSchema
from web.components.sidebar_component import renderSidebarNavigation
from web.views.items_view import renderItemsView
from web.views.upload_view import renderUploadView


def ensureSessionState() -> None:
    """Initialize shared session state used by every application view."""
    if "documents_by_name" not in st.session_state:
        st.session_state["documents_by_name"] = {}

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


def syncDocumentsFromStorage() -> None:
    """Ensure local PDFs appear in session state even before extraction metadata exists."""
    settings = getSettings()
    storageDirectory = Path(settings.storageDir)
    storageDirectory.mkdir(parents=True, exist_ok=True)

    documentsByName: dict[str, dict[str, object]] = st.session_state["documents_by_name"]
    existingFileNames = set()

    for pdfPath in storageDirectory.glob("*.pdf"):
        existingFileNames.add(pdfPath.name)
        if pdfPath.name in documentsByName:
            continue

        documentsByName[pdfPath.name] = {
            "file_name": pdfPath.name,
            "file_path": str(pdfPath.resolve()),
            "original_name": pdfPath.name,
            "created_at": datetime.fromtimestamp(pdfPath.stat().st_mtime).strftime("%Y-%m-%d"),
            "status": "Com Pendencia",
            "client_name": "",
            "seller_name": "",
            "total_amount": 0.0,
            "extracted_data": OrcamentoSchema().model_dump(),
        }

    removableKeys = [fileName for fileName in documentsByName if fileName not in existingFileNames]
    for fileName in removableKeys:
        documentsByName.pop(fileName, None)


def renderPage() -> None:
    """Render the main application with sidebar navigation and central views."""
    st.set_page_config(
        page_title="Gestao de Orcamentos",
        page_icon=":material/description:",
        layout="wide",
    )

    ensureSessionState()
    syncDocumentsFromStorage()

    selectedView = renderSidebarNavigation()
    allDocuments: list[dict[str, object]] = list(st.session_state["documents_by_name"].values())

    if selectedView == "📦 Itens e Materiais Extraidos":
        renderItemsView(allDocuments)
        return

    renderUploadView(allDocuments)


renderPage()
