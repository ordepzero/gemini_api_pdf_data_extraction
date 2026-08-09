from rag_budget.core.exceptions import ValidationError
from rag_budget.domain.models import UploadRequest


def validatePdfUpload(uploadRequest: UploadRequest) -> None:
    lowerFileName = uploadRequest.fileName.lower()
    isPdfMimeType = uploadRequest.contentType == "application/pdf"
    hasPdfExtension = lowerFileName.endswith(".pdf")

    if not isPdfMimeType and not hasPdfExtension:
        raise ValidationError("Envie um arquivo PDF valido.")
