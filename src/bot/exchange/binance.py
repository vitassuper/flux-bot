from typing import Union
from decimal import Decimal
import ccxt

from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.bot.types.margin_type import MarginType
from src.core.config import settings


class Binance(BaseExchange):

    def get_exchange_name(self):
        return 'Binance'

    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.binance({
            'apiKey': settings.API_KEY_BINANCE,
            'secret': settings.API_SECRET_BINANCE,
            'options': {
                'defaultType': 'future',
            },
            'enableRateLimit': True
        })

        super().__init__(bot_id=bot_id, exchange=exchange)

    def ensure_long_position_not_opened(self, pair: str):
        raise NotImplementedError('This function is not implemented yet.')

    def ensure_long_position_opened(self, pair: str) -> None:
        raise NotImplementedError('This function is not implemented yet.')

    def add_margin_to_long_position(self, pair: str, amount: float):
        raise NotImplementedError('This function is not implemented yet.')

    def add_margin_to_short_position(self, pair: str, amount: float):
        raise NotImplementedError('This function is not implemented yet.')

    def ensure_short_position_not_opened(self, pair: str) -> None:
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if open_position:
            raise ConnectorException(f'position already exists: {pair}')

    def ensure_short_position_opened(self, pair: str) -> None:
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if not open_position:
            raise ConnectorException(f'position not exists: {pair}')

    def get_opened_short_position(self, pair: str):
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        open_position = next(
            (p for p in positions if p['contracts']), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def get_opened_long_position(self, pair: str):
        raise NotImplementedError('This function is not implemented yet.')

    def get_order_status(self, order, pair):
        return order

    def set_leverage_for_short_position(self, pair: str, leverage: int, margin_type: Union[
        MarginType.cross, MarginType.isolated] = MarginType.isolated):
        self.ccxt_exchange.set_leverage(leverage, pair)

    def buy_short_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_buy_order(
            symbol=pair,
            amount=amount,
            params={'reduceOnly': True}
        )

    def sell_short_position(self, pair: str, amount: float,
                            margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        return self.ccxt_exchange.create_market_sell_order(
            symbol=pair,
            amount=amount,
        )

    def get_base_amount(self, pair: str, quote_amount: Decimal):
        market = self.ccxt_exchange.market(pair)
        price = self.ccxt_exchange.fetch_ticker(pair)['last']

        min_notional_filter = next(
            filter(lambda x: x['filterType'] == 'MIN_NOTIONAL', market['info']['filters']))

        min_notional = float(min_notional_filter['notional'])
        minimal_quote_amount = market['limits']['amount']['min'] * price

        minimal_amount = max(minimal_quote_amount, min_notional)

        if float(quote_amount) < minimal_amount:
            raise ConnectorException(
                f'low amount for pair {pair} - min amount: {minimal_amount}')

        return self.ccxt_exchange.amount_to_precision(pair, amount=float(quote_amount / price))

    def buy_long_position(self, pair: str, amount: float,
                          margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        raise NotImplementedError('This function is not implemented yet.')

    def sell_long_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        raise NotImplementedError('This function is not implemented yet.')

    def set_leverage_for_long_position(self, pair: str, leverage: int,
                                       margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        raise NotImplementedError('This function is not implemented yet.')
