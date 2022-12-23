import os
from dotenv import load_dotenv

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from .notificator import send_notification
import ccxt
import traceback
import logging


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

    def get_open_positions(self):
        positions = self.okx.fetch_positions()

        return positions

    def open_short_position(self, pair, amount, leverage = 20):
        send_notification(f"Received signal type: open, pair: {pair}, amount: {amount}")

        positions = self.okx.fetch_positions()

        open_position = next((p for p in positions if  p['info']['instId'] == pair), None)

        if(open_position):
            send_notification(f"Can't open new position, position already exists pair: {pair}")

            return

        quantity = self.convert_quote_to_contracts(pair, amount)

        self.okx.set_leverage(leverage=leverage, symbol=pair, params = {
            'mgnMode': 'isolated',
            'posSide': 'short'
        })
        
        order = self.okx.create_order(symbol=pair, side = 'sell', type='market', amount=quantity, params = {
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        self.okx.add_margin(symbol=pair, amount=0.5, params={
            'posSide': 'short'
        })

    def add_to_short_position(self, pair, amount):
        send_notification(f"Received signal type: add, pair: {pair}, amount: {amount}")

        positions = self.okx.fetch_positions()

        open_position = [p for p in positions if p['info']['instId'] == pair]

        if(len(open_position) == 0):
            send_notification(f"Can't average position, position not exists pair: {pair}")

            return

        quantity = self.convert_quote_to_contracts(pair, amount)

        order = self.okx.create_order(symbol=pair, side = 'sell', type='market', amount=quantity, params = {
            'posSide': 'short',
            'tdMode': 'isolated',
        })
        

    def close_short_position(self, pair):
        send_notification(f"Received signal type: close, pair: {pair}")

        positions = self.okx.fetch_positions()

        open_position = next((p for p in positions if  p['info']['instId'] == pair), None)

        if(not open_position):
            send_notification(f"Can't close position, position not exists pair: {pair}")

            return

        order = self.okx.create_order(symbol=pair, side = 'buy', type='market', amount=int(open_position['contracts']), params = { 
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        id = order['id']

        result = self.okx.fetch_order(id, symbol=pair)

        send_notification(f"PNL:{result['info']['pnl']} Symbol:{result['symbol']} size: {result['info']['fillSz']}")
        

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
        connector.open_short_position(pair=pair, amount=amount)

    if(type_of_signal == 'add'):
        connector.add_to_short_position(pair=pair, amount=amount)

    if(type_of_signal == 'close'):
        connector.close_short_position(pair=pair)

    if(type_of_signal == 'check'):
        positions = connector.get_open_positions()
        chatId = request.json_body.get('chat_id', '')
        result = ""

        for item in positions:
            result += f"symbol: {item['symbol']}, entryPrice: {item['entryPrice']}, unrealizedPnl: {item['unrealizedPnl']} ({round(item['percentage'], 2)}%), liquidationPrice: {item['liquidationPrice']} Pos size: {item['info']['notionalUsd']}💰\n"

        send_notification(result, chatId)

    return {}

def main():
    logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', level=logging.ERROR)
    try:
        with Configurator() as config:
            config.add_route('handler', '/')
            config.scan()
            app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 80, app)
        server.serve_forever()
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
