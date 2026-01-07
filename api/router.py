from fastapi import APIRouter
from api.openai_response.router import router as openai_router

router = APIRouter()
router.include_router(openai_router)