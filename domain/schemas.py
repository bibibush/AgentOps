from pydantic import BaseModel
from typing import Any

class ResponseAPI(BaseModel):
    status_code: int
    message: str
    data: Any