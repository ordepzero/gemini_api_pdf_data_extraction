from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


SYSTEM_INSTRUCTION = (
    "Voce e um extrator estruturado de orcamentos em PDF. "
    "Extraia os dados com maxima fidelidade ao documento. "
    "Converta textos monetarios para numeros float usando apenas o valor numerico. "
    "Extraia materiais, especificacoes tecnicas, bitolas, espessuras, medidas e dimensoes exatamente como aparecem. "
    "Nao invente informacoes ausentes. Quando um campo nao existir, retorne null. "
    "Preencha a lista de itens com o maximo de detalhamento tecnico encontrado."
)

USER_EXTRACTION_PROMPT = (
    "Analise o PDF anexado e retorne exclusivamente um JSON valido aderente ao schema informado. "
    "Extraia cliente, vendedor, itens, totais e observacoes gerais do orcamento."
)


@dataclass(slots=True)
class AppSettings:
    geminiApiKey: str
    geminiModelName: str
    geminiTemperature: float
    storageDir: Path
    minLoadingTimeSeconds: float
    databaseUrl: str
    chromaPersistDirectory: Path


def getSettings() -> AppSettings:
    """Load project settings from environment variables with safe defaults."""
    load_dotenv()

    geminiApiKey = os.getenv("GEMINI_API_KEY", "").strip()
    geminiModelName = os.getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash").strip()
    geminiTemperature = _parseFloat(
        value=os.getenv("GEMINI_TEMPERATURE", "0.0"),
        default=0.0,
    )
    storageDir = Path(os.getenv("STORAGE_DIR", "storage/pdfs")).expanduser()
    minLoadingTimeSeconds = _parseFloat(
        value=os.getenv("MIN_LOADING_TIME_SECONDS", "3.0"),
        default=3.0,
    )
    databaseUrl = os.getenv("DATABASE_URL", "sqlite:///storage/rag_budget.db").strip()
    chromaPersistDirectory = Path(
        os.getenv("CHROMA_PERSIST_DIR", "storage/chroma")
    ).expanduser()

    return AppSettings(
        geminiApiKey=geminiApiKey,
        geminiModelName=geminiModelName or "gemini-3.6-flash",
        geminiTemperature=geminiTemperature,
        storageDir=storageDir,
        minLoadingTimeSeconds=minLoadingTimeSeconds,
        databaseUrl=databaseUrl or "sqlite:///storage/rag_budget.db",
        chromaPersistDirectory=chromaPersistDirectory,
    )


def _parseFloat(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
