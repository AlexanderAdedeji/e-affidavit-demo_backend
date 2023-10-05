import string
import json
import random
from typing import List
import qrcode
from app.api.dependencies.authentication import (
    get_currently_authenticated_user,
    commissioner_permission_dependency,
)
from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from app.repositories.document_repo import document_repo
from app.core.errors.exceptions import (
    ObjectNotFoundException,
    UnauthorizedEndpointException,
)
from io import BytesIO
import logging
from app.api.dependencies.authentication import get_currently_authenticated_user

from app.core.settings import security
from app.schemas.document_schema import (
    AttestDocument,
    AttestDocumentCreate,
    DocumentBase,
    DocumentCreate,
    DocumentInResponse,
    DocumentQRCode,
    DocumentUpdate,
)
from app.api.dependencies.db import get_db

# Your own security module where convert_to_base_64 function resides
# from your_security_module import convert_to_base_64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def generate_random_string(length: int) -> str:
    try:
        letters = string.ascii_lowercase
        return "".join(random.sample(letters, length))
    except Exception as e:
        logger.error(f"Failed to generate random string: {e}")
        raise HTTPException(status_code=400, detail="Failed to generate random string")


def generate_qr_code(data: str) -> BytesIO:
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data.upper())
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered)
        return buffered
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        raise HTTPException(status_code=400, detail="Failed to generate QR code")


@router.post("/document_ref")
def generate_document_ref(
    document_id: str,
    current_user=Depends(get_currently_authenticated_user),
    db: Session = Depends(get_db),
):
    document = document_repo.get(db, id=document_id)
    if not document:
        raise ObjectNotFoundException(detail="this document was not found")
    if document.user_id != current_user.id:
        raise UnauthorizedEndpointException(
            detail="You are not the creator of this document"
        )

    if document.document_ref:
        raise UnauthorizedEndpointException(detail="This document already has a ref ID")
    if document.status != "PAID":
        raise UnauthorizedEndpointException(
            detail="You cannot generate a document ref without payment"
        )
    try:
        document_ref = generate_random_string(9)
        buffered = generate_qr_code(
            f"https://qr-searchDocument/{document_ref.upper()}"
        )
        img_str = security.convert_to_base_64(buffered.getvalue())
        document_repo.update(
            db,
            db_obj=document,
            obj_in=DocumentQRCode(document_ref=document_ref.upper(), qr_code=img_str),
        )
    except Exception as e:
        print(e)
        logger.error(f"Failed to generate document reference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return DocumentInResponse(
        id=document.id,
        document=document.document,
        template_name=document.template_name,
        document_ref=document.document_ref,
        user_id=document.user_id,
        status=document.status,
        document_data=json.loads(document.document_data),
        created_at=document.created_at,
        qr_code=document.qr_code,
    )


@router.post("/create_document")
def document_create(
    document: DocumentBase,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    document_in = document.dict()
    document_in["document_data"] = json.dumps(document_in["document_data"])
    document_in = dict(**document_in, user_id=current_user.id)
    document_obj = document_repo.create(db, obj_in=document_in)
    return document_obj


@router.get("/my_documents")
def get_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    documents = document_repo.get_by_user(db, user_id=current_user.id)
    return [
        DocumentInResponse(
            id=document.id,
            document=document.document,
            template_name=document.template_name,
            document_ref=document.document_ref,
            user_id=document.user_id,
            status=document.status,
            document_data=json.loads(document.document_data),
            created_at=document.created_at,
            qr_code=document.qr_code,
        )
        for document in documents
    ]


@router.get("/document")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    document = document_repo.get(db, id=document_id)
    if not document:
        raise ObjectNotFoundException(detail="this document was not found")
    if document.user_id != current_user.id:
        raise UnauthorizedEndpointException(
            detail="You are not the creator of this document"
        )
    return DocumentInResponse(
        id=document.id,
        document=document.document,
        template_name=document.template_name,
        document_ref=document.document_ref,
        user_id=document.user_id,
        status=document.status,
        qr_code=document.qr_code,
        document_data=json.loads(document.document_data),
        created_at=document.created_at,
    )


@router.get("/pay_for_document")
def pay_for_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    document = document_repo.get(db, id=document_id)
    if not document:
        raise ObjectNotFoundException(detail="this document was not found")
    if document.user_id != current_user.id:
        raise UnauthorizedEndpointException(
            detail="You are not the creator of this document"
        )
    document_repo.update_field(
        db, db_obj=document, field_name="status", field_value="PAID"
    )
    return {"document_id": document.id}


@router.post("/attest_document")
def attest_document(
    document_attest: AttestDocument,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    document_attested = document_repo.get_attested_document(
        db, document_ref=document_attest.document_ref
    )
    if document_attested:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This Document has already been attested",
        )
    document = document_repo.get_by_ref(db, ref=document_attest.document_ref)
    if not document:
        raise ObjectNotFoundException(detail="this document was not found")
    if document.status == "SAVED":
        raise UnauthorizedEndpointException(
            detail="You have to pay for this document to attest it"
        )
    document_in = {"document": document_attest.document, "status": "ATTESTED"}
    document_repo.update(db, db_obj=document, obj_in=document_in)
    attest_document_in = {**document_attest.dict(), "commissioner_id": current_user.id}
    document_repo.create_attested_document(db, obj_in=attest_document_in)
    return {"document_id": document.id}


@router.get(
    "/search_by_ref",
    dependencies=[Depends(commissioner_permission_dependency)],
)
def search_document_by_ref(
    document_ref: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    
    
    document = document_repo.get_by_ref(db, ref=document_ref)
    if not document:
        raise ObjectNotFoundException(detail="this document was not found")

    return DocumentInResponse(
        id=document.id,
        document=document.document,
        template_name=document.template_name,
        document_ref=document.document_ref,
        user_id=document.user_id,
        status=document.status,
        qr_code=document.qr_code,
        document_data=json.loads(document.document_data),
        created_at=document.created_at,
    )


@router.put("/document_update")
def update_document(
    document: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_currently_authenticated_user),
):
    document_obj = document_repo.get(db, id=document.id)
    if not document_obj:
        raise ObjectNotFoundException(detail="this document was not found")
    if document_obj.user_id != current_user.id:
        raise UnauthorizedEndpointException(
            detail="You are not the creator of this document"
        )
    document_in = document.dict()
    document_in["document_data"] = json.dumps(document_in["document_data"])
    updated_document = document_repo.update(db, db_obj=document_obj, obj_in=document_in)

    return DocumentInResponse(
        id=updated_document.id,
        document=updated_document.document,
        template_name=updated_document.template_name,
        document_ref=updated_document.document_ref,
        user_id=updated_document.user_id,
        status=updated_document.status,
        qr_code=updated_document.qr_code,
        document_data=json.loads(updated_document.document_data),
        created_at=updated_document.created_at,
    )
