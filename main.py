from threading import Thread
from src.bot.telegram import run as run_telegram
from uvicorn import run as run_uvicorn
from src.core.config import settings
from uvicorn.config import LOGGING_CONFIG


def main():
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    t = Thread(target=run_telegram, daemon=True)
    t.start()

    run_uvicorn("src.server.server:app", host='0.0.0.0', port=80,
                log_level="info", reload=settings.DEBUG_MODE)


if __name__ == "__main__":
    main()
