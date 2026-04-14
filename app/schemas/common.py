from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer

from app.core.time import to_moscow


class APIModel(BaseModel):
    """базовая схема api"""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MoscowTimeModel(APIModel):
    """схема с сериализацией времени по москве"""

    @field_serializer("created_at", "updated_at", check_fields=False)
    def serialize_datetime(self, value: datetime) -> str:
        """сериализует время в московском часовом поясе"""

        return to_moscow(value).isoformat()


class ErrorDetails(APIModel):
    """детали ошибки"""

    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(APIModel):
    """обёртка для ответа с ошибкой"""

    error: ErrorDetails


class MessageResponse(APIModel):
    """ответ с сообщением"""

    message: str
