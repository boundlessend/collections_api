from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl, field_validator

from app.schemas.common import MoscowTimeModel


class BookmarkCreate(MoscowTimeModel):
    """схема создания статьи"""

    title: str = Field(min_length=1, max_length=255)
    url: HttpUrl

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        """нормализует заголовок статьи"""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Title must not be blank")
        return normalized


class BookmarkRead(MoscowTimeModel):
    """схема статьи в ответе"""

    id: UUID
    title: str
    url: str
    created_at: datetime
