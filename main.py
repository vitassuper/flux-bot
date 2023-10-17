from sanic import Sanic

from src import settings
from src.web_server.routes.signal import router

app = Sanic("Connector")
app.blueprint(router)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=80,
        debug=settings.DEBUG_MODE,
        access_log=True,
        auto_reload=settings.DEBUG_MODE,
        workers=2,
    )
