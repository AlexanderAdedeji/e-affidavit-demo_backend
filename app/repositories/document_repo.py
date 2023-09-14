import uuid
import json
from typing import List
from fastapi import HTTPException
from app.models.document_model import Document
from app.schemas.document_schema import DocumentCreate, DocumentBase
from commonLib.repositories.repository_class import Base
from sqlalchemy.orm import Session


class DocumentRepository(Base[Document]):
    def create(self, db: Session, *, obj_in):
        db_obj = Document(**obj_in, id=str(uuid.uuid4()))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(self, db: Session, *, user_id):
        try:
            documents = db.query(Document).filter(Document.user_id == user_id).all()
            return documents
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database error") from e


document_repo = DocumentRepository(Document)
