from pathlib import Path

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    fileName: str = Field(min_length=1)
    fileBytes: bytes = Field(min_length=1)
    contentType: str = Field(default="application/pdf")


class UploadResult(BaseModel):
    originalFileName: str
    sanitizedFileName: str
    storedPath: Path
    directoryName: str
    fileSizeInBytes: int = Field(ge=0)


class LlmExtractRequest(BaseModel):
    prompt: str = Field(min_length=1)
    documentPath: Path
    modelName: str = Field(min_length=1)


class LlmExtractResult(BaseModel):
    modelName: str
    rawText: str
