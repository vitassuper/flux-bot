from sanic import Sanic

from src.app.routes.signal import router
from src.core.config import settings

app = Sanic('Connector')
app.blueprint(router)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, access_log=True, auto_reload=settings.DEBUG_MODE, workers=2)
