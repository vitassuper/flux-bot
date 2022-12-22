import os
from dotenv import load_dotenv

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from .notificator import send_notification
import ccxt


class Config:
    def __init__(self):
        self.connector_secret = ''
        self.apiKey = ''
        self.apiSecret = ''
        self.safety_margin = 0
        
        self.load_config()

    def load_config(self):
        load_dotenv()

        self.connector_secret = os.environ['CONNECTOR_SECRET']
        self.apiKey = os.environ['API_KEY']
        self.apiSecret = os.environ['API_SECRET']
        self.safety_margin = os.environ['SAFETY_MARGIN']
    
    def validate_connector_secret(self, secret):
        return self.connector_secret == secret

class Connector:
    def __init__(self):
        configEnv = Config()

        self.okx = ccxt.okex({
        'apiKey': configEnv.apiKey,
        'secret': configEnv.apiSecret,
        'password': "That's1Me",
        'options': {
            'defaultType': 'swap',
            },
        })

        self.okx.load_markets()

    def convert_quote_to_contracts(self, symbol, amount):
        market = self.okx.market(symbol)
        price = self.okx.fetch_ticker(symbol)["last"]

        return int(amount / price / market['contractSize'])

    def open_short_position(self, pair, amount):
        quantity = self.convert_quote_to_contracts(pair, amount)

        self.okx.set_leverage(leverage=8, symbol=pair, params = {
            'mgnMode': 'isolated',
            'posSide': 'short'
        })
        
        order = self.okx.create_order(symbol=pair, side = 'sell', type='market', amount=quantity, params = {
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        self.okx.add_margin(symbol=pair, amount=0.6, params={
            'posSide': 'short'
        })

    def add_to_short_position(self, pair, amount):
        quantity = self.convert_quote_to_contracts(pair, amount)

        order = self.okx.create_order(symbol=pair, side = 'sell', type='market', amount=quantity, params = {
            'posSide': 'short',
            'tdMode': 'isolated',
        })
        

    def close_short_position(self, pair):
        pos = self.okx.fetch_position(pair)
        amount = int(pos['contracts'])

        order = self.okx.create_order(symbol=pair, side = 'buy', type='market', amount=amount, params = { 
            'posSide': 'short',
            'tdMode': 'isolated',
        })

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
        send_notification(f"Received signal type: {type_of_signal}, pair: {pair}, amount: {amount}")
        # connector.open_short_position(pair=pair, amount=amount)

    if(type_of_signal == 'add'):
         send_notification(f"Received signal type: {type_of_signal}, pair: {pair}, amount: {amount}")
        # connector.add_to_short_position(pair=pair, amount=amount)

    if(type_of_signal == 'close'):
         send_notification(f"Received signal type: close, pair: {pair}, amount: {amount}")
        # connector.close_short_position(pair=pair)

    return {}

def main():
    with Configurator() as config:
        config.add_route('handler', '/')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 80, app)
    server.serve_forever()