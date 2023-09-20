from datetime import datetime, timedelta

# from backend.app.schemas.reset_token import ResetTokenCreate
import jwt
from sqlalchemy.orm.session import Session
from app.core.settings.config import settings
from commonLib.models.base_class import Base
from app.schemas.jwt import JWTUser
from app.core.settings import security
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES

SECRET_KEY = settings.SECRET_KEY
SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE
RESET_TOKEN_EXPIRE_MINUTES = settings.RESET_TOKEN_EXPIRE_MINUTES


# docker-compose -f docker-compose-dev.yml run --publish 6543:5432 database
class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    is_active = Column(String, nullable=True)
    image = Column(String, nullable=True)
    user_type_id = Column(String, ForeignKey("usertype.id"), nullable=False)
    user_type = relationship("UserType", back_populates="users")
    



    @property
    def is_superuser(self):
        return self.user_type.name == SUPERUSER_USER_TYPE

    def set_password(self, password: str) -> None:
        self.hashed_password = security.get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return security.verify_password(password, self.hashed_password)

    def generate_jwt(self, expires_delta: timedelta = None):
        if not self.is_active:
            raise Exception("user is not active")

        jwt_content = JWTUser(id=self.id).dict()
        if expires_delta is None:
            expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)

        now = datetime.now()
        expires_at = now + expires_delta

        jwt_content["exp"] = expires_at.timestamp()
        jwt_content["iat"] = now.timestamp()

        encoded_token = jwt.encode(
            payload=jwt_content, key=str(SECRET_KEY), algorithm=JWT_ALGORITHM
        )
        return encoded_token.encode()
