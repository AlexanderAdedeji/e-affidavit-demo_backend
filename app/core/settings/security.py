import binascii
import hashlib
import time
from datetime import datetime, timedelta
from app.core.settings.config import settings
from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext
from passlib.hash import bcrypt
from pydantic import EmailStr
from fastapi import HTTPException
from typing import Union, Optional
import base64
import logging


RESET_TOKEN_EXPIRE_MINUTES = settings.RESET_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_api_key_hash(api_key: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        api_key.encode("utf-8"),
        SECRET_KEY.encode("utf-8"),
        100000,
    ).hex()


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    return get_api_key_hash(plain_api_key) == hashed_api_key


def generate_reset_token(email: EmailStr, expires_delta: timedelta = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    exp = datetime.now() + expires_delta
    obj = {"email": email, "expires_at": exp.timestamp()}
    return URLSafeSerializer(secret_key=str(SECRET_KEY)).dumps(obj)


def decode_reset_token(token: str) -> EmailStr:
    obj = URLSafeSerializer(secret_key=str(SECRET_KEY)).loads(token)
    expires_at = obj["expires_at"]
    if expires_at <= time.time():
        raise ValueError("expired token")
    return obj["email"]



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_base_64(image: Union[bytes, bytearray]) -> Optional[str]:
    try:
        # Make sure the input is bytes or bytearray
        if not isinstance(image, (bytes, bytearray)):
            raise TypeError("Image should be bytes or bytearray")
        
        # Perform base64 encoding
        base64_encoded = base64.b64encode(image).decode("utf-8")
        
        return base64_encoded
    except Exception as e:
        logger.error(f"Failed to convert image to base64: {e}")
        raise HTTPException(status_code=400, detail="Invalid image data")

def convert_to_image(b: str) -> Optional[bytes]:
    try:
        # Validate that the input is a base64 string
        if not isinstance(b, str):
            raise TypeError("Input should be a base64 encoded string")
        
        # Perform base64 decoding
        base64_decoded = base64.b64decode(b)
        
        return base64_decoded
    except (binascii.Error, TypeError, Exception) as e:
        logger.error(f"Failed to convert base64 to image: {e}")
        raise HTTPException(status_code=400, detail="Invalid base64 data")


