from typing import Protocol

class ResponseClientInterface(Protocol):
    def create_response(self, model, input, stream, **kwargs):
        ...
    
    def output_response(self):
        ...
    
    def output_response_stream(self):
        ...