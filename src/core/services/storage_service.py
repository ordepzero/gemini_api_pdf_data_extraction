from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import re
import unicodedata

from core.config import getSettings


class StorageServiceError(Exception):
    """Raised when the uploaded file cannot be validated or persisted."""


@dataclass(slots=True)
class SavedFileInfo:
    """Represents the result of a persisted uploaded file."""

    original_name: str
    sanitized_name: str
    final_name: str
    file_path: str
    was_renamed: bool
    was_sanitized: bool

    def toDict(self) -> dict[str, Any]:
        """Return the result as a serializable dictionary."""
        return asdict(self)


@dataclass(slots=True)
class SanitizedFileNameInfo:
    """Represents the sanitized filename preview before persistence."""

    original_name: str
    sanitized_name: str
    was_sanitized: bool

    def toDict(self) -> dict[str, Any]:
        """Return the preview as a serializable dictionary."""
        return asdict(self)


def save_uploaded_file(
    uploaded_file: Any,
    target_dir: str | None = None,
    confirmed_file_name: str | None = None,
) -> dict[str, Any]:
    """
    Persist a single uploaded PDF to disk, renaming duplicates incrementally.

    Args:
        uploaded_file: Streamlit UploadedFile-like object.
        target_dir: Base directory where the PDF will be stored.

    Returns:
        A dictionary with the original name, final name, full path and rename flag.

    Raises:
        StorageServiceError: If the file is invalid or cannot be written.
    """
    if uploaded_file is None:
        raise StorageServiceError("Nenhum arquivo foi enviado.")

    fileNameInfo = preview_sanitized_file_name(uploaded_file=uploaded_file)
    original_name = str(fileNameInfo["original_name"])
    sanitized_name = str(fileNameInfo["sanitized_name"])
    was_sanitized = bool(fileNameInfo["was_sanitized"])

    resolvedTargetDir = target_dir or str(getSettings().storageDir)
    target_path = Path(resolvedTargetDir)

    try:
        target_path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise StorageServiceError(
            f"Nao foi possivel criar o diretorio de armazenamento: {error}"
        ) from error

    preferred_name = confirmed_file_name or sanitized_name
    if Path(preferred_name).suffix.lower() != ".pdf":
        raise StorageServiceError("O nome final do arquivo deve preservar a extensao .pdf.")

    final_name, was_renamed = _buildAvailableFileName(
        directory=target_path,
        original_name=preferred_name,
    )
    final_path = target_path / final_name

    try:
        file_bytes = uploaded_file.getbuffer()
        with final_path.open("wb") as file_pointer:
            file_pointer.write(file_bytes)
    except OSError as error:
        raise StorageServiceError(
            f"Nao foi possivel salvar o arquivo em disco: {error}"
        ) from error
    except Exception as error:
        raise StorageServiceError(
            f"Falha ao processar o arquivo enviado: {error}"
        ) from error

    saved_file_info = SavedFileInfo(
        original_name=original_name,
        sanitized_name=sanitized_name,
        final_name=final_name,
        file_path=str(final_path.resolve()),
        was_renamed=was_renamed,
        was_sanitized=was_sanitized,
    )
    return saved_file_info.toDict()


def preview_sanitized_file_name(uploaded_file: Any) -> dict[str, Any]:
    """Preview the sanitized ASCII-safe file name without persisting the file."""
    if uploaded_file is None:
        raise StorageServiceError("Nenhum arquivo foi enviado.")

    original_name = Path(str(getattr(uploaded_file, "name", ""))).name
    if not original_name:
        raise StorageServiceError("O arquivo enviado nao possui um nome valido.")

    if Path(original_name).suffix.lower() != ".pdf":
        raise StorageServiceError("Apenas arquivos PDF sao permitidos.")

    sanitized_name = sanitize_file_name(file_name=original_name)

    fileNameInfo = SanitizedFileNameInfo(
        original_name=original_name,
        sanitized_name=sanitized_name,
        was_sanitized=sanitized_name != original_name,
    )
    return fileNameInfo.toDict()


def sanitize_file_name(file_name: str) -> str:
    """Remove accents and special characters, preserving a safe .pdf file name."""
    originalPath = Path(file_name)
    normalizedStem = unicodedata.normalize("NFKD", originalPath.stem)
    asciiStem = normalizedStem.encode("ascii", "ignore").decode("ascii")
    safeStem = re.sub(r"[^A-Za-z0-9._-]+", "_", asciiStem).strip("._-")

    if not safeStem:
        safeStem = "arquivo"

    suffix = originalPath.suffix.lower() or ".pdf"
    return f"{safeStem}{suffix}"


def _buildAvailableFileName(directory: Path, original_name: str) -> tuple[str, bool]:
    """Return a non-conflicting filename preserving the .pdf extension."""
    candidate_path = directory / original_name
    if not candidate_path.exists():
        return original_name, False

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    counter = 1

    while True:
        candidate_name = f"{stem}_{counter}{suffix}"
        candidate_path = directory / candidate_name
        if not candidate_path.exists():
            return candidate_name, True
        counter += 1
