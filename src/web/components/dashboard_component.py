from __future__ import annotations

import streamlit as st

def renderTopSection(documents: list[dict[str, object]]) -> str:
    """Render page header, metrics and search field."""
    st.title("Gestao e Extracao de Orcamentos")
    st.caption("Central de acompanhamento, conferencia e visualizacao de orcamentos em PDF.")

    totalPdfs = len(documents)
    totalAmount = sum(float(document.get("total_amount", 0.0) or 0.0) for document in documents)
    pendingCount = sum(1 for document in documents if document.get("status") == "Com Pendencia")

    metricCol1, metricCol2, metricCol3 = st.columns(3)
    metricCol1.metric("Total de PDFs", totalPdfs)
    metricCol2.metric("Valor total orcado (R$)", f"{totalAmount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    metricCol3.metric("Pendentes de revisao", pendingCount)

    return st.text_input(
        "Buscar por arquivo, cliente ou vendedor",
        placeholder="Digite um nome de arquivo, cliente ou vendedor",
    )
