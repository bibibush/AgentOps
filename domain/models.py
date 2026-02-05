from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar('T')

class ResponseAPI(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T = None

class User(BaseModel):
    id: int
    username: str
    email: str

class Session(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: Optional[str]
    token: Optional[str]
    created_at: datetime


class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    session_id: int
    created_at: datetime
