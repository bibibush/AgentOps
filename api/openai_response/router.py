from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from domain.models import ResponseAPI
from domain.openai_response.models import OpenAIResponseAPIModel
from domain.parser import format_sse_data
from application.openai_usecases import OpenAIUseCase
from application.session_usecases import SessionUsecase

router = APIRouter(prefix="/openai-response")

@router.post("/text", response_model=ResponseAPI)
async def get_openai_response(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()
    try:
        response = await openai_usecase.generate_text_response(
            ai_request=data
        )

        return ResponseAPI(
            status_code=200,
            message="OpenAI response generated successfully.",
            data=response
        )
    finally:
        await openai_usecase.cleanup()

@router.post("/json", response_model=ResponseAPI)
async def get_openai_response_json(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()
    try:
        response = await openai_usecase.generate_json_response(
            ai_request=data
        )

        return ResponseAPI(
            status_code=200,
            message="OpenAI JSON response generated successfully.",
            data=response
        )
    finally:
        await openai_usecase.cleanup()

@router.post("/sse")
async def get_openai_response_sse(data: OpenAIResponseAPIModel):
    openai_usecase = OpenAIUseCase()
    session_usecase = SessionUsecase()
    try:
        if data.session_id is None:
            session_id = await session_usecase.create_session_id(data)
        else:
            session_id = data.session_id
    finally:
        # 세션 생성 후 즉시 cleanup
        await session_usecase.cleanup()

    async def event_generator():
        try:
            yield f"event: session\ndata: {session_id}\n\n"
            async for chunk in openai_usecase.generate_stream_response(
                ai_request=data,
                session_id=session_id,
            ):
                yield format_sse_data(chunk)
        finally:
            # 스트리밍 완료 후 cleanup
            await openai_usecase.cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
