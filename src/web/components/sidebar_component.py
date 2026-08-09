from __future__ import annotations

import streamlit as st

def renderSidebarNavigation() -> str:
    """Render the main sidebar navigation and return the selected view."""
    with st.sidebar:
        st.title("Budget AI")
        st.caption("Gestao inteligente de orcamentos em PDF")
        st.divider()
        return st.radio(
            "Navegacao",
            options=[
                "📄 Orcamentos e Upload",
                "📦 Itens e Materiais Extraidos",
            ],
            index=0,
        )
