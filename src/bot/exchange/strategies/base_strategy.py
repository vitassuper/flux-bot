import abc
from datetime import datetime
from decimal import Decimal

from ccxt import TRUNCATE

from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.strategy_db_helper import StrategyDBHelper
from src.bot.exchange.strategy_helper import StrategyHelper
from src.bot.objects.averaged_deal import AveragedDeal
from src.bot.objects.closed_deal import ClosedDeal
from src.bot.objects.opened_deal import OpenedDeal
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
    async def close_deal_process(self, amount: float = None):
        pass

    @abc.abstractmethod
    async def average_deal_process(self, amount: float):
        pass

    # Helpers

    async def open_deal(self, amount: float) -> OpenedDeal:
        quote_amount, price = await self.open_deal_process(amount=amount)

        return OpenedDeal(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            price='0')

    async def average_deal(self, amount: float) -> AveragedDeal:
        safety_count, quote_amount = await self.average_deal_process(amount=amount)

        return AveragedDeal(
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            safety_orders_count=safety_count,
            price='0'
        )

    async def close_deal(self, amount: float) -> ClosedDeal:
        deal, pnl_percentage = await self.close_deal_process(amount=amount)

        return ClosedDeal(
            pair=self.pair,
            quote_amount='Unknown',
            safety_orders_count=deal.safety_order_count,
            duration=StrategyHelper.get_time_duration_string(date_open=deal.date_open, date_close=datetime.now()),
            profit=self.exchange.ccxt_exchange.decimal_to_precision(deal.pnl, TRUNCATE, 4),
            profit_percentage=pnl_percentage,
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
