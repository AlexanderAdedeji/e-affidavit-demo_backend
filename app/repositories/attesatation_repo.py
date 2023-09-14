from typing import List
from app.models.attestation_model import Attestation
from commonLib.repositories.repository_class import Base
from app.schemas.attestation_schema import StampBase
from sqlalchemy.orm import Session


class AttestationRepository(Base[Attestation]):
    def get_by_user_id(self, db, *, user_id: str):
        return db.query(Attestation).filter(Attestation.user_id == user_id).first()
        

    pass


attestation_repo = AttestationRepository(Attestation)
