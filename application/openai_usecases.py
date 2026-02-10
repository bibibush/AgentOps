from domain.ports import MyDBPort
from domain.models import ChatMessage, Session
from domain.openai_response.ports import OpenAIResponseAPIPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.openai_response.api_repository import OpenAIResponseAPIRepository
from infrastructure.mydb_repository import MyDBRepository
from infrastructure.db.models import UserORM, ChatMessageORM, SessionORM

class OpenAIUseCase:
    openai_repository: OpenAIResponseAPIPort
    user_repository: MyDBPort[UserORM]
    chat_repository: MyDBPort[ChatMessageORM]
    session_repository: MyDBPort[SessionORM]

    def __init__(self):
        self.openai_repository = OpenAIResponseAPIRepository()
        self.user_repository = MyDBRepository(entity_class=UserORM)
        self.chat_repository = MyDBRepository(entity_class=ChatMessageORM)
        self.session_repository = MyDBRepository(entity_class=SessionORM)

    async def cleanup(self):
        """모든 repository의 세션을 닫습니다."""
        await self.user_repository.close()
        await self.chat_repository.close()
        await self.session_repository.close()

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
            session_id: int,
        ):
        chat = []
        
        user_message = ai_request.input if isinstance(ai_request.input, str) else ""
        user_message_entity = ChatMessageORM(
            session_id=session_id,
            role="user",
            message=user_message,
        )
        await self.chat_repository.add(user_message_entity)
        await self.chat_repository.commit()
        
        request_data = ai_request.model_dump()
        request_data.pop("session_id", None)
        response = await self.openai_repository.create_response(mode="architecture", **request_data)
        async for chunk in self.openai_repository.output_response_stream(response):
            chat.append(chunk)
            yield chunk

        entire_chat_message = ''.join(chat)
        chat_message_entity = ChatMessageORM(
            role="assistant",
            message=entire_chat_message,
            session_id=session_id,
        )
        
        await self.chat_repository.add(chat_message_entity)
        await self.chat_repository.commit()
