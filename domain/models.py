from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class ResponseAPI(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T = None

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    id: int
    role: str
    message: str
    user_id: int
    created_at: str

    class Config:
        from_attributes = True