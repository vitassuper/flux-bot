import ccxt

from datetime import datetime

from bot.models.deals import Deals
from bot.notificator import Notificator
from bot.settings import Config
from decimal import Decimal, ROUND_DOWN

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

    def db_get_opened_deals(self):
        query = Deals.select().where(Deals.date_close.is_null())

        return query

    def db_get_deal(self, posId):
        deal = Deals.get(Deals.exchangeId == posId, Deals.date_close.is_null())

        return deal

    def convert_quote_to_contracts(self, symbol, amount):
        market = self.okx.market(symbol)
        price = self.okx.fetch_ticker(symbol)["last"]

        return int(amount / price / market['contractSize'])


    def findElement(self, items, function):
        for item in items:
            if function(item):
                return item

    def get_open_positions(self):
        positions = self.okx.fetch_positions()
        positions.sort(key=lambda item: item['info']['instId'])
        deals = self.db_get_opened_deals()

        result = ""
        for item in positions:
            deal = self.findElement(deals, (lambda deal: deal.pair == item['info']['instId']))

            result += (
                f"{item['info']['instId']}\n"
                f"margin: {Decimal(item['info']['margin']).quantize(Decimal('0.001'))}\n"
                f"entryPrice: {item['entryPrice']}\n"
                f"avgPrice: {item['info']['avgPx']}\n"
                f"unrealizedPnl: {Decimal(item['unrealizedPnl']).quantize(Decimal('0.0001'))} ({round(item['percentage'], 2)}%)\n"
                f"liquidationPrice: {item['liquidationPrice']}\n"
                f"Pos size: {Decimal(item['info']['notionalUsd']).quantize(Decimal('0.001'))}💰\n"
                f"Duration: {self.get_time_duration(deal.date_open, datetime.now())}\n"
                f"Safety orders {deal.safety_order_count if deal else 'Unknown info'}\n\n"
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

        self.okx.add_margin(symbol=pair, amount=0.7, params={
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

        result = self.okx.fetch_order(order['id'], symbol=pair)

        deal = self.db_get_deal(open_position['info']['posId'])

        self.db_close_deal(
            open_position['info']['posId'], result['info']['pnl'], result['timestamp'])

        pnl = Decimal(result['info']['pnl']).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)

        avgPrice = open_position['entryPrice']
        price = result['price']

        pnl_percentage = self.calculate_pnl_percentage(price, avgPrice, float(result['info']['lever']), result['info']['posSide'])

        duration = self.get_time_duration(deal.date_open, datetime.fromtimestamp(result['timestamp'] / 1000))

        self.notificator.send_notification((
            f"{result['symbol']}\n"
            f"Profit:{pnl}$ ({pnl_percentage}%)\n"
            f"Size: {result['info']['fillSz']}\n"
            f"Duration: {duration}"
        ))

    def get_time_duration(self, date_open, date_close):
        diff = date_close - date_open
        seconds_duration = diff.total_seconds()

        days, seconds = divmod(seconds_duration, 86400)
        hours, seconds = divmod(seconds_duration, 3600)
        minutes, seconds = divmod(seconds_duration, 60)

        hours, minutes = divmod(minutes, 60)

        return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"
    
    def calculate_pnl_percentage(self, closePrice, avgPrice, leverage, posSide):
        sign = 1

        if(posSide == 'short' and closePrice > avgPrice):
            sign = -1

        if(posSide == 'long' and closePrice < avgPrice):
            sign = -1

        return Decimal(((closePrice - avgPrice) / avgPrice) * float(leverage) * 100 * sign).quantize(Decimal('0.01'))