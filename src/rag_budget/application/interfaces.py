from typing import Protocol

from rag_budget.domain.models import LlmExtractRequest, LlmExtractResult, UploadRequest, UploadResult


class FileStorageGateway(Protocol):
    def savePdf(self, uploadRequest: UploadRequest) -> UploadResult:
        ...


class LlmGateway(Protocol):
    def extractStructuredContent(self, extractRequest: LlmExtractRequest) -> LlmExtractResult:
        ...
