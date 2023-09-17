import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentBase(BaseModel):
    document: str
    template_name: str
    document_data: dict


class DocumentInResponse(DocumentBase):
    id: str
    user_id: str
    document_ref: Optional[str]
    created_at: datetime.datetime
    qr_code:Optional[str]
    status:str


class DocumentCreate(BaseModel):
    document: str
    document_ref: Optional[str]
    document_fileds: str
    status: str
    id: str
    user_id: str


class DocumentRef(BaseModel):
    document_ref: str


class DocumentQRCode(DocumentRef):
    qr_code: str




class AttestDocument(BaseModel):
    document_ref:str
    document: str
class AttestDocumentCreate(AttestDocument):
    commissioner_id:str
