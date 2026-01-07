from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class ResponseAPI(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T = None
