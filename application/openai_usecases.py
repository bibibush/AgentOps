from domain.openai_response.ports import OpenAIResponseAPIPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.openai_response.api_repository import OpenAIResponseAPIRepository
from typing import Literal

class OpenAIUseCase:
    openai_repository: OpenAIResponseAPIPort
    
    def __init__(self, mode: Literal["text", "json", "stream"] = "stream"):
        self.openai_repository = OpenAIResponseAPIRepository()
        self.mode = mode
        self.switcher = {
            "text": self.openai_repository.output_response_text,
            "json": self.openai_repository.output_response_json,
            "stream": self.openai_repository.output_response_stream,
        }
    
    async def generate_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        if self.mode == "stream":
            return self._generate_stream_response(ai_request)
        else:
            return await self._generate_response(ai_request)
    
    async def _generate_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(
            **request_data
        )

        return await self.switcher[self.mode](response)

    async def _generate_stream_response(
            self,
            ai_request: OpenAIResponseAPIModel,
        ):
        
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(
            **request_data
        )

        async for chunk in await self.switcher[self.mode](response):
            yield chunk

