from typing import Any

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """базовая схема api"""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ErrorDetails(APIModel):
    """детали ошибки"""

    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(APIModel):
    """обёртка для ответа с ошибкой"""

    error: ErrorDetails
