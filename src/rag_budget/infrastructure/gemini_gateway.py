from typing import Any

from rag_budget.core.exceptions import LlmIntegrationError
from rag_budget.domain.models import LlmExtractRequest, LlmExtractResult

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


class GeminiGateway:
    def __init__(self, apiKey: str) -> None:
        self.apiKey = apiKey

    def extractStructuredContent(self, extractRequest: LlmExtractRequest) -> LlmExtractResult:
        if genai is None:
            raise LlmIntegrationError(
                "A dependencia google-genai nao esta disponivel no ambiente."
            )

        if not self.apiKey:
            raise LlmIntegrationError("A variavel GEMINI_API_KEY nao foi configurada.")

        try:
            client = genai.Client(api_key=self.apiKey)
            uploadedFile = client.files.upload(file=extractRequest.documentPath)
            response: Any = client.models.generate_content(
                model=extractRequest.modelName,
                contents=[uploadedFile, extractRequest.prompt],
            )
        except Exception as error:  # pragma: no cover
            raise LlmIntegrationError(f"Falha ao chamar o Gemini: {error}") from error

        responseText = getattr(response, "text", "") or ""

        return LlmExtractResult(
            modelName=extractRequest.modelName,
            rawText=responseText,
        )
