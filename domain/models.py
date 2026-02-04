from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

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


class Session(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    token: Optional[str]
    created_at: str


class ChatMessage(BaseModel):
    id: int
    role: str
    message: str
    session_id: int
    created_at: str
