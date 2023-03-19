from fastapi import FastAPI, Request, Response
# from src.bot.notifier import Notifier
from src.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from src.app.routes import signal
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f'{settings.API_V1_STR}/openapi.json'
)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     notifier = Notifier()
#     notifier.send_warning_notification(f'{exc}')
#
#     return Response(content='Validation Error', status_code=400)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(signal.api_router, prefix=settings.API_V1_STR)
