from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.database.connection import Base, SessionLocal, engine
from core.database.models import Cliente, ItemOrcamento, Orcamento, Vendedor
from core.schemas.budget_schema import OrcamentoSchema
from core.services.pricing_engine import calculateAreaM2, calculatePrecoPorM2


def initializeDatabase() -> None:
    """Create the SQLite schema used by the Streamlit app."""
    Base.metadata.create_all(bind=engine)


def saveProcessedBudget(
    saveResult: dict[str, object],
    extractedBudget: OrcamentoSchema,
) -> dict[str, object]:
    """Persist a fully processed budget and return its serialized representation."""
    with SessionLocal() as session:
        cliente = None
        vendedor = None

        if extractedBudget.cliente and extractedBudget.cliente.nome:
            cliente = Cliente(
                nome=extractedBudget.cliente.nome,
                documento=extractedBudget.cliente.documento,
                telefone=extractedBudget.cliente.telefone,
                email=extractedBudget.cliente.email,
                endereco=extractedBudget.cliente.endereco,
            )
            session.add(cliente)
            session.flush()

        if extractedBudget.vendedor and extractedBudget.vendedor.nome:
            vendedor = Vendedor(
                nome=extractedBudget.vendedor.nome,
                telefone=extractedBudget.vendedor.telefone,
                email=extractedBudget.vendedor.email,
                empresa=extractedBudget.vendedor.empresa,
            )
            session.add(vendedor)
            session.flush()

        budget = Orcamento(
            numeroOrcamento=extractedBudget.numeroOrcamento,
            dataEmissao=extractedBudget.dataEmissao,
            validade=extractedBudget.validade,
            subtotal=extractedBudget.subtotal,
            desconto=extractedBudget.desconto,
            frete=extractedBudget.frete,
            impostos=extractedBudget.impostos,
            valorTotal=extractedBudget.valorTotal,
            observacoesGerais=extractedBudget.observacoesGerais,
            status="Com Pendencia" if _hasPendingData(extractedBudget) else "Processado",
            arquivoOriginalNome=str(saveResult["original_name"]),
            arquivoSalvoNome=str(saveResult["final_name"]),
            arquivoCaminho=str(saveResult["file_path"]),
            clienteId=cliente.id if cliente else None,
            vendedorId=vendedor.id if vendedor else None,
        )
        session.add(budget)
        session.flush()

        for index, itemSchema in enumerate(extractedBudget.itens or [], start=1):
            largura, comprimento = _extractDimensions(itemSchema.dimensoes)
            areaM2 = calculateAreaM2(largura=largura, comprimento=comprimento)
            precoPorM2 = calculatePrecoPorM2(
                valorUnitario=itemSchema.valorUnitario,
                areaM2=areaM2,
            )
            session.add(
                ItemOrcamento(
                    orcamentoId=budget.id,
                    codigo=f"{budget.numeroOrcamento or budget.id}-{index}",
                    descricao=itemSchema.descricao,
                    descricaoNormalizada=_normalizeDescription(itemSchema.descricao or ""),
                    quantidade=itemSchema.quantidade,
                    unidade=itemSchema.unidade,
                    material=itemSchema.material,
                    dimensoes=itemSchema.dimensoes,
                    largura=largura,
                    comprimento=comprimento,
                    areaM2=areaM2,
                    valorUnitario=itemSchema.valorUnitario,
                    valorTotal=itemSchema.valorTotal,
                    precoPorM2=precoPorM2,
                    observacoes=itemSchema.observacoes,
                )
            )

        session.commit()
        budgetId = budget.id

    return getBudgetRecord(budgetId)


def listBudgetRecords() -> list[dict[str, object]]:
    """Read all budgets directly from SQLite."""
    with SessionLocal() as session:
        budgets = session.execute(
            select(Orcamento)
            .options(
                joinedload(Orcamento.cliente),
                joinedload(Orcamento.vendedor),
                joinedload(Orcamento.itens),
            )
            .order_by(Orcamento.criadoEm.desc())
        ).scalars().unique().all()
        return [_serializeBudget(budget) for budget in budgets]


def getBudgetRecord(budgetId: int) -> dict[str, object]:
    """Read one budget directly from SQLite."""
    with SessionLocal() as session:
        budget = session.execute(
            select(Orcamento)
            .options(
                joinedload(Orcamento.cliente),
                joinedload(Orcamento.vendedor),
                joinedload(Orcamento.itens),
            )
            .where(Orcamento.id == budgetId)
        ).scalars().unique().one()
        return _serializeBudget(budget)


def deleteBudgetRecord(budgetId: int) -> None:
    """Delete a budget from SQLite and remove its physical PDF."""
    with SessionLocal() as session:
        budget = session.get(Orcamento, budgetId)
        if budget is None:
            return

        filePath = Path(budget.arquivoCaminho)
        session.delete(budget)
        session.commit()

    if filePath.exists():
        filePath.unlink()


def _serializeBudget(budget: Orcamento) -> dict[str, object]:
    extractedData = OrcamentoSchema(
        numeroOrcamento=budget.numeroOrcamento,
        dataEmissao=budget.dataEmissao,
        validade=budget.validade,
        cliente={
            "nome": budget.cliente.nome if budget.cliente else None,
            "documento": budget.cliente.documento if budget.cliente else None,
            "telefone": budget.cliente.telefone if budget.cliente else None,
            "email": budget.cliente.email if budget.cliente else None,
            "endereco": budget.cliente.endereco if budget.cliente else None,
        }
        if budget.cliente
        else None,
        vendedor={
            "nome": budget.vendedor.nome if budget.vendedor else None,
            "telefone": budget.vendedor.telefone if budget.vendedor else None,
            "email": budget.vendedor.email if budget.vendedor else None,
            "empresa": budget.vendedor.empresa if budget.vendedor else None,
        }
        if budget.vendedor
        else None,
        itens=[
            {
                "descricao": item.descricao,
                "quantidade": item.quantidade,
                "unidade": item.unidade,
                "material": item.material,
                "dimensoes": item.dimensoes,
                "valorUnitario": item.valorUnitario,
                "valorTotal": item.valorTotal,
                "observacoes": item.observacoes,
            }
            for item in budget.itens
        ],
        subtotal=budget.subtotal,
        desconto=budget.desconto,
        frete=budget.frete,
        impostos=budget.impostos,
        valorTotal=budget.valorTotal,
        observacoesGerais=budget.observacoesGerais,
    )

    return {
        "id": budget.id,
        "file_name": budget.arquivoSalvoNome,
        "file_path": budget.arquivoCaminho,
        "original_name": budget.arquivoOriginalNome,
        "created_at": budget.dataEmissao or budget.criadoEm.strftime("%Y-%m-%d"),
        "status": budget.status,
        "client_name": budget.cliente.nome if budget.cliente else "",
        "seller_name": budget.vendedor.nome if budget.vendedor else "",
        "total_amount": budget.valorTotal or 0.0,
        "extracted_data": extractedData.model_dump(),
    }


def _hasPendingData(extractedBudget: OrcamentoSchema) -> bool:
    clientName = extractedBudget.cliente.nome if extractedBudget.cliente and extractedBudget.cliente.nome else ""
    return not clientName or not extractedBudget.itens


def _extractDimensions(dimensoes: str | None) -> tuple[float | None, float | None]:
    if not dimensoes:
        return None, None

    normalized = dimensoes.lower().replace(",", ".").replace("x", " ")
    numericParts: list[str] = []
    current = ""
    for char in normalized:
        if char.isdigit() or char == ".":
            current += char
            continue
        if current:
            numericParts.append(current)
            current = ""
    if current:
        numericParts.append(current)

    if len(numericParts) < 2:
        return None, None

    try:
        return float(numericParts[0]), float(numericParts[1])
    except ValueError:
        return None, None


def _normalizeDescription(description: str) -> str:
    return " ".join(description.lower().split())
