from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from core.schemas.budget_schema import ClienteSchema, ItemOrcamentoSchema, OrcamentoSchema, VendedorSchema


class ItemPricingResponseSchema(BaseModel):
    material: str | None = None
    largura: float | None = None
    comprimento: float | None = None
    areaM2: float | None = None
    precoMedioPorM2: float | None = None
    valorEstimado: float | None = None
    itensReferencia: list[dict[str, object]] = Field(default_factory=list)


class BudgetListItemSchema(BaseModel):
    id: int
    numeroOrcamento: str | None = None
    status: str
    valorTotal: float | None = None
    arquivoOriginalNome: str
    arquivoSalvoNome: str
    clienteNome: str | None = None
    vendedorNome: str | None = None
    criadoEm: datetime


class BudgetProcessResponseSchema(BaseModel):
    id: int
    status: str
    arquivoOriginalNome: str
    arquivoSalvoNome: str
    arquivoCaminho: str
    cliente: ClienteSchema | None = None
    vendedor: VendedorSchema | None = None
    orcamento: OrcamentoSchema
    itens: list[ItemOrcamentoSchema] = Field(default_factory=list)


class PaginatedBudgetsResponseSchema(BaseModel):
    items: list[BudgetListItemSchema]
    page: int
    pageSize: int
    total: int
