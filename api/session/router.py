from fastapi import APIRouter
from typing import List, Optional
from domain.models import ResponseAPI, Session, User
from application.session_usecases import SessionUsecase

router = APIRouter()

@router.get("/sessions/{user_id}", response_model=ResponseAPI[List[Session]])
async def get_sessions(user_id: int):
    session_usecase = SessionUsecase()
    try:
        sessions = await session_usecase.get_sessions_by_user(user_id)
        sessions = [Session.model_validate(session, from_attributes=True) for session in sessions]

        return ResponseAPI(
            status_code=200,
            message="세션 목록 조회 성공",
            data=sessions
        )
    finally:
        await session_usecase.cleanup()

@router.delete("/sessions/{session_id}", response_model=ResponseAPI)
async def delete_session(session_id: int):
    session_usecase = SessionUsecase()
    try:
        success_message = await session_usecase.delete_session(session_id)

        return ResponseAPI(
            status_code=200,
            message=success_message,
        )
    finally:
        await session_usecase.cleanup()

@router.get("/user", response_model=ResponseAPI[Optional[User]])
async def get_user():
    session_usecase = SessionUsecase()
    try:
        user = await session_usecase.get_user()
        if user:
            user = User.model_validate(user, from_attributes=True)

        return ResponseAPI(
            status_code=200,
            message="유저 조회 성공",
            data=user
        )
    finally:
        await session_usecase.cleanup()

@router.post("/user/admin", response_model=ResponseAPI)
async def create_admin_user():
    session_usecase = SessionUsecase()
    try:
        success_message = await session_usecase.create_admin_user()

        return ResponseAPI(
            status_code=201,
            message=success_message,
        )
    finally:
        await session_usecase.cleanup()
