from domain.openai_response.ports import OpenAIResponseAPIPort
from openai import AsyncOpenAI

class OpenAIResponseAPIRepository(OpenAIResponseAPIPort):

    def __init__(self):
        self.client = AsyncOpenAI()
        self.response = None

    async def create_response(self, model, input, tools, stream, **kwargs):
        response = await self.client.responses.create(
            model=model,
            input=input,
        )

        self.response = response