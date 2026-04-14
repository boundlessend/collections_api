from datetime import datetime
from math import ceil
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.bookmark import BookmarkRead
from app.schemas.common import MessageResponse, MoscowTimeModel

BookmarkSort = Literal[
    "created_asc",
    "created_desc",
    "title_asc",
    "title_desc",
    "url_asc",
    "url_desc",
]


class CollectionCreate(MoscowTimeModel):
    """схема создания коллекции"""

    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """нормализует имя коллекции"""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Collection name must not be blank")
        return normalized


class CollectionUpdate(MoscowTimeModel):
    """схема обновления коллекции"""

    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """нормализует новое имя коллекции"""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Collection name must not be blank")
        return normalized


class CollectionRead(MoscowTimeModel):
    """схема коллекции в ответе"""

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class CollectionsPage(MoscowTimeModel):
    """страница коллекций"""

    items: list[CollectionRead]
    page: int
    size: int
    total: int
    pages: int

    @classmethod
    def build(
        cls,
        *,
        items: list[CollectionRead],
        page: int,
        size: int,
        total: int,
    ) -> "CollectionsPage":
        """собирает ответ с пагинацией"""

        return cls(
            items=items,
            page=page,
            size=size,
            total=total,
            pages=ceil(total / size) if total else 0,
        )


class CollectionBookmarksRead(MoscowTimeModel):
    """список статей внутри коллекции"""

    collection_id: UUID
    collection_name: str
    sort: BookmarkSort
    total: int
    items: list[BookmarkRead]


class DeleteResult(MessageResponse):
    """ответ после удаления сущности"""
