from datetime import datetime
from pathlib import Path
import re

from rag_budget.core.exceptions import StorageError
from rag_budget.domain.models import UploadRequest, UploadResult


class LocalFileStorageGateway:
    def __init__(self, baseDirectory: Path) -> None:
        self.baseDirectory = baseDirectory

    def savePdf(self, uploadRequest: UploadRequest) -> UploadResult:
        directoryName = datetime.now().strftime("%Y%m%d")
        targetDirectory = self.baseDirectory / directoryName
        sanitizedFileName = self.sanitizeFileName(fileName=uploadRequest.fileName)
        targetPath = targetDirectory / sanitizedFileName

        try:
            targetDirectory.mkdir(parents=True, exist_ok=True)
            targetPath.write_bytes(uploadRequest.fileBytes)
        except OSError as error:
            raise StorageError(f"Nao foi possivel salvar o arquivo: {error}") from error

        return UploadResult(
            originalFileName=uploadRequest.fileName,
            sanitizedFileName=sanitizedFileName,
            storedPath=targetPath,
            directoryName=directoryName,
            fileSizeInBytes=len(uploadRequest.fileBytes),
        )

    @staticmethod
    def sanitizeFileName(fileName: str) -> str:
        sanitizedName = re.sub(r"[^A-Za-z0-9._-]", "_", fileName)
        return sanitizedName or "arquivo.pdf"
