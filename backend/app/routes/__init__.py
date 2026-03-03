from fastapi import APIRouter
from . import history, insights

api_router = APIRouter()
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
