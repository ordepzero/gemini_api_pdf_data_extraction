from __future__ import annotations

import pandas as pd
import streamlit as st

from core.schemas.budget_schema import OrcamentoSchema


def renderItemsView(allDocuments: list[dict[str, object]]) -> None:
    """Render the consolidated extracted items view."""
    st.title("Itens e Materiais Extraidos")
    st.caption("Tabela consolidada com todos os itens extraidos dos orcamentos processados.")

    allItems = _buildFlattenedItems(allDocuments)

    filterCol1, filterCol2, filterCol3 = st.columns(3)
    materialFilter = filterCol1.text_input("Filtrar por material", placeholder="Ex: M1 ou MDF")
    itemFilter = filterCol2.text_input("Filtrar por item", placeholder="Nome ou descricao")
    clientFilter = filterCol3.text_input("Filtrar por cliente", placeholder="Nome do cliente")

    filteredItems = _filterItems(
        items=allItems,
        materialFilter=materialFilter,
        itemFilter=itemFilter,
        clientFilter=clientFilter,
    )

    if not filteredItems:
        st.info("Nenhum item extraido encontrado para os filtros selecionados.")
        return

    st.dataframe(pd.DataFrame(filteredItems), width="stretch", hide_index=True)


def _buildFlattenedItems(documents: list[dict[str, object]]) -> list[dict[str, object]]:
    flattenedItems: list[dict[str, object]] = []

    for document in documents:
        extractedData = OrcamentoSchema.model_validate(document.get("extracted_data", {}))
        clientName = extractedData.cliente.nome if extractedData.cliente and extractedData.cliente.nome else ""
        budgetNumber = extractedData.numeroOrcamento or str(document.get("file_name") or "")

        for index, item in enumerate(extractedData.itens or [], start=1):
            flattenedItems.append(
                {
                    "codigo": f"{budgetNumber}-{index}",
                    "descricao_original": item.descricao or "",
                    "descricao_normalizada": _normalizeDescription(item.descricao or ""),
                    "material": item.material or "",
                    "dimensoes": item.dimensoes or "",
                    "quantidade": item.quantidade,
                    "valor_unitario": item.valorUnitario,
                    "valor_total": item.valorTotal,
                    "cliente": clientName,
                    "numero_orcamento": budgetNumber,
                }
            )

    return flattenedItems


def _filterItems(
    items: list[dict[str, object]],
    materialFilter: str,
    itemFilter: str,
    clientFilter: str,
) -> list[dict[str, object]]:
    normalizedMaterial = materialFilter.strip().lower()
    normalizedItem = itemFilter.strip().lower()
    normalizedClient = clientFilter.strip().lower()
    filteredItems: list[dict[str, object]] = []

    for item in items:
        matchesMaterial = not normalizedMaterial or normalizedMaterial in str(item.get("material") or "").lower()
        matchesItem = not normalizedItem or normalizedItem in str(item.get("descricao_original") or "").lower() or normalizedItem in str(item.get("descricao_normalizada") or "").lower()
        matchesClient = not normalizedClient or normalizedClient in str(item.get("cliente") or "").lower()

        if matchesMaterial and matchesItem and matchesClient:
            filteredItems.append(item)

    return filteredItems


def _normalizeDescription(description: str) -> str:
    return " ".join(description.lower().split())
