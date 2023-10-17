from sanic import Blueprint

from src.web_server.controllers import signal

router = Blueprint(name='signal')
router.add_route(signal.handler, '/api/v1/signal', ['POST'])
