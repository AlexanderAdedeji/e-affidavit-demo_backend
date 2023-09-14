from typing import Optional
from pydantic import BaseModel


class SignatureBase(BaseModel):
    Signature: str


class StampBase(BaseModel):
    stamp: str


class SignatureInResponse(SignatureBase):
    user_id: str


class StampInResponse(StampBase):
    user_id: str


class AttestationBase(BaseModel):
    signature: Optional[str]
    stamp: Optional[str]


class AttestationCreate(AttestationBase):
    user_id: str

class AttestationInResponse(AttestationCreate):
    pass
