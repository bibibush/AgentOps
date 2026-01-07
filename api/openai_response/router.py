from fastapi import APIRouter
from infrastructure.openai_response.models import OpenAIResponseAPIModel

router = APIRouter(prefix="/openai-response")

@router.post("/")
async def get_openai_response(data: OpenAIResponseAPIModel):
    return {"message": "Hello, World!"}