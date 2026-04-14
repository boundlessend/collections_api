from uuid import UUID

from sqlalchemy import Select, delete, exists, func, select
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
    "created_asc": CollectionBookmark.created_at.asc(),
    "created_desc": CollectionBookmark.created_at.desc(),
    "title_asc": Bookmark.title.asc(),
    "title_desc": Bookmark.title.desc(),
    "url_asc": Bookmark.url.asc(),
    "url_desc": Bookmark.url.desc(),
}


def cleanup_orphan_bookmarks(db: Session) -> None:
    """удаляет статьи без коллекций"""

    db.execute(
        delete(Bookmark).where(
            ~exists(
                select(CollectionBookmark.bookmark_id).where(
                    CollectionBookmark.bookmark_id == Bookmark.id,
                )
            )
        )
    )


def create_collection(db: Session, *, name: str) -> Collection:
    """создаёт коллекцию"""

    collection = Collection(name=name)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def get_collection_or_404(db: Session, collection_id: UUID) -> Collection:
    """возвращает коллекцию или выбрасывает 404"""

    collection = db.get(Collection, collection_id)
    if collection is None:
        raise CollectionNotFound(collection_id)
    return collection


def update_collection_name(
    db: Session, *, collection_id: UUID, name: str
) -> Collection:
    """обновляет имя коллекции"""

    collection = get_collection_or_404(db, collection_id)
    collection.name = name
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, *, collection_id: UUID) -> None:
    """удаляет коллекцию"""

    collection = get_collection_or_404(db, collection_id)
    db.delete(collection)
    db.flush()
    cleanup_orphan_bookmarks(db)
    db.commit()


def list_collections(
    db: Session, *, page: int, size: int
) -> tuple[list[Collection], int]:
    """возвращает коллекции с пагинацией"""

    total = db.scalar(select(func.count(Collection.id))) or 0
    stmt = (
        select(Collection)
        .order_by(Collection.created_at.asc(), Collection.name.asc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = db.scalars(stmt).all()
    return items, total


def add_bookmark_to_collection(
    db: Session,
    *,
    collection_id: UUID,
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
    collection_id: UUID,
    sort: BookmarkSort,
) -> tuple[Collection, list[Bookmark]]:
    """возвращает статьи коллекции с сортировкой"""

    collection = get_collection_or_404(db, collection_id)
    sort_expression = SORT_MAPPING[sort]
    stmt: Select[tuple[Bookmark]] = (
        select(Bookmark)
        .join(
            CollectionBookmark, CollectionBookmark.bookmark_id == Bookmark.id
        )
        .where(CollectionBookmark.collection_id == collection.id)
        .order_by(sort_expression, Bookmark.title.asc(), Bookmark.url.asc())
    )
    items = db.scalars(stmt).all()
    return collection, items


def delete_bookmark_from_collection(
    db: Session, *, collection_id: UUID, bookmark_id: UUID
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
    db.flush()
    cleanup_orphan_bookmarks(db)
    db.commit()
