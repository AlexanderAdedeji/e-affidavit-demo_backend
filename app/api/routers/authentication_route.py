from app.core.settings.config import settings
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from app.api.dependencies.db import get_db
from app.core.errors import error_strings
from app.core.errors.exceptions import (
    DisallowedLoginException,
    IncorrectLoginException,
)

from app.repositories.user_repo import user_repo
from app.schemas.user_schema import UserInLogin, UserWithToken
from app.schemas.user_type_schema import UserTypeInDB
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session


SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE


router = APIRouter()


@router.post(
    "/login",
    response_model=UserWithToken,
    name="Login",
)
def login(
    db: Session = Depends(get_db),
    user_login: UserInLogin = Body(..., alias="user"),
) -> UserWithToken:
    """
    This route expects you to supply your credentials and if valid, returns a JWT for you to use to authenticate future requests.
    Only superusers,agent's managers and agent's supervisors are allowed to log in.
    """

    user = user_repo.get_by_email(db, email=user_login.email)

    if user is None or not user.verify_password(user_login.password):
        raise IncorrectLoginException()

    # if user.user_type.name not in [SUPERUSER_USER_TYPE]:
    #     raise HTTPException(
    #         status_code=HTTP_403_FORBIDDEN, detail=error_strings.UNAUTHORIZED_ACTION
    #     )

    if not user.is_active:
        raise DisallowedLoginException(detail=error_strings.INACTIVE_USER_ERROR)

    token = user.generate_jwt()
    return UserWithToken(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        token=token,
        user_type=UserTypeInDB(id=user.user_type_id, name=user.user_type.name),
    )
