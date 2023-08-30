from pydantic import BaseModel
from typing import Optional, Type, TypeVar, Generic


DataModelType = TypeVar("DataModelType", bound=BaseModel)


class ResponseWrapper(Generic[DataModelType], BaseModel):
    status_code: int
    message: str
    data: Optional[DataModelType]
    page: Optional[int]
