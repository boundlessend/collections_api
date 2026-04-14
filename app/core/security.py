import secrets

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.exceptions import AuthRequired, InvalidAuthToken

bearer_scheme = HTTPBearer(auto_error=False)


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> None:
    """проверяет bearer token для доступа к api"""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthRequired()

    if not secrets.compare_digest(
        credentials.credentials, settings.auth_token
    ):
        raise InvalidAuthToken()
