from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.database.connection import SessionLocal
from core.database.models import ItemOrcamento
from core.schemas.api_schema import ItemPricingResponseSchema
from core.services.pricing_engine import calculateAreaM2
from core.services.vector_service import search_similar_items


pricingBlueprint = Blueprint("pricing", __name__, url_prefix="/api/v1/items")


@pricingBlueprint.get("/reference-pricing")
def getReferencePricing():
    material = request.args.get("material")
    largura = request.args.get("largura", type=float)
    comprimento = request.args.get("comprimento", type=float)

    with SessionLocal() as session:
        payload = _buildReferencePricingPayload(
            session=session,
            material=material,
            largura=largura,
            comprimento=comprimento,
        )

    return jsonify(payload.model_dump(mode="json"))


def _buildReferencePricingPayload(
    session: Session,
    material: str | None,
    largura: float | None,
    comprimento: float | None,
) -> ItemPricingResponseSchema:
    query = select(func.avg(ItemOrcamento.precoPorM2)).where(ItemOrcamento.precoPorM2.is_not(None))
    if material:
        query = query.where(ItemOrcamento.material == material)

    precoMedioPorM2 = session.execute(query).scalar()
    areaM2 = calculateAreaM2(largura=largura, comprimento=comprimento)
    valorEstimado = precoMedioPorM2 * areaM2 if precoMedioPorM2 and areaM2 else None

    return ItemPricingResponseSchema(
        material=material,
        largura=largura,
        comprimento=comprimento,
        areaM2=areaM2,
        precoMedioPorM2=precoMedioPorM2,
        valorEstimado=valorEstimado,
        itensReferencia=search_similar_items(
            query=material or "",
            material=material,
            top_k=5,
        ),
    )
