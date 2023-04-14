import abc
from datetime import datetime

from ccxt import TRUNCATE

from src.app.models import Deal
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, update_deal, increment_safety_orders_count, get_deal
from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.strategy_helper import StrategyHelper
from src.bot.objects.averaged_deal import AveragedDeal
from src.bot.objects.closed_deal import ClosedDeal
from src.bot.objects.opened_deal import OpenedDeal


class BaseStrategy(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, side: BaseSide, pair: str) -> None:
        self.bot_id = bot_id
        self.side = side
        self.exchange = side.exchange
        self.pair = pair

        self.strategy_helper = StrategyHelper(taker_fee=self.exchange.ccxt_exchange.market(self.pair)['taker'],
                                              side=side.get_type())

    # Abstract methods

    @abc.abstractmethod
    def open_deal_process(self, amount: float):
        pass

    @abc.abstractmethod
    def close_deal_process(self, amount: float = None):
        pass

    @abc.abstractmethod
    def average_deal_process(self, amount: float):
        pass

    # Helpers

    def open_deal(self, amount: float) -> OpenedDeal:
        quote_amount, price = self.open_deal_process(amount=amount)

        return OpenedDeal(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            price='0')

    def average_deal(self, amount: float) -> AveragedDeal:
        safety_count, quote_amount = self.average_deal_process(amount=amount)

        return AveragedDeal(
            pair=self.pair,
            quote_amount=quote_amount,
            safety_orders_count=safety_count,
            price='0'
        )

    def close_deal(self, amount: float) -> ClosedDeal:
        deal, pnl_percentage = self.close_deal_process(amount=amount)

        return ClosedDeal(
            pair=self.pair,
            quote_amount='Unknown',
            safety_orders_count=deal.safety_order_count,
            duration=StrategyHelper.get_time_duration_string(date_open=deal.date_open, date_close=datetime.now()),
            profit=self.exchange.ccxt_exchange.decimal_to_precision(deal.pnl, TRUNCATE, 4),
            profit_percentage=pnl_percentage,
            price='0'
        )

    def get_deal_in_db(self) -> Deal:
        return get_deal(bot_id=self.bot_id, pair=self.pair)

    def open_deal_in_db(self) -> Deal:
        return create_deal(DealCreate(bot_id=self.bot_id, pair=self.pair, date_open=datetime.now()))

    def close_deal_in_db(self, pnl: float) -> Deal:
        return update_deal(bot_id=self.bot_id, pair=self.pair, obj_in=DealUpdate(
            pnl=pnl, date_close=datetime.now()))

    def average_deal_in_db(self):
        return increment_safety_orders_count(
            bot_id=self.bot_id, pair=self.pair)

    def ensure_deal_opened(self):
        self.side.ensure_deal_opened(pair=self.pair)

    def ensure_deal_not_opened(self):
        self.side.ensure_deal_not_opened(pair=self.pair)

    def get_opened_position(self):
        return self.side.get_opened_position(pair=self.pair)

    def open_market_order(self, amount: float):
        return self.side.open_market_order(pair=self.pair, amount=amount)

    def average_market_order(self, amount: float):
        return self.side.open_market_order(pair=self.pair, amount=amount)

    def close_market_order(self, amount: float):
        return self.side.close_market_order(pair=self.pair, amount=amount)

    def set_leverage(self, leverage: int):
        self.side.set_leverage(pair=self.pair, leverage=leverage)

    # End helpers

    def get_quote_amount(self, order):
        market = self.exchange.get_market(pair=self.pair)

        return order['amount'] * market['contractSize'] * order['average']

    def get_base_amount(self, quote_amount: float) -> float:
        return self.side.exchange.get_base_amount(pair=self.pair, quote_amount=quote_amount)
