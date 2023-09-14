import collections
from typing import List
from pydantic import AnyHttpUrl, validator
from pydantic import  EmailStr
from pydantic_settings import BaseSettings

import os
from pathlib import Path
from pydantic import validator
from starlette.datastructures import CommaSeparatedStrings



class Settings(BaseSettings):
    API_V1_STR: str
    PROJECT_NAME: str
    API_URL_PREFIX:str
    DEBUG:bool
    DEVELOPMENT_DATABASE_URL:str
    PRODUCTION_DATABASE_URL:str
    SECRET_KEY:str
    RESET_TOKEN_EXPIRE_MINUTES:int
    JWT_EXPIRE_MINUTES:int
    JWT_ALGORITHM:str
    JWT_TOKEN_PREFIX:str
    HEADER_KEY:str
    REGULAR_USER_TYPE:str
    SUPERUSER_USER_TYPE:str
    COMMISSIONER_USER_TYPE:str
    VERIFIER_USER_TYPE:str
    USER_TYPES:list

    # USER_TYPES = collections.defaultdict(lambda: REGULAR_USER_TYPE)



    class Config:
        env_file = os.getenv(
            "ENV_VARIABLE_PATH", Path(__file__).parent / "env_files" / ".env"
        )


settings = Settings()







