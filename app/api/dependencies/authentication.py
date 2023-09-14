from starlette.status import HTTP_403_FORBIDDEN
from app.models.user_type_model import UserType
from typing import List, Optional

from app.api.dependencies.db import get_db
from app.core.errors.error_strings import (
    AUTHENTICATION_REQUIRED,
    INACTIVE_USER_ERROR,
    MALFORMED_PAYLOAD,
    WRONG_TOKEN_PREFIX,
)
from app.core.errors.exceptions import (
    DisallowedLoginException,
    InvalidTokenException,
    UnauthorizedEndpointException,
)
from app.core.settings.config import settings
from app.models.user_model import User
from app.repositories.user_repo import user_repo
from app.core.services.jwt import get_id_from_token
from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    APIKeyHeader as DefaultAPIKeyHeader,
)
from loguru import logger
from sqlalchemy.orm import Session
from starlette import requests
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import error_strings

JWT_TOKEN_PREFIX = settings.JWT_TOKEN_PREFIX
HEADER_KEY = settings.HEADER_KEY


SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE
COMMISSIONER_USER_TYPE=settings.COMMISSIONER_USER_TYPE






class JWTHeader(DefaultAPIKeyHeader):
    async def __call__(
        _,
        request: requests.Request,
    ) -> Optional[str]:
        try:
            return await super().__call__(request)
        except StarletteHTTPException as original_auth_exc:
            raise HTTPException(
                status_code=original_auth_exc.status_code,
                detail=original_auth_exc.detail or AUTHENTICATION_REQUIRED,
            )


def _extract_jwt_from_header(
    authorization_header: str = Security(JWTHeader(name=HEADER_KEY)),
) -> str:
    try:
        token_prefix, token = authorization_header.split(" ")
    except ValueError:
        raise InvalidTokenException(detail=WRONG_TOKEN_PREFIX)

    if token_prefix != JWT_TOKEN_PREFIX:
        raise InvalidTokenException(detail=WRONG_TOKEN_PREFIX)
    return token


def get_currently_authenticated_user(
    *,
    db: Session = Depends(get_db),
    token: str = Depends(_extract_jwt_from_header),
) -> User:
    try:
        id = get_id_from_token(token)
        user = user_repo.get(db, id=id)
        check_if_user_is_valid(user)
    except ValueError:
        raise InvalidTokenException(detail=MALFORMED_PAYLOAD)
    return user


def check_if_user_is_valid(user: User):
    if not user:
        raise InvalidTokenException(detail=MALFORMED_PAYLOAD)
    if not user.is_active:
        raise DisallowedLoginException(detail=INACTIVE_USER_ERROR)


class PermissionChecker:
    def __init__(self, *, allowed_user_types: List[str]):
        self.allowed_user_types = allowed_user_types

    def __call__(self, user: User = Depends(get_currently_authenticated_user)):
        current_user_type: UserType = user.user_type
        if current_user_type.name not in self.allowed_user_types:
            logger.debug(
                f"User with type {current_user_type.name} not in {self.allowed_user_types}"
            )
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=error_strings.UNAUTHORIZED_ACTION
            )


superuser_permission_dependency = PermissionChecker(
    allowed_user_types=[SUPERUSER_USER_TYPE]
)

manager_and_supervisor_and_superuser_permission_dependency = PermissionChecker(
    allowed_user_types=[SUPERUSER_USER_TYPE]
)

commissioner_permission_dependency = PermissionChecker(
    allowed_user_types=[COMMISSIONER_USER_TYPE]
)