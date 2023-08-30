from typing import List
from app.models.user_type_model import UserType
from commonLib.repositories.repository_class import Base
from app.schemas.user_type import UserTypeCreate, UserTypeUpdate
from sqlalchemy.orm import Session


class UserTypeRepository(Base[UserType]):
    def get_by_name(self, db: Session, *, name:str) -> UserType:
        return db.query(UserType).filter(UserType.name == name).first()
    
    def get_by_id(self, db:Session, *,id:int )->UserType:
        return db.query(UserType).filter(UserType.id == id).first()

user_type = UserTypeRepository(UserType)
