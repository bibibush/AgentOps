from domain.ports import MyDBPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.db.models import UserORM, ChatMessageORM, SessionORM
from infrastructure.mydb_repository import MyDBRepository

class SessionUsecase:
    user_repository: MyDBPort[UserORM]
    chat_repository: MyDBPort[ChatMessageORM]
    session_repository: MyDBPort[SessionORM]
    def __init__(self):
        self.user_repository = MyDBRepository(entity_class=UserORM)
        self.chat_repository = MyDBRepository(entity_class=ChatMessageORM)
        self.session_repository = MyDBRepository(entity_class=SessionORM)

    async def cleanup(self):
        """모든 repository의 세션을 닫습니다."""
        await self.user_repository.close()
        await self.chat_repository.close()
        await self.session_repository.close()
    
    async def create_session_id(self, ai_request: OpenAIResponseAPIModel) -> int:
        new_session = SessionORM(
            user_id=1,
            title=ai_request.input[:20] if isinstance(ai_request.input, str) else "New Session",
        )
        await self.session_repository.add(new_session)
        # flush()를 호출하면 id가 할당되고, commit 전이므로 객체가 여전히 세션에 연결되어 있습니다
        session_id = new_session.id
        await self.session_repository.commit()
        return session_id
    
    async def get_sessions_by_user(self, user_id: int):
        sessions = await self.session_repository.filter_by(user_id=user_id)
        return sessions
    
    async def get_user(self):
        user = await self.user_repository.get_by_id(1)
        return user
    
    async def create_admin_user(self):
        new_user = UserORM(
            id=1,
            username="admin",
            email="admin@admin.com",
            hashed_password="admin1234!@#$"
        )
        await self.user_repository.add(new_user)
        await self.user_repository.commit()

        return "admin계정 생성 완료"
