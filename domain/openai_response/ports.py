from typing import Protocol

class OpenAIResponseAPIPort(Protocol):
    def create_response(self, model, input, tools, stream, **kwargs):
        ...
    
    def output_response(self):
        ...
    
    def output_response_stream(self):
        ...