from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from domain.models import ResponseAPI
from domain.openai_response.models import OpenAIResponseAPIModel
from application.openai_usecases import OpenAIUseCase

router = APIRouter(prefix="/openai-response")

@router.post("/text", response_model=ResponseAPI)
async def get_openai_response(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()
    response = await openai_usecase.generate_text_response(
        ai_request=data
    )

    return ResponseAPI(
        status_code=200,
        message="OpenAI response generated successfully.",
        data=response
    )

@router.post("/json", response_model=ResponseAPI)
async def get_openai_response_json(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()
    response = await openai_usecase.generate_json_response(
        ai_request=data
    )

    return ResponseAPI(
        status_code=200,
        message="OpenAI JSON response generated successfully.",
        data=response
    )

@router.post("/sse")
async def get_openai_response_sse(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()

    async def event_generator():
        async for chunk in openai_usecase.generate_stream_response(ai_request=data):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
