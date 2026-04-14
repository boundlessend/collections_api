from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.routes.collections import router as collections_router
from app.core.config import get_settings
from app.exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(collections_router, prefix=settings.api_prefix)
