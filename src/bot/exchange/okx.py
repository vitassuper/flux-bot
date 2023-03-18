from typing import Literal, Union
import ccxt
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.core.config import settings


class Okex(BaseExchange):

    def get_exchange_name(self):
        return 'OKEX'

    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.okex({
            'apiKey': settings.API_KEY,
            'secret': settings.API_SECRET,
            'password': settings.API_PASSWORD,
            'options': {
                'defaultType': 'swap',
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def get_opened_position(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def ensure_long_position_not_opened(self, pair: str) -> None:
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == 'long'), None)

        if open_position:
            raise ConnectorException(f'position already exists: {pair}')

    def ensure_long_position_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == 'long'), None)

        if not open_position:
            raise ConnectorException('position not exists')

    def ensure_short_position_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == 'short'), None)

        if not open_position:
            raise ConnectorException('position not exists')

    def ensure_short_position_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == 'short'), None)

        if open_position:
            raise ConnectorException(f'position already exists: {pair}')

    def get_base_amount(self, pair: str, quote_amount: float):
        market = self.exchange.market(pair)
        price = self.exchange.fetch_ticker(pair)['last']

        return int(quote_amount / price / market['contractSize'])

    def get_order_status(self, order, pair):
        return self.exchange.fetch_order(order['id'], pair)

    def add_margin_to_short_position(self, pair: str, amount: float):
        self.exchange.add_margin(symbol=pair, amount=amount,
                                 params={'posSide': 'short'})

    def add_margin_to_long_position(self, pair: str, amount: float):
        self.exchange.add_margin(symbol=pair, amount=amount,
                                 params={'posSide': 'long'})

    def set_leverage(self, pair: str, leverage: int, side: Union[Literal['long'], Literal['short']] = 'short'):
        self.exchange.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={'mgnMode': 'isolated', 'posSide': side},
        )

    def set_leverage_for_short_position(self, pair: str, leverage: int):
        self.set_leverage(leverage=leverage,
                          pair=pair)

    def set_leverage_for_long_position(self, pair: str, leverage: int):
        self.set_leverage(leverage=leverage,
                          pair=pair, side='long')

    def sell_short_position(self, pair: str, amount: int):
        return self.exchange.create_market_sell_order(symbol=pair, amount=amount, params={
            'posSide': 'short',
            'tdMode': 'isolated',
        })

    def buy_short_position(self, pair: str, amount: int):
        return self.exchange.create_market_buy_order(symbol=pair, amount=amount, params={
            'posSide': 'short',
            'tdMode': 'isolated',
        })

    def buy_long_position(self, pair: str, amount: int):
        return self.exchange.create_market_buy_order(symbol=pair, amount=amount, params={
            'posSide': 'long',
            'tdMode': 'isolated',
        })

    def sell_long_position(self, pair: str, amount: int):
        return self.exchange.create_market_sell_order(symbol=pair, amount=amount, params={
            'posSide': 'long',
            'tdMode': 'isolated',
        })
