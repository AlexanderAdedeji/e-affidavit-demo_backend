from app.models.user_type_model import UserType

from typing import Any, Dict, List, Optional, Union

from app.core.settings.config import settings
from app.models.user_model import User
from commonLib.repositories.repository_class import Base
from app.repositories.user_type_repo import user_type as user_type_repo
from app.schemas.user import UserCreate, UserUpdate

from app.core.settings.security import get_password_hash
from sqlalchemy.orm import Session

REGULAR_USER_TYPE = settings.REGULAR_USER_TYPE
SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE




class UserRepository(Base[User]):
    def get_by_email(self, db: Session, *, email: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        return user

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            user_type_id=obj_in.user_type_id
        )
        
        db_obj.set_password(obj_in.password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.verify_password(password):
            return None
        return user

    def activate(self, db: Session, *, db_obj: User) -> User:
        return self._set_activation_status(db=db, db_obj=db_obj, status=True)

    def deactivate(self, db: Session, *, db_obj: User) -> User:
        return self._set_activation_status(db=db, db_obj=db_obj, status=False)

    def _set_activation_status(
        self, db: Session, *, db_obj: User, status: bool
    ) -> User:
        if db_obj.is_active == status:
            return db_obj
        return super().update(db, db_obj=db_obj, obj_in={"is_active": status})

    def set_as_superuser(self, db: Session, db_obj: User) -> User:
        superuser_type = user_type_repo.get_by_name(
            db, name=USER_TYPES[SUPERUSER_USER_TYPE]
        )
        return self.set_usertype(db, db_obj=db_obj, user_type=superuser_type)

    def set_usertype(self, db: Session, db_obj: User, user_type: UserType) -> User:
        db_obj.user_type = user_type
        return super().update(db, db_obj=db_obj, obj_in={})


user_repo = UserRepository(User)
