from fastapi import APIRouter

from src.app.controllers import deals

api_router = APIRouter()
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
