from fastapi import APIRouter
from typing import List, Optional
from domain.models import ResponseAPI, Session, User
from application.session_usecases import SessionUsecase

router = APIRouter()

@router.get("/session/{user_id}", response_model=ResponseAPI[List[Session]])
async def get_sessions(user_id: int):
    session_usecase = SessionUsecase()
    sessions = await session_usecase.get_sessions_by_user(user_id)
    sessions = [Session.model_validate(session, from_attributes=True) for session in sessions]

    return ResponseAPI(
        status_code=200,
        message="세션 목록 조회 성공",
        data=sessions
    )

@router.get("/user", response_model=ResponseAPI[Optional[User]])
async def get_user():
    session_usecase = SessionUsecase()
    user = await session_usecase.get_user()
    if user:
        user = User.model_validate(user, from_attributes=True)

    return ResponseAPI(
        status_code=200,
        message="유저 조회 성공",
        data=user
    )

@router.post("/user/admin", response_model=ResponseAPI)
async def create_admin_user():
    session_usecase = SessionUsecase()
    success_message = await session_usecase.create_admin_user()

    return ResponseAPI(
        status_code=201,
        message=success_message,
    )
