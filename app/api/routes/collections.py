from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.db.session import get_db
from app.schemas.bookmark import BookmarkCreate, BookmarkRead
from app.schemas.collection import (
    BookmarkSort,
    CollectionBookmarksRead,
    CollectionCreate,
    CollectionRead,
    CollectionsPage,
    CollectionUpdate,
)
from app.schemas.common import ErrorResponse
from app.services.collections import (
    add_bookmark_to_collection,
    create_collection,
    delete_bookmark_from_collection,
    list_collection_bookmarks,
    list_collections,
    update_collection_name,
)

router = APIRouter(
    prefix="/collections",
    tags=["collections"],
    dependencies=[Depends(require_auth)],
)


@router.post(
    "",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_collection_endpoint(
    payload: CollectionCreate, db: Session = Depends(get_db)
) -> CollectionRead:
    """создаёт коллекцию через api"""

    collection = create_collection(db, name=payload.name)
    return CollectionRead.model_validate(collection)


@router.patch(
    "/{collection_id}",
    response_model=CollectionRead,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_collection_endpoint(
    collection_id: int,
    payload: CollectionUpdate,
    db: Session = Depends(get_db),
) -> CollectionRead:
    """обновляет имя коллекции через api"""

    collection = update_collection_name(
        db, collection_id=collection_id, name=payload.name
    )
    return CollectionRead.model_validate(collection)


@router.get(
    "",
    response_model=CollectionsPage,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def list_collections_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CollectionsPage:
    """возвращает список коллекций"""

    collections, total = list_collections(db, page=page, size=size)
    return CollectionsPage.build(
        items=[CollectionRead.model_validate(item) for item in collections],
        page=page,
        size=size,
        total=total,
    )


@router.post(
    "/{collection_id}/bookmarks",
    response_model=BookmarkRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def add_bookmark_endpoint(
    collection_id: int,
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
) -> BookmarkRead:
    """добавляет статью в коллекцию через api"""

    bookmark = add_bookmark_to_collection(
        db, collection_id=collection_id, payload=payload
    )
    return BookmarkRead.model_validate(bookmark)


@router.get(
    "/{collection_id}/bookmarks",
    response_model=CollectionBookmarksRead,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def list_bookmarks_endpoint(
    collection_id: int,
    sort: BookmarkSort = Query("created_at"),
    db: Session = Depends(get_db),
) -> CollectionBookmarksRead:
    """возвращает статьи внутри коллекции"""

    collection, bookmarks = list_collection_bookmarks(
        db, collection_id=collection_id, sort=sort
    )
    return CollectionBookmarksRead(
        collection_id=collection.id,
        collection_name=collection.name,
        sort=sort,
        total=len(bookmarks),
        items=[BookmarkRead.model_validate(item) for item in bookmarks],
    )


@router.delete(
    "/{collection_id}/bookmarks/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_bookmark_endpoint(
    collection_id: int,
    bookmark_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """удаляет статью из коллекции через api"""

    delete_bookmark_from_collection(
        db, collection_id=collection_id, bookmark_id=bookmark_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
