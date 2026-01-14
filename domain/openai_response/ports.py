from typing import Protocol

class OpenAIResponseAPIPort(Protocol):
    async def create_response(self, model, input, stream, **kwargs):
        ...

    async def output_response_text(self):
        ...
    
    async def output_response_json(self):
        ...
    
    async def output_response_stream(self):
        ...
    