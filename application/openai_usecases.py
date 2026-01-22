from domain.openai_response.ports import OpenAIResponseAPIPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.openai_response.api_repository import OpenAIResponseAPIRepository

class OpenAIUseCase:
    openai_repository: OpenAIResponseAPIPort

    def __init__(self):
        self.openai_repository = OpenAIResponseAPIRepository()

    async def generate_text_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(**request_data)
        return await self.openai_repository.output_response_text(response)

    async def generate_json_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(**request_data)
        return await self.openai_repository.output_response_json(response)

    async def generate_stream_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(**request_data)
        async for chunk in self.openai_repository.output_response_stream(response):
            yield chunk
