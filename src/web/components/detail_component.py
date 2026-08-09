from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from core.schemas.budget_schema import OrcamentoSchema


def renderDocumentDetail(selectedDocument: dict[str, object] | None) -> None:
    """Render the PDF viewer and extracted details area."""
    st.subheader("Visualizador e detalhes")

    if selectedDocument is None:
        st.info("Selecione um PDF na lista para visualizar")
        return

    previewTab, extractedDataTab = st.tabs(["Visualizacao do PDF", "Dados extraidos (Gemini)"])

    with previewTab:
        _renderPdfPreview(filePath=Path(str(selectedDocument["file_path"])))

    with extractedDataTab:
        extractedData = OrcamentoSchema.model_validate(selectedDocument["extracted_data"])
        with st.form("extracted_data_form", border=True):
            customerCol, sellerCol = st.columns(2)
            customerCol.text_input("Cliente", value=extractedData.cliente.nome if extractedData.cliente and extractedData.cliente.nome else "")
            sellerCol.text_input("Vendedor", value=extractedData.vendedor.nome if extractedData.vendedor and extractedData.vendedor.nome else "")

            dateCol, validityCol = st.columns(2)
            dateCol.text_input("Data de emissao", value=extractedData.dataEmissao or "")
            validityCol.text_input("Validade", value=extractedData.validade or "")

            totalCol, subtotalCol, discountCol = st.columns(3)
            totalCol.text_input(
                "Valor total",
                value=_formatCurrency(extractedData.valorTotal),
            )
            subtotalCol.text_input("Subtotal", value=_formatCurrency(extractedData.subtotal))
            discountCol.text_input("Desconto", value=_formatCurrency(extractedData.desconto))

            itemsDataframe = pd.DataFrame(
                [
                    {
                        "descricao": item.descricao,
                        "quantidade": item.quantidade,
                        "unidade": item.unidade,
                        "material": item.material,
                        "dimensoes": item.dimensoes,
                        "valor_unitario": item.valorUnitario,
                        "valor_total": item.valorTotal,
                    }
                    for item in (extractedData.itens or [])
                ]
            )
            st.dataframe(itemsDataframe, width="stretch", hide_index=True)
            st.form_submit_button("Confirmar conferencia", type="primary")


def _renderPdfPreview(filePath: Path) -> None:
    if not filePath.exists():
        st.error("O arquivo PDF selecionado nao foi encontrado no armazenamento local.")
        return

    pdfBytes = filePath.read_bytes()
    base64Pdf = base64.b64encode(pdfBytes).decode("utf-8")
    st.markdown(
        (
            f'<iframe src="data:application/pdf;base64,{base64Pdf}" '
            'width="100%" height="700" type="application/pdf"></iframe>'
        ),
        unsafe_allow_html=True,
    )


def _formatCurrency(value: float | None) -> str:
    if value is None:
        return ""

    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
