import uuid
import json
from typing import List
from app.models.attested_document_model import AttestedDocuments
from fastapi import HTTPException
from app.models.document_model import Document
from app.schemas.document_schema import AttestDocumentCreate, DocumentCreate, DocumentBase
from commonLib.repositories.repository_class import Base
from sqlalchemy.orm import Session


class DocumentRepository(Base[Document]):
    def create(self, db: Session, *, obj_in):
        try:
            db_obj = Document(**obj_in, id=str(uuid.uuid4()), status="SAVED")
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database error") from e

    def get_by_user(self, db: Session, *, user_id: str):
        try:
            documents = db.query(Document).filter(Document.user_id == user_id).all()
            return documents
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database error") from e

    def get_by_ref(self, db: Session, *, ref: str):
        try:
            document = db.query(Document).filter(Document.document_ref == ref).first()
            return document
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database error") from e

    def update_field(
        self, db: Session, *, db_obj: Document, field_value: str, field_name: str
    ):
        return super().update(db, db_obj=db_obj, obj_in={field_name: field_value})

    def get_attested_document(self, db: Session, *, document_ref: str):
        try:
            document = (
                db.query(AttestedDocuments)
                .filter(AttestedDocuments.document_ref == document_ref)
                .first()
            )
            return document
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database error") from e
    def create_attested_document(self, db: Session, *, obj_in):
        # try:
            db_obj = AttestedDocuments(**obj_in, id=str(uuid.uuid4()))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        # except Exception as e:
        #     raise HTTPException(status_code=503, detail="Database error") from e

document_repo = DocumentRepository(Document)
