from app.api.dependencies.authentication import (
    get_currently_authenticated_user,
    commissioner_permission_dependency,
)
from app.core.settings.config import settings
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from app.api.dependencies.db import get_db
from app.core.errors import error_strings
from app.core.errors.exceptions import (
    DisallowedLoginException,
    IncorrectLoginException,
)
from app.repositories.attesatation_repo import attestation_repo

from app.repositories.user_repo import user_repo
from app.schemas.attestation_schema import (
    AttestationBase,
    AttestationInResponse,
)
from app.schemas.user_schema import UserInLogin, UserWithToken
from app.schemas.user_type_schema import UserTypeInDB
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session


SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE


router = APIRouter()


@router.post(
    "/attestation_create",
    name="Attestation Create",
    dependencies=[Depends(commissioner_permission_dependency)],
)
def create_attestation(
    attestation_in: AttestationBase,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    try:
        attestation_exist = attestation_repo.get_by_user_id(db, user_id=current_user.id)

        if attestation_exist:
            new_attestation = attestation_repo.update(
                db, db_obj=attestation_exist, obj_in=attestation_in
            )
        else:
            attestation_obj = AttestationInResponse(
                user_id=current_user.id, **attestation_in.dict()
            )
            new_attestation = attestation_repo.create(db, obj_in=attestation_obj)

        return AttestationInResponse(
            user_id=new_attestation.user_id,
            signature=new_attestation.signature,
            stamp=new_attestation.stamp,
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get_attestation",
    name="Get Attestation",
    # response_model=AttestationInResponse,
    status_code=HTTP_200_OK,
    dependencies=[Depends(commissioner_permission_dependency)],
)
def get_attestation(
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    attestation_exist = attestation_repo.get_by_user_id(db, user_id=current_user.id)
    if not attestation_exist:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="You do not have any signature or stamp saved",
        )

    return AttestationInResponse(
        user_id=attestation_exist.user_id,
        signature=attestation_exist.signature,
        stamp=attestation_exist.stamp,
    )
