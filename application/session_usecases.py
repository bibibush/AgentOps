from domain.ports import MyDBPort
from domain.openai_response.models import OpenAIResponseAPIModel
from infrastructure.db.models import UserORM, ChatMessageORM, SessionORM
from infrastructure.mydb_repository import MyDBRepository
from typing import Any, Optional

class SessionUsecase:
    MAX_SESSION_TITLE_LENGTH = 20
    DEFAULT_SESSION_TITLE = "New Session"

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
        title = self._build_session_title(ai_request.input)
        new_session = SessionORM(
            user_id=1,
            title=title,
        )
        await self.session_repository.add(new_session)
        # flush()를 호출하면 id가 할당되고, commit 전이므로 객체가 여전히 세션에 연결되어 있습니다
        session_id = new_session.id
        await self.session_repository.commit()
        return session_id

    def _build_session_title(self, raw_input: Any) -> str:
        if isinstance(raw_input, str):
            title_source = raw_input
        else:
            title_source = self._extract_input_text(raw_input)

        title = title_source.strip() if isinstance(title_source, str) else ""
        if not title:
            return self.DEFAULT_SESSION_TITLE

        return title[: self.MAX_SESSION_TITLE_LENGTH]

    def _extract_input_text(self, raw_input: Any) -> Optional[str]:
        if not isinstance(raw_input, list):
            return None

        for message in raw_input:
            if not isinstance(message, dict):
                continue

            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content

            if not isinstance(content, list):
                continue

            for block in content:
                if not isinstance(block, dict):
                    continue

                if block.get("type") != "input_text":
                    continue

                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text

        return None
    
    async def delete_session(self, session_id: int) -> str:
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            raise Exception("세션을 찾을 수 없습니다")
        
        await self.session_repository.delete(session)
        await self.session_repository.commit()
        return "세션 삭제 완료"
    
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
