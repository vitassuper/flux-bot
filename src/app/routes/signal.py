from sanic import Blueprint

from src.app.controllers import signal

router = Blueprint(name='signal')
router.add_route(signal.handler, '/api/v1/signal', ['POST'])
