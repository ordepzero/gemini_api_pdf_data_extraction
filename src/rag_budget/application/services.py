from rag_budget.application.interfaces import FileStorageGateway, LlmGateway
from rag_budget.core.exceptions import ValidationError
from rag_budget.domain.models import LlmExtractRequest, LlmExtractResult, UploadRequest, UploadResult
from rag_budget.domain.validators import validatePdfUpload


class UploadService:
    def __init__(self, fileStorageGateway: FileStorageGateway) -> None:
        self.fileStorageGateway = fileStorageGateway

    def uploadPdf(self, uploadRequest: UploadRequest) -> UploadResult:
        validatePdfUpload(uploadRequest=uploadRequest)
        return self.fileStorageGateway.savePdf(uploadRequest=uploadRequest)


class QuoteExtractionService:
    def __init__(self, llmGateway: LlmGateway) -> None:
        self.llmGateway = llmGateway

    def extractQuoteData(self, extractRequest: LlmExtractRequest) -> LlmExtractResult:
        if not extractRequest.documentPath.exists():
            raise ValidationError("O arquivo informado para extracao nao existe.")

        return self.llmGateway.extractStructuredContent(extractRequest=extractRequest)
