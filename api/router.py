from fastapi import APIRouter
from api.openai_response.router import router as openai_router
from api.session.router import router as session_router

router = APIRouter()
router.include_router(openai_router)
router.include_router(session_router)