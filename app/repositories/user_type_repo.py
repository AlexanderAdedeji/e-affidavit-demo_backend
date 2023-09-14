import uuid
from typing import List
from app.models.user_type_model import UserType
from commonLib.repositories.repository_class import Base
from app.schemas.user_type_schema import UserTypeCreate, UserTypeUpdate
from sqlalchemy.orm import Session


class UserTypeRepository(Base[UserType]):
    def get_by_name(self, db: Session, *, name: str) -> UserType:
        return db.query(UserType).filter(UserType.name == name).first()

    def get_by_id(self, db: Session, *, id: int) -> UserType:
        return db.query(UserType).filter(UserType.id == id).first()

    def create(self, db: Session, *, obj_in: UserType) -> UserType:
        db_obj = UserType(id=str(uuid.uuid4()), name=str(obj_in.name))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_type_repo = UserTypeRepository(UserType)
