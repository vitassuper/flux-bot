from fastapi import APIRouter

from src.app.controllers import signal

api_router = APIRouter()
api_router.include_router(signal.router, prefix="/signal", tags=["signal"])
