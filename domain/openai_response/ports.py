from typing import Protocol, Any, AsyncGenerator, Union, List, Dict

class OpenAIResponseAPIPort(Protocol):
    async def create_response(self, model: str, input: Any, stream: bool, **kwargs) -> Any:
        ...

    async def output_response_text(self, response: Any) -> str:
        ...
    
    async def output_response_json(self, response: Any) -> Union[List, Dict]:
        ...
    
    async def output_response_stream(self, response: Any) -> AsyncGenerator[Any, None]:
        ...
    