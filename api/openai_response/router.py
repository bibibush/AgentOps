from fastapi import APIRouter
from domain.models import ResponseAPI
from domain.openai_response.models import OpenAIResponseAPIModel
from application.openai_usecases import OpenAIUseCase

router = APIRouter(prefix="/openai-response")

@router.post("/", response_model=ResponseAPI)
async def get_openai_response(data: OpenAIResponseAPIModel, mode: str = "stream"):
    openai_usecase = OpenAIUseCase()
    response = await openai_usecase.generate_response(
        ai_request=data,
        mode=mode
    )

    return ResponseAPI(
        status_code=200,
        message="OpenAI response generated successfully.",
        data=response
    )
