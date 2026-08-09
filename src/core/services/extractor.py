from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from core.config import SYSTEM_INSTRUCTION, USER_EXTRACTION_PROMPT, getSettings
from core.schemas.budget_schema import OrcamentoSchema
from core.services.storage_service import sanitize_file_name

try:
    from google import genai
    from google.genai import types
except ImportError as error:  # pragma: no cover
    genai = None
    types = None
    _GENAI_IMPORT_ERROR = error
else:
    _GENAI_IMPORT_ERROR = None


class BudgetExtractionError(Exception):
    """Raised when the PDF structured extraction cannot be completed."""


def extract_budget_data(
    pdf_path: str,
    model_name: str | None = None,
    temperature: float | None = None,
) -> OrcamentoSchema:
    """
    Extract structured budget data from a PDF using Google Gemini.

    Args:
        pdf_path: Local path to the PDF file to be processed.
        model_name: Optional Gemini model override.
        temperature: Optional sampling temperature override.

    Returns:
        A validated `OrcamentoSchema` instance with the extracted fields.

    Raises:
        BudgetExtractionError: If the file is invalid, the API call fails or the
            structured response cannot be validated.
    """
    if genai is None or types is None:
        raise BudgetExtractionError(
            "A dependencia google-genai nao esta instalada ou nao pode ser importada. "
            f"Detalhe tecnico: {_GENAI_IMPORT_ERROR}"
        ) from _GENAI_IMPORT_ERROR

    resolvedPdfPath = Path(pdf_path).expanduser().resolve()
    if not resolvedPdfPath.exists():
        raise BudgetExtractionError(f"O arquivo PDF nao foi encontrado: {resolvedPdfPath}")

    if not resolvedPdfPath.is_file():
        raise BudgetExtractionError(f"O caminho informado nao e um arquivo: {resolvedPdfPath}")

    if resolvedPdfPath.suffix.lower() != ".pdf":
        raise BudgetExtractionError("O arquivo informado deve possuir extensao .pdf")

    settings = getSettings()
    if not settings.geminiApiKey:
        raise BudgetExtractionError(
            "A variavel GEMINI_API_KEY nao foi encontrada apos carregar o arquivo .env. "
            "Verifique se o arquivo .env existe na raiz do projeto e se contem GEMINI_API_KEY."
        )

    uploadedFile = None
    response = None
    safeDisplayName = sanitize_file_name(file_name=resolvedPdfPath.name)
    effectiveModelName = model_name or settings.geminiModelName
    effectiveTemperature = settings.geminiTemperature if temperature is None else temperature

    try:
        client = genai.Client(api_key=settings.geminiApiKey)
        uploadedFile = client.files.upload(
            file=str(resolvedPdfPath),
            config={
                "mime_type": "application/pdf",
                "display_name": safeDisplayName,
            },
        )
        response = client.models.generate_content(
            model=effectiveModelName,
            contents=[USER_EXTRACTION_PROMPT, uploadedFile],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=effectiveTemperature,
                response_mime_type="application/json",
                response_schema=OrcamentoSchema,
            ),
        )
    except Exception as error:
        raise BudgetExtractionError(
            f"Falha ao extrair dados estruturados do PDF com o Gemini: {type(error).__name__}: {error}"
        ) from error
    finally:
        if uploadedFile is not None:
            try:
                client.files.delete(name=uploadedFile.name)
            except Exception as cleanupError:
                print(
                    "Aviso ao limpar arquivo temporario no Gemini: "
                    f"{type(cleanupError).__name__}: {cleanupError}"
                )

    responseText = getattr(response, "text", None)
    if not responseText:
        raise BudgetExtractionError("O Gemini nao retornou conteudo estruturado no campo text.")

    try:
        return OrcamentoSchema.model_validate_json(responseText)
    except ValidationError as error:
        raise BudgetExtractionError(
            f"A resposta estruturada do Gemini nao corresponde ao schema esperado: {error}"
        ) from error
