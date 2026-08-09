from __future__ import annotations

from typing import Any

import streamlit as st

def renderUploadComponent(uploaderKey: str) -> Any | None:
    """Render the upload widget and return the selected file."""
    uploaded_file = st.file_uploader(
        "Selecione um arquivo PDF",
        type=["pdf"],
        accept_multiple_files=False,
        key=uploaderKey,
    )
    return uploaded_file
