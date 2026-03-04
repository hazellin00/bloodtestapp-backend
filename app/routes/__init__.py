from fastapi import APIRouter
from .history import router as history_router
from .insights import router as insight_router

api_router = APIRouter()
api_router.include_router(history_router, prefix="/history")
api_router.include_router(insight_router, prefix="/insights")