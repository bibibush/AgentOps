from domain.ports import MyDBPort
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
    
    async def get_sessions_by_user(self, user_id: int):
        sessions = await self.session_repository.filter_by(user_id=user_id)
        return sessions
    
    async def get_user(self):
        user = await self.user_repository.get_by_id(1)
        return user