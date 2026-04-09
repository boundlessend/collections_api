from datetime import datetime

from pydantic import Field, HttpUrl, field_validator

from app.schemas.common import APIModel


class BookmarkCreate(APIModel):
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


class BookmarkRead(APIModel):
    """схема статьи в ответе"""

    id: int
    title: str
    url: str
    created_at: datetime
