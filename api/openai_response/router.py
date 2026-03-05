import base64
import json
from typing import Any, Dict, List, Literal, Union

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from domain.models import ResponseAPI
from domain.openai_response.models import OpenAIResponseAPIModel
from domain.parser import format_sse_data
from application.openai_usecases import OpenAIUseCase
from application.session_usecases import SessionUsecase

router = APIRouter(prefix="/openai-response")


def _parse_json_field(field_name: str, value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid JSON payload for '{field_name}'.",
        ) from exc

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
async def get_openai_response_sse(
    session_id: int | None = Form(None),
    mode: Literal["architecture", "frontend"] = Form("architecture"),
    model: str = Form(...),
    input: str = Form(...),
    instructions: str | None = Form(None),
    stream: bool = Form(False),
    tools: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    parsed_input: Union[List[Dict[str, Any]], str] = input
    input_stripped = input.strip()
    if input_stripped.startswith("{") or input_stripped.startswith("["):
        parsed_input = _parse_json_field("input", input)

    parsed_tools = _parse_json_field("tools", tools) if tools else None

    data = OpenAIResponseAPIModel(
        session_id=session_id,
        mode=mode,
        model=model,
        input=parsed_input,
        instructions=instructions,
        stream=stream,
        tools=parsed_tools,
    )

    if image is not None:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=422, detail="Uploaded image is empty.")

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        content_type = image.content_type or "application/octet-stream"
        text = data.input if isinstance(data.input, str) else json.dumps(data.input, ensure_ascii=False)

        data = OpenAIResponseAPIModel(
            **data.model_dump(exclude={"input"}),
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": text},
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{base64_image}",
                        },
                    ],
                }
            ],
        )

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
