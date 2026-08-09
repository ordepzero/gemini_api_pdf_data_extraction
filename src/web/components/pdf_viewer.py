from __future__ import annotations

from pathlib import Path

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer


def renderPdfViewer(file_path: str | Path) -> None:
    """Render a PDF with a viewer compatible with local and deployed environments."""
    resolvedPath = Path(file_path)
    if not resolvedPath.exists():
        st.error("O arquivo PDF selecionado nao foi encontrado no armazenamento local.")
        return

    pdf_viewer(input=resolvedPath.read_bytes(), width="100%", height=700)
