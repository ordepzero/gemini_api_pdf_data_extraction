from pathlib import Path

import streamlit as st

from rag_budget.core.exceptions import RagBudgetError
from rag_budget.domain.models import UploadRequest
from rag_budget.presentation.dependencies import getSettings, getUploadService
from rag_budget.presentation.view_models import UploadFeedback


def buildUploadRequest() -> UploadRequest | None:
    uploadedFile = st.file_uploader(
        "Selecione um PDF",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if uploadedFile is None:
        return None

    return UploadRequest(
        fileName=uploadedFile.name,
        fileBytes=uploadedFile.getvalue(),
        contentType=uploadedFile.type or "application/pdf",
    )


def handleUpload() -> UploadFeedback | None:
    uploadRequest = buildUploadRequest()

    if uploadRequest is None:
        st.info("Aguardando o envio de um arquivo PDF.")
        return None

    if not st.button("Salvar arquivo", type="primary", icon=":material/upload_file:"):
        return None

    try:
        uploadResult = getUploadService().uploadPdf(uploadRequest=uploadRequest)
    except RagBudgetError as error:
        return UploadFeedback(
            success=False,
            title="Falha no upload",
            message=str(error),
        )
    except Exception as error:
        return UploadFeedback(
            success=False,
            title="Erro inesperado",
            message=f"Ocorreu um erro inesperado: {error}",
        )

    storedPath = Path(uploadResult.storedPath)
    return UploadFeedback(
        success=True,
        title="Arquivo salvo com sucesso",
        message=(
            f"Nome original: {uploadResult.originalFileName}\n"
            f"Caminho salvo: {storedPath}\n"
            f"Tamanho: {uploadResult.fileSizeInBytes} bytes"
        ),
    )

def renderPage() -> None:
    st.set_page_config(
        page_title="Upload de PDF",
        page_icon=":material/upload_file:",
        layout="centered",
    )

    settings = getSettings()

    st.title("Upload de arquivo PDF")
    st.caption(
        "O arquivo original sera salvo localmente em um subdiretorio no formato anomesdia."
    )

    with st.container(border=True):
        st.write(f"Diretorio base de upload: `{settings.uploadBaseDirectory}`")
        feedback = handleUpload()

    if feedback is not None:
        if feedback.success:
            st.success(feedback.title)
            st.code(feedback.message)
        else:
            st.error(feedback.title)
            st.write(feedback.message)
