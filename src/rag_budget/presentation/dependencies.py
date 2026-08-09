from rag_budget.application.services import QuoteExtractionService, UploadService
from rag_budget.core.config import AppSettings
from rag_budget.infrastructure.file_storage import LocalFileStorageGateway
from rag_budget.infrastructure.gemini_gateway import GeminiGateway


def getSettings() -> AppSettings:
    return AppSettings.fromEnvironment()


def getUploadService() -> UploadService:
    settings = getSettings()
    fileStorageGateway = LocalFileStorageGateway(baseDirectory=settings.uploadBaseDirectory)
    return UploadService(fileStorageGateway=fileStorageGateway)


def getQuoteExtractionService() -> QuoteExtractionService:
    settings = getSettings()
    llmGateway = GeminiGateway(apiKey=settings.geminiApiKey)
    return QuoteExtractionService(llmGateway=llmGateway)
