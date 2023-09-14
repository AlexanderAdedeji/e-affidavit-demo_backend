from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies.authentication import get_currently_authenticated_user
from app.api.dependencies.db import get_db
from app.core.errors.exceptions import AlreadyExistsException, ServerException
from app.repositories.user_repo import user_repo
from app.repositories.user_type_repo import user_type_repo
from app.core.settings.config import Settings
from app.schemas.user_schema import UserCreate, UserInResponse,UserCreateForm
from app.schemas.user_type_schema import UserTypeInDB


router = APIRouter()

settings = Settings()
COMMISSIONER_USER_TYPE = settings.COMMISSIONER_USER_TYPE
REGULAR_USER_TYPE = settings.REGULAR_USER_TYPE
VERIFIER_USER_TYPE = settings.VERIFIER_USER_TYPE


def check_unique_user(db: Session, user_in: UserCreateForm):
    user_with_same_email = user_repo.get_by_email(db, email=user_in.email)
    if user_with_same_email:
        raise AlreadyExistsException(
            entity_name="user with email {}".format(user_in.email)
        )

    # user_with_same_phone = user_repo.get_by_field(
    #     db, field_name="phone", field_value=user_in.phone
    # )
    # if user_with_same_phone:
    #     raise AlreadyExistsException(
    #         entity_name="user with phone {}".format(user_in.phone)
    #     )


@router.get("/user_default")
def user_default(current_user=Depends(get_currently_authenticated_user)):
    return {"msg": "User default"}


@router.post("/user_create")
def user_create(
    user_in: UserCreateForm,
    db: Session = Depends(get_db),
):
    check_unique_user(db, user_in)
    user_type = user_type_repo.get_by_name(db, name=REGULAR_USER_TYPE)

    if not user_type:
        raise ServerException()
    user = user_repo.create(
        db,
        obj_in=UserCreate(**user_in.dict(), user_type_id=user_type.id),
    )

    return UserInResponse(
        id=user.id,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user.is_active,
        user_type=UserTypeInDB(id=user_type.id, name=user_type.name),
    )




@router.post("/commissioner_create")
def commissioner_create(
    user_in: UserCreateForm,
    db: Session = Depends(get_db),
):
    check_unique_user(db, user_in)
    user_type = user_type_repo.get_by_name(db, name=COMMISSIONER_USER_TYPE)

    if not user_type:
        raise ServerException()
    user = user_repo.create(
        db,
        obj_in=UserCreate(**user_in.dict(), user_type_id=user_type.id),
    )

    return UserInResponse(
        id=user.id,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user.is_active,
        user_type=UserTypeInDB(id=user_type.id, name=user_type.name),
    )


@router.post("/verifier_create")
def verifier_create(
    user_in: UserCreateForm,
    db: Session = Depends(get_db),
):
    check_unique_user(db, user_in)
    user_type = user_type_repo.get_by_name(db, name=VERIFIER_USER_TYPE)

    if not user_type:
        raise ServerException()
    user = user_repo.create(
        db,
        obj_in=UserCreate(**user_in.dict(), user_type_id=user_type.id),
    )

    return UserInResponse(
        id=user.id,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user.is_active,
        user_type=UserTypeInDB(id=user_type.id, name=user_type.name),
    )
