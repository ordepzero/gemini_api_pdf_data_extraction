from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from core.database.connection import SessionLocal
from core.database.models import Cliente, ItemOrcamento, Orcamento, Vendedor
from core.schemas.api_schema import BudgetListItemSchema, BudgetProcessResponseSchema, PaginatedBudgetsResponseSchema
from core.schemas.budget_schema import OrcamentoSchema
from core.services.extractor import extract_budget_data
from core.services.pricing_engine import calculateAreaM2, calculatePrecoPorM2
from core.services.storage_service import save_uploaded_file
from core.services.vector_service import vectorService


budgetsBlueprint = Blueprint("budgets", __name__, url_prefix="/api/v1/budgets")


@budgetsBlueprint.post("/process")
def processBudget():
    uploadedFile = request.files.get("file")
    if uploadedFile is None:
        return jsonify({"error": "Arquivo PDF nao enviado.", "status_code": 400}), 400

    with SessionLocal() as session:
        saveResult = save_uploaded_file(uploaded_file=uploadedFile)
        extractedBudget = extract_budget_data(str(saveResult["file_path"]))
        persistedBudget = _persistProcessedBudget(
            session=session,
            saveResult=saveResult,
            extractedBudget=extractedBudget,
        )
        session.commit()
        session.refresh(persistedBudget)

        responseSchema = _buildBudgetProcessResponse(
            persistedBudget,
            extractedBudget=extractedBudget,
        )

    return jsonify(responseSchema.model_dump(mode="json")), 201


@budgetsBlueprint.get("")
def listBudgets():
    page = request.args.get("page", default=1, type=int)
    pageSize = request.args.get("page_size", default=20, type=int)
    cliente = request.args.get("cliente")
    vendedor = request.args.get("vendedor")
    status = request.args.get("status")

    with SessionLocal() as session:
        baseQuery = (
            select(Orcamento)
            .options(joinedload(Orcamento.cliente), joinedload(Orcamento.vendedor))
            .order_by(Orcamento.criadoEm.desc())
        )
        countQuery = select(func.count(Orcamento.id))

        if cliente:
            baseQuery = baseQuery.join(Orcamento.cliente).where(Cliente.nome.ilike(f"%{cliente}%"))
            countQuery = countQuery.join(Orcamento.cliente).where(Cliente.nome.ilike(f"%{cliente}%"))
        if vendedor:
            baseQuery = baseQuery.join(Orcamento.vendedor).where(Vendedor.nome.ilike(f"%{vendedor}%"))
            countQuery = countQuery.join(Orcamento.vendedor).where(Vendedor.nome.ilike(f"%{vendedor}%"))
        if status:
            baseQuery = baseQuery.where(Orcamento.status == status)
            countQuery = countQuery.where(Orcamento.status == status)

        total = session.execute(countQuery).scalar_one()
        budgets = session.execute(
            baseQuery.offset((page - 1) * pageSize).limit(pageSize)
        ).scalars().unique().all()

    response = PaginatedBudgetsResponseSchema(
        items=[
            BudgetListItemSchema(
                id=budget.id,
                numeroOrcamento=budget.numeroOrcamento,
                status=budget.status,
                valorTotal=budget.valorTotal,
                arquivoOriginalNome=budget.arquivoOriginalNome,
                arquivoSalvoNome=budget.arquivoSalvoNome,
                clienteNome=budget.cliente.nome if budget.cliente else None,
                vendedorNome=budget.vendedor.nome if budget.vendedor else None,
                criadoEm=budget.criadoEm,
            )
            for budget in budgets
        ],
        page=page,
        pageSize=pageSize,
        total=total,
    )
    return jsonify(response.model_dump(mode="json"))


@budgetsBlueprint.delete("/<int:budgetId>")
def deleteBudget(budgetId: int):
    with SessionLocal() as session:
        budget = session.get(Orcamento, budgetId)
        if budget is None:
            return jsonify({"error": "Orcamento nao encontrado.", "status_code": 404}), 404

        filePath = Path(budget.arquivoCaminho)
        vectorService.removeBudgetItems(budgetId=budget.id)
        session.delete(budget)
        session.commit()

    if filePath.exists():
        filePath.unlink()

    return jsonify({"message": "Orcamento removido com sucesso.", "status_code": 200})


def _persistProcessedBudget(
    session,
    saveResult: dict[str, object],
    extractedBudget: OrcamentoSchema,
) -> Orcamento:
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
        status="Processado",
        arquivoOriginalNome=str(saveResult["original_name"]),
        arquivoSalvoNome=str(saveResult["final_name"]),
        arquivoCaminho=str(saveResult["file_path"]),
        clienteId=cliente.id if cliente else None,
        vendedorId=vendedor.id if vendedor else None,
    )
    session.add(budget)
    session.flush()

    indexedItems: list[dict[str, object]] = []
    for index, itemSchema in enumerate(extractedBudget.itens or [], start=1):
        largura, comprimento = _extractDimensions(itemSchema.dimensoes)
        areaM2 = calculateAreaM2(largura=largura, comprimento=comprimento)
        precoPorM2 = calculatePrecoPorM2(
            valorUnitario=itemSchema.valorUnitario,
            areaM2=areaM2,
        )
        item = ItemOrcamento(
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
        session.add(item)
        indexedItems.append(
            {
                "codigo": item.codigo,
                "descricao": item.descricao,
                "material": item.material,
                "preco_por_m2": item.precoPorM2,
                "orcamento_id": budget.id,
            }
        )

    session.flush()
    vectorService.indexBudgetItems(budgetId=budget.id, items=indexedItems)
    return budget


def _buildBudgetProcessResponse(
    budget: Orcamento,
    extractedBudget: OrcamentoSchema,
) -> BudgetProcessResponseSchema:
    return BudgetProcessResponseSchema(
        id=budget.id,
        status=budget.status,
        arquivoOriginalNome=budget.arquivoOriginalNome,
        arquivoSalvoNome=budget.arquivoSalvoNome,
        arquivoCaminho=budget.arquivoCaminho,
        cliente=extractedBudget.cliente,
        vendedor=extractedBudget.vendedor,
        orcamento=extractedBudget,
        itens=extractedBudget.itens or [],
    )


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
