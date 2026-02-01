from domain.ports import MyDBPort
from domain.models import ChatMessage
from domain.openai_response.ports import OpenAIResponseAPIPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.openai_response.api_repository import OpenAIResponseAPIRepository
from infrastructure.mydb_repository import MyDBRepository
from infrastructure.db.models import UserORM, ChatMessageORM

class OpenAIUseCase:
    openai_repository: OpenAIResponseAPIPort
    user_repository: MyDBPort[UserORM]
    chat_repository: MyDBPort[ChatMessageORM]

    def __init__(self):
        self.openai_repository = OpenAIResponseAPIRepository()
        self.user_repository = MyDBRepository(entity_class=UserORM)
        self.chat_repository = MyDBRepository(entity_class=ChatMessageORM)

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
        chat = []
        
        request_data = ai_request.model_dump()
        response = await self.openai_repository.create_response(**request_data)
        async for chunk in self.openai_repository.output_response_stream(response):
            chat.append(chunk)
            yield chunk

        entire_chat_message = ''.join(chat)
        chat_message = ChatMessage(
            user_id=1,
            role="assistant",
            message=entire_chat_message,
        )
        chat_message_entity = ChatMessageORM(**chat_message.model_dump())
        
        await self.chat_repository.add(chat_message_entity)
        await self.chat_repository.commit()