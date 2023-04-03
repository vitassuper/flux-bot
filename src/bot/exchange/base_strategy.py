import abc
from datetime import datetime
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, get_deal, increment_safety_orders_count, update_deal
from src.bot.exchange.base import BaseExchange
from src.bot.helper import calculate_position_pnl_for_position, get_time_duration_string
from src.bot.objects.averaged_position import AveragedPosition
from src.bot.objects.closed_position import ClosedPosition
from src.bot.objects.opened_position import OpenedPosition

from ccxt.base.decimal_to_precision import TRUNCATE


class BaseStrategy(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, exchange: BaseExchange) -> None:
        self.bot_id = bot_id
        self.exchange = exchange

    # Abstract method

    @abc.abstractmethod
    def ensure_deal_not_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def ensure_deal_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def set_leverage(self, pair: str, leverage: int):
        pass

    @abc.abstractmethod
    def open_market_order(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def close_market_order(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def add_margin(self, pair: str, quote_amount: float):
        pass

    @abc.abstractmethod
    def get_opened_position(self, pair: str):
        pass

    def get_base_amount(self, pair: str, quote_amount: float) -> float:
        return self.exchange.get_base_amount(pair=pair, quote_amount=quote_amount)

    def average_market_order(self, pair: str, amount: float):
        return self.open_market_order(pair=pair, amount=amount)

    def calculate_realized_pnl(self, position, order):
        market = self.exchange.exchange.market(order['symbol'])

        amount = order['amount'] * market['contractSize']

        entry_value = position['entryPrice'] * amount
        exit_value = order['average'] * amount

        u_pnl = exit_value - entry_value

        open_fee = position['entryPrice'] * amount * market['taker']
        close_fee = order['average'] * amount * market['taker']

        if position['side'] == 'short':
            u_pnl = u_pnl * -1

        return u_pnl - open_fee - close_fee

    def calculate_pnl_percentage(self, position, order):
        return calculate_position_pnl_for_position(
            order['average'], position['entryPrice'], float(
                position['leverage']), position['side']
        )

    def open_deal(self, pair: str, amount: float):
        self.ensure_deal_not_opened(pair)
        self.set_leverage(pair, 20)

        base_amount = self.get_base_amount(pair=pair, quote_amount=amount)

        order = self.open_market_order(pair=pair, amount=base_amount)

        market = self.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.add_margin(pair, quote_amount * 0.06)

        create_deal(DealCreate(bot_id=self.bot_id,
                    pair=order['symbol'], date_open=datetime.now()))

        return OpenedPosition(pair=pair, quote_amount=self.exchange.exchange.cost_to_precision(order['symbol'], quote_amount))

    def average_deal(self, pair: str, amount: float):
        self.ensure_deal_opened(pair)

        base_amount = self.get_base_amount(pair=pair, quote_amount=amount)

        order = self.average_market_order(pair=pair, amount=base_amount)

        market = self.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.add_margin(pair, quote_amount * 0.06)

        safety_count = increment_safety_orders_count(
            bot_id=self.bot_id, pair=pair)

        return AveragedPosition(
            pair=pair,
            quote_amount=self.exchange.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=safety_count
        )

    def close_deal(self, pair: str, amount: float):
        open_position = self.get_opened_position(pair)

        order = self.close_market_order(pair, open_position['contracts'])

        deal = get_deal(bot_id=self.bot_id, pair=pair)

        pnl = self.calculate_realized_pnl(open_position, order)
        pnl_percentage = self.calculate_pnl_percentage(open_position, order)

        update_deal(bot_id=self.bot_id, pair=pair, obj_in=DealUpdate(
            pnl=pnl, date_close=datetime.now()))

        duration = get_time_duration_string(
            date_open=deal.date_open, date_close=datetime.now())

        market = self.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        return ClosedPosition(
            pair=pair,
            quote_amount=self.exchange.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=deal.safety_order_count,
            duration=duration,
            profit=self.exchange.exchange.decimal_to_precision(
                pnl, TRUNCATE, 4),
            profit_percentage=pnl_percentage
        )
