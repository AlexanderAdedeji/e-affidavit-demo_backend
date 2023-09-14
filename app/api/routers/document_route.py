import string
import json
import random
from typing import List
import qrcode
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
    DocumentBase,
    DocumentCreate,
    DocumentInResponse,
    DocumentQRCode,
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
def generate_document_ref():
    try:
        # Generate a random document reference
        document_ref = generate_random_string(9)

        # Generate QR code image
        buffered = generate_qr_code(document_ref)

        # Convert image to base64
        img_str = security.convert_to_base_64(buffered.getvalue())

        # Optionally, save image to a file
        with open("qrcode001.jpeg", "wb") as f:
            f.write(buffered.getvalue())

        return DocumentQRCode(document_ref=document_ref, qr_Code=img_str)
    except Exception as e:
        logger.error(f"Failed to generate document reference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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