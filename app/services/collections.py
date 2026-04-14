from typing import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import Bookmark, Collection, CollectionBookmark
from app.exceptions import (
    BookmarkAlreadyInCollection,
    BookmarkNotFound,
    BookmarkNotInCollection,
    CollectionNotFound,
)
from app.schemas.bookmark import BookmarkCreate
from app.schemas.collection import BookmarkSort

SORT_MAPPING = {
    "created_at": CollectionBookmark.created_at.asc(),
    "-created_at": CollectionBookmark.created_at.desc(),
    "title": Bookmark.title.asc(),
    "-title": Bookmark.title.desc(),
    "url": Bookmark.url.asc(),
    "-url": Bookmark.url.desc(),
}


def create_collection(db: Session, *, name: str) -> Collection:
    """создаёт коллекцию"""

    collection = Collection(name=name)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def get_collection_or_404(db: Session, collection_id: int) -> Collection:
    """возвращает коллекцию или выбрасывает 404"""

    collection = db.get(Collection, collection_id)
    if collection is None:
        raise CollectionNotFound(collection_id)
    return collection


def update_collection_name(
    db: Session, *, collection_id: int, name: str
) -> Collection:
    """обновляет имя коллекции"""

    collection = get_collection_or_404(db, collection_id)
    collection.name = name
    db.commit()
    db.refresh(collection)
    return collection


def list_collections(
    db: Session, *, page: int, size: int
) -> tuple[Sequence[Collection], int]:
    """возвращает коллекции с пагинацией"""

    total = db.scalar(select(func.count(Collection.id))) or 0
    stmt = (
        select(Collection)
        .order_by(Collection.id.asc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = db.scalars(stmt).all()
    return items, total


def add_bookmark_to_collection(
    db: Session,
    *,
    collection_id: int,
    payload: BookmarkCreate,
) -> Bookmark:
    """добавляет статью в коллекцию"""

    collection = get_collection_or_404(db, collection_id)

    bookmark = db.scalar(
        select(Bookmark).where(Bookmark.url == str(payload.url))
    )
    created_new_bookmark = False
    if bookmark is None:
        bookmark = Bookmark(title=payload.title, url=str(payload.url))
        db.add(bookmark)
        db.flush()
        created_new_bookmark = True

    existing_link = db.scalar(
        select(CollectionBookmark).where(
            CollectionBookmark.collection_id == collection.id,
            CollectionBookmark.bookmark_id == bookmark.id,
        )
    )
    if existing_link is not None:
        if created_new_bookmark:
            db.rollback()
        raise BookmarkAlreadyInCollection(collection.id, bookmark.url)

    db.add(
        CollectionBookmark(
            collection_id=collection.id, bookmark_id=bookmark.id
        )
    )
    db.commit()
    db.refresh(bookmark)
    return bookmark


def list_collection_bookmarks(
    db: Session,
    *,
    collection_id: int,
    sort: BookmarkSort,
) -> tuple[Collection, Sequence[Bookmark]]:
    """возвращает статьи коллекции с сортировкой"""

    collection = get_collection_or_404(db, collection_id)
    sort_expression = SORT_MAPPING[sort]
    stmt: Select[tuple[Bookmark]] = (
        select(Bookmark)
        .join(
            CollectionBookmark, CollectionBookmark.bookmark_id == Bookmark.id
        )
        .where(CollectionBookmark.collection_id == collection.id)
        .order_by(sort_expression, Bookmark.id.asc())
    )
    items = db.scalars(stmt).all()
    return collection, items


def delete_bookmark_from_collection(
    db: Session, *, collection_id: int, bookmark_id: int
) -> None:
    """удаляет статью из коллекции"""

    get_collection_or_404(db, collection_id)

    bookmark = db.get(Bookmark, bookmark_id)
    if bookmark is None:
        raise BookmarkNotFound(bookmark_id)

    link = db.scalar(
        select(CollectionBookmark).where(
            CollectionBookmark.collection_id == collection_id,
            CollectionBookmark.bookmark_id == bookmark_id,
        )
    )
    if link is None:
        raise BookmarkNotInCollection(collection_id, bookmark_id)

    db.delete(link)
    db.commit()
