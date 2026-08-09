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

DEFAULT_GEMINI_MODEL_NAME = "gemini-3.6-flash"


@dataclass(slots=True)
class AppSettings:
    geminiApiKey: str
    geminiModelName: str
    geminiTemperature: float
    storageDir: Path
    minLoadingTimeSeconds: float
    databaseUrl: str
    chromaPersistDirectory: Path


def get_secret(key_name: str, default: str | None = None) -> str | None:
    """
    Resolve a secret using environment variables first and Streamlit secrets second.

    Search precedence:
    1. Environment variables / .env
    2. Streamlit secrets
    3. Provided default
    """
    load_dotenv()

    environmentValue = os.getenv(key_name)
    if environmentValue is not None and environmentValue.strip():
        return environmentValue.strip()

    try:
        import streamlit as st

        secretValue = st.secrets.get(key_name)
        if secretValue is not None and str(secretValue).strip():
            return str(secretValue).strip()
    except Exception:
        pass

    return default


def getSettings() -> AppSettings:
    """Load project settings from environment variables with safe defaults."""
    load_dotenv()

    geminiApiKey = get_secret("GEMINI_API_KEY", default="")
    geminiModelName = os.getenv("GEMINI_MODEL_NAME", DEFAULT_GEMINI_MODEL_NAME).strip()
    geminiTemperature = _parseFloat(
        value=os.getenv("GEMINI_TEMPERATURE", "0.0"),
        default=0.0,
    )
    storageDir = Path(os.getenv("STORAGE_DIR", "storage/pdfs")).expanduser()
    minLoadingTimeSeconds = _parseFloat(
        value=os.getenv("MIN_LOADING_TIME_SECONDS", "3.0"),
        default=3.0,
    )
    databaseUrl = os.getenv("DATABASE_URL", "sqlite:///storage/app.db").strip()
    chromaPersistDirectory = Path(
        os.getenv("CHROMA_PERSIST_DIR", "storage/chroma")
    ).expanduser()

    return AppSettings(
        geminiApiKey=geminiApiKey,
        geminiModelName=geminiModelName or DEFAULT_GEMINI_MODEL_NAME,
        geminiTemperature=geminiTemperature,
        storageDir=storageDir,
        minLoadingTimeSeconds=minLoadingTimeSeconds,
        databaseUrl=databaseUrl or "sqlite:///storage/app.db",
        chromaPersistDirectory=chromaPersistDirectory,
    )


def _parseFloat(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def requireGeminiApiKey() -> str:
    """
    Return the Gemini API key or raise a setup-oriented error.

    Use this helper during application/service initialization whenever Gemini is mandatory.
    """
    geminiApiKey = getSettings().geminiApiKey
    if geminiApiKey:
        return geminiApiKey

    raise ValueError(
        "GEMINI_API_KEY nao foi encontrada. Configure a chave em um arquivo .env "
        "na raiz do projeto ou em .streamlit/secrets.toml antes de iniciar a aplicacao."
    )
