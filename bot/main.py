import threading
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from bot.connector import Connector

from bot.settings import Config
import traceback
import logging

from bot.tg import run

configEnv = Config()

@view_config(request_method='POST', route_name='handler', renderer='json')
def handle(request):
    connector_secret = request.json_body.get('connector_secret', '')
    type_of_signal = request.json_body.get('type_of_signal', '')
    pair =  request.json_body.get('pair', '')
    amount = request.json_body.get('amount', '')

    connector = Connector()
    
    if(configEnv.validate_connector_secret(connector_secret)):
        print('Correct secret')
    else:
        print('Incorrect secret')
        
        return {}

    if(type_of_signal == 'open'):     
        margin_amount = request.json_body.get('margin_amount', None)

        connector.open_short_position(pair=pair, amount=amount, leverage=20, margin=margin_amount)

    if(type_of_signal == 'add'):
        connector.add_to_short_position(pair=pair, amount=amount)

    if(type_of_signal == 'close'):
        connector.close_short_position(pair=pair)

    if(type_of_signal == 'check'):
        chatId = request.json_body.get('chat_id', '')
        connector.check_open_positions(chatId)

    return {}

def main():
    logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', level=logging.ERROR)
    try:
        with Configurator() as config:
            config.add_route('handler', '/')
            config.scan()
            app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 80, app)

        thread1 = threading.Thread(target=server.serve_forever)
        thread2 = threading.Thread(target=run)

        thread1.start()
        thread2.start()

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
