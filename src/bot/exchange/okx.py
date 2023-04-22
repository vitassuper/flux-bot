from typing import Union

import ccxt

from src.bot.exceptions.connector_exception import ConnectorException

from src.bot.exchange.base import BaseExchange
from src.bot.types.margin_type import MarginType
from src.bot.types.side_type import SideType
from src.core.config import settings


class Okex(BaseExchange):

    def get_exchange_name(self):
        return 'OKEX'

    def __init__(self, bot_id: int) -> None:
        exchange: ccxt.okex = ccxt.okex({
            'apiKey': settings.API_KEY,
            'secret': settings.API_SECRET,
            'password': settings.API_PASSWORD,
            'options': {
                'defaultType': 'swap',
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def get_opened_long_position(self, pair: str):
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.long.value), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def get_opened_short_position(self, pair: str):
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.short.value), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def ensure_long_position_not_opened(self, pair: str) -> None:
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.long), None)

        if open_position:
            raise ConnectorException(f'position already exists: {pair}')

    def ensure_long_position_opened(self, pair: str) -> None:
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.long), None)

        if not open_position:
            raise ConnectorException('position not exists')

    def ensure_short_position_opened(self, pair: str):
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.short), None)

        if not open_position:
            raise ConnectorException('position not exists')

    def ensure_short_position_not_opened(self, pair: str):
        positions = self.ccxt_exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p['symbol'] == pair and p['side'] == SideType.short), None)

        if open_position:
            raise ConnectorException(f'position already exists: {pair}')

    def get_base_amount(self, pair: str, quote_amount: float):
        market = self.ccxt_exchange.market(pair)
        price = self.ccxt_exchange.fetch_ticker(pair)['last']

        return int(quote_amount / price / market['contractSize'])

    def get_order_status(self, order, pair):
        return self.ccxt_exchange.fetch_order(order['id'], pair)

    def add_margin_to_short_position(self, pair: str, amount: float):
        self.ccxt_exchange.add_margin(symbol=pair, amount=amount,
                                      params={'posSide': SideType.short.value})

    def add_margin_to_long_position(self, pair: str, amount: float):
        self.ccxt_exchange.add_margin(symbol=pair, amount=amount,
                                      params={'posSide': SideType.long.value})

    def set_leverage(
        self,
        pair: str,
        leverage: int,
        side: Union[SideType.long, SideType.short] = SideType.short,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated
    ):
        self.ccxt_exchange.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={'mgnMode': margin_type.value, 'posSide': side.value},
        )

    def set_leverage_for_short_position(self, pair: str, leverage: int,
                                        margin_type: Union[
                                            MarginType.cross, MarginType.isolated] = MarginType.isolated):
        self.set_leverage(leverage=leverage,
                          pair=pair, margin_type=margin_type)

    def set_leverage_for_long_position(self, pair: str, leverage: int,
                                       margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        self.set_leverage(leverage=leverage,
                          pair=pair, side=SideType.long, margin_type=margin_type)

    def sell_short_position(self, pair: str, amount: float,
                            margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_sell_order(symbol=pair, amount=amount, params={
            'posSide': 'short',
            'tdMode': margin_type,
        })

    def buy_short_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_buy_order(symbol=pair, amount=amount, params={
            'posSide': 'short',
            'tdMode': margin_type,
        })

    def buy_long_position(self, pair: str, amount: float,
                          margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_buy_order(symbol=pair, amount=amount, params={
            'posSide': 'long',
            'tdMode': margin_type,
        })

    def sell_long_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_sell_order(symbol=pair, amount=amount, params={
            'posSide': 'long',
            'tdMode': margin_type,
        })
