from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator

from app.schemas.user_type_schema import UserTypeInDB
from commonLib.models.base_class import Base


from app.core.services.validators import phone as phone_validators


class User(BaseModel):
    first_name: str
    last_name: str


class UserCreate(User):
    email: EmailStr
    password: str
    user_type_id: str
    # user_type_id: int

    # @validator("phone")
    # def validate_phone(cls, value: str) -> str:
    #     return phone_validators.validate_phone_number(value)


class UserUpdate(User):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str] = None
    image: Optional[str] = None


class UserInLogin(BaseModel):
    email: EmailStr
    password: str


class UserWithToken(BaseModel):
    first_name: str
    last_name:str
    email: EmailStr
    user_type: UserTypeInDB
    token: str


class UserCreateForm(User):
    email: EmailStr
    password: str
    user_type: str


class UserInResponse(User):
    id: str
    email: EmailStr
    is_active: bool
    image: Optional[str]
    user_type: UserTypeInDB


class SlimUserInResponse(BaseModel):
    id: str
    email: EmailStr
    user_type: UserTypeInDB


class ResetPasswordSchema(BaseModel):
    token: str
    password: str
