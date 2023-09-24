from decimal import Decimal
from typing import Union, Dict

import ccxt

from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.bot.exchange.decorators import retry_on_exception
from src.bot.models import Exchange
from src.bot.types.margin_type import MarginType
from src.bot.types.side_type import SideType


class Binance(BaseExchange):

    def get_exchange_name(self):
        return 'Binance'

    def __init__(self, exchange: Exchange) -> None:
        hedge_mode = exchange.hedge

        exchange = ccxt.binance({
            'apiKey': exchange.get_api_key(),
            'secret': exchange.get_api_secret(),
            'options': {
                'defaultType': 'future',
                'hedgeMode': hedge_mode
            },
            'enableRateLimit': True
        })

        self.hedge_mode = hedge_mode

        super().__init__(exchange=exchange)

    def get_current_leverage(self, pair: str, side: Union[SideType.long, SideType.short] = SideType.short):
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        position_side = 'BOTH'

        if self.hedge_mode:
            position_side = side.upper()

        position = next((p for p in positions if p['info']['positionSide'] == position_side), None)

        return position['leverage']

    def add_margin_to_long_position(self, pair: str, amount: float):
        raise NotImplementedError('This function is not implemented yet.')

    def add_margin_to_short_position(self, pair: str, amount: float):
        raise NotImplementedError('This function is not implemented yet.')

    @retry_on_exception()
    def get_opened_short_position(self, pair: str) -> Union[Dict, None]:
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        return next(
            (p for p in positions if p['contracts'] and p['side'] == SideType.short), None)

    def get_opened_long_position(self, pair: str) -> Union[Dict, None]:
        positions = self.ccxt_exchange.fetch_positions_risk([pair])

        return next(
            (p for p in positions if p['contracts'] and p['side'] == SideType.long), None)

    def get_order_status(self, order, pair):
        return order

    @retry_on_exception()
    def set_leverage_for_short_position(self, pair: str, leverage: int, margin_type: Union[
        MarginType.cross, MarginType.isolated] = MarginType.isolated) -> None:
        current_leverage = self.get_current_leverage(pair=pair, side=SideType.short)

        if current_leverage != leverage:
            self.ccxt_exchange.set_leverage(leverage, pair)

    @retry_on_exception()
    def buy_short_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        if self.hedge_mode:
            params = {'positionSide': 'SHORT'}
        else:
            params = {'reduceOnly': True}

        return self.ccxt_exchange.create_market_buy_order(
            symbol=pair,
            amount=amount,
            params=params
        )

    @retry_on_exception()
    def sell_short_position(self, pair: str, amount: float,
                            margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        if self.hedge_mode:
            params = {'positionSide': 'SHORT'}
        else:
            params = {}

        return self.ccxt_exchange.create_market_sell_order(
            symbol=pair,
            amount=amount,
            params=params
        )

    @retry_on_exception()
    def get_base_amount(self, pair: str, quote_amount: Decimal):
        market = self.ccxt_exchange.market(pair)
        price = self.ccxt_exchange.fetch_ticker(pair)['last']

        min_notional_filter = next(filter(lambda x: x['filterType'] == 'MIN_NOTIONAL', market['info']['filters']))

        min_notional = float(min_notional_filter['notional'])
        base_step = minimal_base_amount = market['limits']['amount']['min']

        while minimal_base_amount * price <= min_notional:
            minimal_base_amount += base_step

        minimal_quote_amount = minimal_base_amount * price

        # TODO: refactor this, if value + 300% less than minimal throw exception
        if minimal_quote_amount > quote_amount * 3:
            raise ConnectorException(
                f'low amount for pair {pair} - min amount: {minimal_quote_amount}')

        amount = max(minimal_quote_amount, quote_amount)

        # BADCODE to avoid min notional price
        amount = float(amount) * 1.05

        return self.ccxt_exchange.amount_to_precision(pair, amount=amount / price)

    def buy_long_position(self, pair: str, amount: float,
                          margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        if self.hedge_mode:
            params = {'positionSide': 'LONG'}
        else:
            params = {'reduceOnly': True}

        return self.ccxt_exchange.create_market_buy_order(
            symbol=pair,
            amount=amount,
            params=params
        )

    def sell_long_position(self, pair: str, amount: float,
                           margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated):
        if self.hedge_mode:
            params = {'positionSide': 'LONG'}
        else:
            params = {}

        return self.ccxt_exchange.create_market_sell_order(
            symbol=pair,
            amount=amount,
            params=params
        )

    @retry_on_exception()
    def set_leverage_for_long_position(self, pair: str, leverage: int,
                                       margin_type: Union[
                                           MarginType.cross, MarginType.isolated] = MarginType.isolated) -> None:
        current_leverage = self.get_current_leverage(pair=pair, side=SideType.long)

        if current_leverage != leverage:
            self.ccxt_exchange.set_leverage(leverage, pair)
