from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIException(HTTPException):
    """базовое исключение api"""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ):
        """собирает тело ошибки для клиента"""

        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details},
            headers=headers,
        )


class AuthRequired(APIException):
    """ошибка отсутствующей авторизации"""

    def __init__(self):
        """формирует ошибку для отсутствующего токена"""

        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            "authorization_required",
            "Authorization header with bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidAuthToken(APIException):
    """ошибка неверного токена"""

    def __init__(self):
        """формирует ошибку для неверного токена"""

        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            "invalid_token",
            "Provided bearer token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


class CollectionNotFound(APIException):
    """ошибка отсутствующей коллекции"""

    def __init__(self, collection_id: int):
        """формирует ошибку для несуществующей коллекции"""

        super().__init__(
            404,
            "collection_not_found",
            f"Collection with id={collection_id} was not found",
        )


class BookmarkNotFound(APIException):
    """ошибка отсутствующей статьи"""

    def __init__(self, bookmark_id: int):
        """формирует ошибку для несуществующей статьи"""

        super().__init__(
            404,
            "bookmark_not_found",
            f"Bookmark with id={bookmark_id} was not found",
        )


class BookmarkAlreadyInCollection(APIException):
    """ошибка повторного добавления статьи"""

    def __init__(self, collection_id: int, url: str):
        """формирует ошибку дубля внутри коллекции"""

        super().__init__(
            409,
            "bookmark_already_exists_in_collection",
            f"Bookmark with url={url} is already present in collection id={collection_id}",
        )


class BookmarkNotInCollection(APIException):
    """ошибка отсутствующей связи статьи и коллекции"""

    def __init__(self, collection_id: int, bookmark_id: int):
        """формирует ошибку для несвязанной статьи"""

        super().__init__(
            404,
            "bookmark_not_in_collection",
            f"Bookmark with id={bookmark_id} is not linked to collection id={collection_id}",
        )


async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
    """приводит кастомные исключения к общему формату"""

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers,
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """приводит ошибки валидации к общему формату"""

    details = []
    for error in exc.errors():
        details.append(
            {
                "field": ".".join(
                    str(item) for item in error.get("loc", [])[1:]
                )
                or "body",
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error"),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )
