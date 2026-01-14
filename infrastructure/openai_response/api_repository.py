from domain.openai_response.ports import OpenAIResponseAPIPort
from openai import AsyncOpenAI

class OpenAIResponseAPIRepository(OpenAIResponseAPIPort):

    def __init__(self):
        self.client = AsyncOpenAI()
        self.response = None
        self.stream = False

    async def create_response(self, model, input, stream:bool,  **kwargs):
        self.stream = stream
        
        response = await self.client.responses.create(
            model=model,
            input=input,
            stream=stream,
            **kwargs
        )

        self.response = response
        return response
    
    async def output_response_text(self):
        if self.stream:
            raise ValueError("Response is streamed. Use output_response_stream method instead.")
        if self.response is None:
            raise ValueError("No response available. Please create a response first.")
        
        return self.response.output_text
    
    async def output_response_json(self):
        if self.stream:
            raise ValueError("Response is streamed. Use output_response_stream method instead.")
        if self.response is None:
            raise ValueError("No response available. Please create a response first.")
        
        return self.response.output[0].to_json()
    
    async def output_response_stream(self):
        if not self.stream:
            raise ValueError("Response is not streamed. Use output_response_text or output_response_json method instead.")
        if self.response is None:
            raise ValueError("No response available. Please create a response first.")
        
        async for chunk in self.response:
            yield chunk
