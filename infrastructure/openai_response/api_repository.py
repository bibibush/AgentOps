from domain.openai_response.ports import OpenAIResponseAPIPort
from openai import AsyncOpenAI
from typing import Any, AsyncGenerator, Union, List, Dict

class OpenAIResponseAPIRepository(OpenAIResponseAPIPort):

    def __init__(self) -> None:
        self.client = AsyncOpenAI()
        self.stream = False

    async def create_response(self, model: str, input: Any, stream: bool, **kwargs) -> Any:
        self.stream = stream
        
        response = await self.client.responses.create(
            model=model,
            input=input,
            stream=stream,
            **kwargs
        )

        return response
    
    async def output_response_text(self, response: Any) -> str:
        if self.stream:
            raise ValueError("Response is streamed. Use output_response_stream method instead.")
        if response is None:
            raise ValueError("No response available. Please create a response first.")
        
        return response.output_text
    
    async def output_response_json(self, response: Any) -> Union[Dict, List]:
        if self.stream:
            raise ValueError("Response is streamed. Use output_response_stream method instead.")
        if response is None:
            raise ValueError("No response available. Please create a response first.")
        
        return response.output[0].to_json()
    
    async def output_response_stream(self, response: Any) -> AsyncGenerator[Any, None]:
        if not self.stream:
            raise ValueError("Response is not streamed. Use output_response_text or output_response_json method instead.")
        if response is None:
            raise ValueError("No response available. Please create a response first.")
        
        async for chunk in response:
            yield chunk
