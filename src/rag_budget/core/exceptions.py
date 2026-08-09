class RagBudgetError(Exception):
    """Base application exception."""


class ValidationError(RagBudgetError):
    """Raised when business validation fails."""


class StorageError(RagBudgetError):
    """Raised when a file cannot be persisted."""


class LlmIntegrationError(RagBudgetError):
    """Raised when the LLM provider fails."""
