from os import getenv
from pathlib import Path

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    projectName: str = Field(default="rag-budget")
    uploadBaseDirectory: Path = Field(default=Path("uploads"))
    geminiApiKey: str = Field(default="")
    geminiModelName: str = Field(default="gemini-3.6-flash")

    @classmethod
    def fromEnvironment(cls) -> "AppSettings":
        return cls(
            projectName=getenv("RAG_BUDGET_PROJECT_NAME", "rag-budget"),
            uploadBaseDirectory=Path(getenv("RAG_BUDGET_UPLOAD_DIR", "uploads")),
            geminiApiKey=getenv("GEMINI_API_KEY", ""),
            geminiModelName=getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash"),
        )
