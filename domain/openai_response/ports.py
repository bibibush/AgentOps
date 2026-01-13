from typing import Protocol

class OpenAIResponseAPIPort(Protocol):
    async def create_response(self, model, input, tools, stream, **kwargs):
        ...
    
    async def output_response(self):
        ...
    
    async def output_response_stream(self):
        ...