import abc
from datetime import datetime
from decimal import Decimal

from ccxt import TRUNCATE

from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.strategy_db_helper import StrategyDBHelper
from src.bot.exchange.strategy_helper import StrategyHelper
from src.bot.objects.messages.averaged_deal_message import AveragedDealMessage
from src.bot.objects.closed_deal import ClosedDeal
from src.bot.objects.messages.closed_deal_message import ClosedDealMessage
from src.bot.objects.messages.opened_deal_message import OpenedDealMessage
from src.bot.objects.order import Order


class BaseStrategy(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, side: BaseSide, pair: str) -> None:
        self.bot_id = bot_id
        self.side = side
        self.exchange = side.exchange
        self.pair = pair

        contact_size = Decimal(self.exchange.get_market(pair=pair)['contractSize'])

        self.strategy_helper = StrategyHelper(taker_fee=Decimal(self.exchange.ccxt_exchange.market(self.pair)['taker']),
                                              side=side.get_side_type(), contract_size=contact_size)

        self.db_helper = StrategyDBHelper(side=side.get_side_type(), bot_id=self.bot_id, pair=self.pair)

    # Abstract methods

    @abc.abstractmethod
    async def open_deal_process(self, amount: float):
        pass

    @abc.abstractmethod
    async def close_deal_process(self, amount: float = None) -> ClosedDeal:
        pass

    @abc.abstractmethod
    async def average_deal_process(self, amount: float):
        pass

    # Helpers

    async def open_deal(self, amount: float) -> OpenedDealMessage:
        quote_amount, price = await self.open_deal_process(amount=amount)

        return OpenedDealMessage(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            price=price)

    async def average_deal(self, amount: float) -> AveragedDealMessage:
        safety_count, quote_amount = await self.average_deal_process(amount=amount)

        return AveragedDealMessage(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            safety_orders_count=safety_count,
            price='0'
        )

    async def close_deal(self, amount: float) -> ClosedDealMessage:
        closed_deal = await self.close_deal_process(amount=amount)

        return ClosedDealMessage(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, closed_deal.quote_amount),
            safety_orders_count=closed_deal.deal.safety_order_count,
            duration=StrategyHelper.get_time_duration_string(date_open=closed_deal.deal.date_open, date_close=datetime.now()),
            profit=self.exchange.ccxt_exchange.decimal_to_precision(closed_deal.deal.pnl, TRUNCATE, 4),
            profit_percentage=closed_deal.pnl_percentage,
            price='0'
        )

    def ensure_deal_opened(self):
        self.side.ensure_deal_opened(pair=self.pair)

    def ensure_deal_not_opened(self):
        self.side.ensure_deal_not_opened(pair=self.pair)

    def get_opened_position(self):
        return self.side.get_opened_position(pair=self.pair)

    def open_market_order(self, amount: float) -> Order:
        order = self.side.open_market_order(pair=self.pair, amount=amount)

        return Order(
            price=Decimal(order['average']),
            volume=Decimal(order['amount']),
            quote_amount=Decimal(self.get_quote_amount(order))
        )

    def average_market_order(self, amount: float) -> Order:
        order = self.side.open_market_order(pair=self.pair, amount=amount)

        return Order(
            price=Decimal(order['average']),
            volume=Decimal(order['amount']),
            quote_amount=Decimal(self.get_quote_amount(order))
        )

    def close_market_order(self, amount: float) -> Order:
        order = self.side.close_market_order(pair=self.pair, amount=amount)

        return Order(
            price=Decimal(order['average']),
            volume=Decimal(order['amount']),
            quote_amount=Decimal(self.get_quote_amount(order))
        )

    def set_leverage(self, leverage: int):
        self.side.set_leverage(pair=self.pair, leverage=leverage)

    # End helpers

    def get_quote_amount(self, order):
        market = self.exchange.get_market(pair=self.pair)

        return order['amount'] * market['contractSize'] * order['average']

    def get_base_amount(self, quote_amount: float) -> float:
        return self.side.exchange.get_base_amount(pair=self.pair, quote_amount=quote_amount)
