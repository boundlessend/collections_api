from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import moscow_now
from app.db.base import Base


class CollectionBookmark(Base):
    """связь коллекции и статьи"""

    __tablename__ = "collection_bookmarks"
    __table_args__ = (
        UniqueConstraint(
            "collection_id", "bookmark_id", name="uq_collection_bookmark_pair"
        ),
    )

    collection_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bookmark_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("bookmarks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=moscow_now,
        nullable=False,
    )


class Collection(Base):
    """коллекция статей"""

    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=moscow_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=moscow_now,
        onupdate=moscow_now,
        nullable=False,
    )

    bookmarks: Mapped[List[Bookmark]] = relationship(
        secondary="collection_bookmarks",
        back_populates="collections",
        lazy="selectin",
    )


class Bookmark(Base):
    """статья-закладка"""

    __tablename__ = "bookmarks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=moscow_now,
        nullable=False,
    )

    collections: Mapped[List[Collection]] = relationship(
        secondary="collection_bookmarks",
        back_populates="bookmarks",
        lazy="selectin",
    )
