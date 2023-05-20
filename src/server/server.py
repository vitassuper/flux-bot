from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware

from src.app.routes import signal
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier
from src.core.config import settings

app = FastAPI(
    title=settings.SERVER_NAME, openapi_url=None
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    notifier = TelegramNotifier()

    notifier.add_message_to_stack(f'🚨{exc}')
    await notifier.send_message()

    return Response(content='Validation Error', status_code=400)


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
