from __future__ import annotations

import logging
import time
from typing import Any

import streamlit as st

from core.config import getSettings
from core.schemas.budget_schema import OrcamentoSchema
from core.services.extractor import extract_budget_data
from core.services.storage_service import StorageServiceError, save_uploaded_file
from web.components.dashboard_component import renderTopSection
from web.components.detail_component import renderDocumentDetail
from web.components.document_list_component import renderDocumentList
from web.components.upload_component import renderUploadComponent


def renderUploadView(allDocuments: list[dict[str, object]]) -> None:
    """Render the upload and budgets master-detail view."""
    st.title("Gestao e Extracao de Orcamentos")
    st.caption("Envie PDFs, acompanhe o processamento e revise os dados extraidos.")

    _renderUploadSection()

    searchTerm = renderTopSection(allDocuments)
    selectedStatus = st.segmented_control(
        "Filtrar por status",
        options=["Todos", "Processados", "Com Pendencia"],
        default="Todos",
        selection_mode="single",
    )

    filteredDocuments = _filterDocuments(
        documents=allDocuments,
        selectedStatus=selectedStatus or "Todos",
        searchTerm=searchTerm,
    )
    selectedDocument = _getSelectedDocument(allDocuments)

    st.divider()
    leftColumn, rightColumn = st.columns([1, 1])

    with leftColumn:
        renderDocumentList(filteredDocuments)

    with rightColumn:
        renderDocumentDetail(selectedDocument)


def _renderUploadSection() -> None:
    settings = getSettings()

    with st.container(border=True):
        st.subheader("Upload de PDF")
        st.caption(f"Diretorio de armazenamento: `{settings.storageDir}`")

        uploaderKey = f"pdf_uploader_{st.session_state['uploader_key_index']}"
        uploadedFile = renderUploadComponent(uploaderKey=uploaderKey)
        _syncCurrentUploadedFile(uploadedFile=uploadedFile)
        _renderCurrentUploadStatus()


def _syncCurrentUploadedFile(uploadedFile: Any | None) -> None:
    if uploadedFile is None:
        return

    uploadedSignature = _buildUploadedFileSignature(uploadedFile=uploadedFile)
    lastUploadedSignature = st.session_state.get("last_uploaded_signature")
    if uploadedSignature == lastUploadedSignature:
        return

    try:
        saveResult = save_uploaded_file(uploaded_file=uploadedFile)
    except StorageServiceError as error:
        st.error(f"Falha ao salvar o arquivo enviado: {error}")
        return

    st.session_state["current_uploaded_file"] = saveResult
    st.session_state["last_uploaded_signature"] = uploadedSignature


def _renderCurrentUploadStatus() -> None:
    currentUploadedFile = st.session_state.get("current_uploaded_file")
    if not isinstance(currentUploadedFile, dict):
        st.info("Selecione um arquivo PDF para preparar o processamento.")
        return

    originalName = str(currentUploadedFile["original_name"])
    finalName = str(currentUploadedFile["final_name"])
    if bool(currentUploadedFile.get("was_renamed")):
        st.warning(f"Aviso: Arquivo renomeado para '{finalName}'. Nome original: '{originalName}'.")
    elif bool(currentUploadedFile.get("was_sanitized")):
        st.warning(f"Aviso: Arquivo ajustado para '{finalName}' para compatibilidade.")
    else:
        st.success(f"Arquivo carregado com sucesso: {finalName}")

    actionCol, clearCol = st.columns([2, 1])
    if actionCol.button(
        "[🚀 Extrair Dados com Gemini]",
        key="process_current_uploaded_file",
        type="primary",
        width="stretch",
    ):
        _processCurrentUploadedFile()

    if clearCol.button(
        "Remover/Limpar",
        key="clear_current_uploaded_file",
        width="stretch",
    ):
        _clearCurrentUploadedFile(removePhysicalFile=True)
        st.rerun()


def _processCurrentUploadedFile() -> None:
    currentUploadedFile = st.session_state.get("current_uploaded_file")
    if not isinstance(currentUploadedFile, dict):
        st.error("Nenhum arquivo esta pronto para processamento.")
        return

    startTime = time.perf_counter()

    try:
        with st.spinner("Processando e extraindo dados do PDF..."):
            extractedBudget = extract_budget_data(str(currentUploadedFile["file_path"]))
            _ensureMinimumLoadingTime(startTime=startTime)
    except Exception as error:
        logging.error("Erro na extracao do PDF", exc_info=True)
        print(f"Erro na extracao do PDF: {type(error).__name__}: {error}")
        st.error(f"Erro na extração: {error}")
        return

    documentsByName: dict[str, dict[str, object]] = st.session_state["documents_by_name"]
    finalName = str(currentUploadedFile["final_name"])
    documentsByName[finalName] = _buildDocumentRecord(
        saveResult=currentUploadedFile,
        extractedBudget=extractedBudget,
    )
    st.session_state["selected_document"] = finalName
    _clearCurrentUploadedFile(removePhysicalFile=False)
    st.toast("Extração concluída!")
    st.rerun()


def _clearCurrentUploadedFile(removePhysicalFile: bool) -> None:
    currentUploadedFile = st.session_state.get("current_uploaded_file")
    if removePhysicalFile and isinstance(currentUploadedFile, dict):
        from pathlib import Path

        filePath = Path(str(currentUploadedFile["file_path"]))
        if filePath.exists():
            filePath.unlink()

    st.session_state["current_uploaded_file"] = None
    st.session_state["last_uploaded_signature"] = None
    st.session_state["uploader_key_index"] = int(st.session_state["uploader_key_index"]) + 1


def _buildUploadedFileSignature(uploadedFile: Any | None) -> str | None:
    if uploadedFile is None:
        return None

    fileName = str(getattr(uploadedFile, "name", "") or "")
    fileSize = int(getattr(uploadedFile, "size", 0) or 0)
    return f"{fileName}:{fileSize}"


def _ensureMinimumLoadingTime(startTime: float) -> None:
    minimumLoadingTimeSeconds = getSettings().minLoadingTimeSeconds
    elapsedTime = time.perf_counter() - startTime
    remainingTime = max(0.0, minimumLoadingTimeSeconds - elapsedTime)
    time.sleep(remainingTime)


def _buildDocumentRecord(
    saveResult: dict[str, Any],
    extractedBudget: OrcamentoSchema,
) -> dict[str, object]:
    clientName = extractedBudget.cliente.nome if extractedBudget.cliente and extractedBudget.cliente.nome else ""
    sellerName = extractedBudget.vendedor.nome if extractedBudget.vendedor and extractedBudget.vendedor.nome else ""
    documentDate = extractedBudget.dataEmissao or ""
    totalAmount = extractedBudget.valorTotal or 0.0
    hasPendingData = not clientName or not extractedBudget.itens

    return {
        "file_name": str(saveResult["final_name"]),
        "file_path": str(saveResult["file_path"]),
        "original_name": str(saveResult["original_name"]),
        "created_at": documentDate,
        "status": "Com Pendencia" if hasPendingData else "Processado",
        "client_name": clientName,
        "seller_name": sellerName,
        "total_amount": totalAmount,
        "extracted_data": extractedBudget.model_dump(),
    }


def _filterDocuments(
    documents: list[dict[str, object]],
    selectedStatus: str,
    searchTerm: str,
) -> list[dict[str, object]]:
    normalizedSearchTerm = searchTerm.strip().lower()
    filteredDocuments: list[dict[str, object]] = []

    for document in documents:
        matchesStatus = selectedStatus == "Todos"
        if selectedStatus == "Processados":
            matchesStatus = document.get("status") == "Processado"
        if selectedStatus == "Com Pendencia":
            matchesStatus = document.get("status") == "Com Pendencia"

        searchableText = " ".join(
            [
                str(document.get("file_name") or ""),
                str(document.get("client_name") or ""),
                str(document.get("seller_name") or ""),
            ]
        ).lower()
        matchesSearch = not normalizedSearchTerm or normalizedSearchTerm in searchableText

        if matchesStatus and matchesSearch:
            filteredDocuments.append(document)

    return filteredDocuments


def _getSelectedDocument(documents: list[dict[str, object]]) -> dict[str, object] | None:
    selectedFileName = st.session_state.get("selected_document")
    if not selectedFileName:
        return None

    for document in documents:
        if document.get("file_name") == selectedFileName:
            return document

    return None
