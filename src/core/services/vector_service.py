from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import getSettings


class VectorService:
    """In-memory skeleton ready to evolve into a ChromaDB-backed index."""

    def __init__(self) -> None:
        settings = getSettings()
        self.persistDirectory = Path(settings.chromaPersistDirectory)
        self.persistDirectory.mkdir(parents=True, exist_ok=True)
        self._documents: list[dict[str, Any]] = []

    def indexBudgetItems(self, budgetId: int, items: list[dict[str, Any]]) -> None:
        for item in items:
            self._documents.append(
                {
                    "budget_id": budgetId,
                    "descricao": item.get("descricao"),
                    "material": item.get("material"),
                    "preco_por_m2": item.get("preco_por_m2"),
                    "metadata": item,
                }
            )

    def removeBudgetItems(self, budgetId: int) -> None:
        self._documents = [
            document for document in self._documents if document["budget_id"] != budgetId
        ]

    def searchSimilarItems(
        self,
        query: str,
        material: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        normalizedQuery = query.strip().lower()
        normalizedMaterial = (material or "").strip().lower()
        filteredDocuments: list[dict[str, Any]] = []

        for document in self._documents:
            descricao = str(document.get("descricao") or "").lower()
            documentMaterial = str(document.get("material") or "").lower()
            matchesQuery = not normalizedQuery or normalizedQuery in descricao
            matchesMaterial = not normalizedMaterial or normalizedMaterial == documentMaterial

            if matchesQuery and matchesMaterial:
                filteredDocuments.append(document["metadata"])

        return filteredDocuments[:top_k]


vectorService = VectorService()


def search_similar_items(
    query: str,
    material: str | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Public helper for historical item retrieval."""
    return vectorService.searchSimilarItems(query=query, material=material, top_k=top_k)
