import ccxt

from datetime import datetime

from bot.models.deals import Deals
from bot.notificator import Notificator
from bot.settings import Config


class Connector:
    def __init__(self):
        configEnv = Config()

        self.config = configEnv
        self.notificator = Notificator()

        self.okx = ccxt.okex({
            'apiKey': configEnv.apiKey,
            'secret': configEnv.apiSecret,
            'password': "That's1Me",
            'options': {
                'defaultType': 'swap',
            },
        })

        self.okx.load_markets()

    def db_add_new_deal(self, pair, posId, date_open):
        deal = Deals(pair=pair, exchangeId=posId, date_open=date_open)
        deal.save()

    def db_close_deal(self, posId, pnl, timestamp):
        deal = Deals.get(Deals.exchangeId == posId, Deals.date_close.is_null())
        deal.pnl = pnl
        deal.date_close = timestamp
        deal.save()

    def db_add_safety_order(self, posId):
        deal = Deals.get(Deals.exchangeId == posId, Deals.date_close.is_null())
        deal.safety_order_count = deal.safety_order_count + 1
        deal.save()

    def db_get_deal(self, posId):
        deal = Deals.get(Deals.exchangeId == posId, Deals.date_close.is_null())

        return deal

    def convert_quote_to_contracts(self, symbol, amount):
        market = self.okx.market(symbol)
        price = self.okx.fetch_ticker(symbol)["last"]

        return int(amount / price / market['contractSize'])

    def get_open_positions(self):
        positions = self.okx.fetch_positions()

        result = ""
        for item in positions:
            result += (
                f"{item['info']['instId']}\n"
                f"margin: {item['info']['margin']}\n"
                f"entryPrice: {item['entryPrice']}\n"
                f"avgPrice: {item['info']['avgPx']}\n"
                f"unrealizedPnl: {item['unrealizedPnl']} ({round(item['percentage'], 2)}%)\n"
                f"liquidationPrice: {item['liquidationPrice']}\n"
                f"Pos size: {item['info']['notionalUsd']}💰"
            )

        return result

    def open_short_position(self, pair, amount, leverage=20, margin=None):
        self.notificator.send_notification(
            f"Received signal type: open, pair: {pair}, amount: {amount}")

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p['info']['instId'] == pair), None)

        if (open_position):
            self.notificator.send_warning_notification(
                f"Can't open new position, position already exists pair: {pair}")

            return

        quantity = self.convert_quote_to_contracts(pair, amount)

        if (quantity == 0):
            self.notificator.send_warning_notification(
                f"Can't open new position, low amount for pair: {pair}")

            return

        self.okx.set_leverage(leverage=leverage, symbol=pair, params={
            'mgnMode': 'isolated',
            'posSide': 'short'
        })

        order = self.okx.create_order(symbol=pair, side='sell', type='market', amount=quantity, params={
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p['info']['instId'] == pair), None)

        self.db_add_new_deal(
            pair, open_position['info']['posId'], datetime.now().timestamp())

        self.okx.add_margin(symbol=pair, amount=0.2, params={
            'posSide': 'short'
        })

    def add_to_short_position(self, pair, amount):
        self.notificator.send_notification(
            f"Received signal type: add, pair: {pair}, amount: {amount}")

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p['info']['instId'] == pair), None)

        if (not open_position):
            self.notificator.send_warning_notification(
                f"Can't average position, position not exists pair: {pair}")

            return

        quantity = self.convert_quote_to_contracts(pair, amount)

        if (quantity == 0):
            self.notificator.send_warning_notification(
                f"Can't average position, low amount for pair: {pair}")

            return

        order = self.okx.create_order(symbol=pair, side='sell', type='market', amount=quantity, params={
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        self.db_add_safety_order(open_position['info']['posId'])

        deal = self.db_get_deal(open_position['info']['posId'])

        self.notificator.send_notification(
            f"Averaged position ({deal.safety_order_count})")

    def close_short_position(self, pair):
        self.notificator.send_notification(
            f"Received signal type: close, pair: {pair}")

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p['info']['instId'] == pair), None)

        if (not open_position):
            self.notificator.send_warning_notification(
                f"Can't close position, position not exists pair: {pair}")

            return

        order = self.okx.create_order(symbol=pair, side='buy', type='market', amount=int(open_position['contracts']), params={
            'posSide': 'short',
            'tdMode': 'isolated',
        })

        id = order['id']

        result = self.okx.fetch_order(id, symbol=pair)

        self.db_close_deal(
            open_position['info']['posId'], result['info']['pnl'], result['timestamp'])

        self.notificator.send_notification(
            f"PNL:{result['info']['pnl']} Symbol:{result['symbol']} size: {result['info']['fillSz']}")
