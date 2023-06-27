import abc
from datetime import datetime
from decimal import Decimal
from typing import Union

from ccxt import TRUNCATE

from src.app.models import Deal
from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.strategy_db_helper import StrategyDBHelper
from src.bot.exchange.strategy_helper import StrategyHelper
from src.bot.objects.closed_deal import ClosedDeal
from src.bot.objects.messages.averaged_deal_message import AveragedDealMessage
from src.bot.objects.messages.closed_deal_message import ClosedDealMessage
from src.bot.objects.messages.opened_deal_message import OpenedDealMessage
from src.bot.objects.order import Order


class BaseStrategy(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, side: BaseSide, pair: str) -> None:
        self.bot_id = bot_id
        self.side = side
        self.exchange = side.exchange
        self.pair = pair

        self.contract_size = Decimal(self.exchange.get_market(pair=pair)['contractSize'])

        self.strategy_helper = StrategyHelper(taker_fee=Decimal(self.exchange.ccxt_exchange.market(self.pair)['taker']),
                                              side=side.get_side_type(), contract_size=self.contract_size)

        self.db_helper = StrategyDBHelper(side=side.get_side_type(), bot_id=self.bot_id, pair=self.pair)

    # Abstract methods
    @abc.abstractmethod
    async def open_deal_process(self, base_amount: Decimal):
        pass

    @abc.abstractmethod
    async def close_deal_process(self, amount: float = None, deal: Union[Deal, None] = None) -> ClosedDeal:
        pass

    @abc.abstractmethod
    async def average_deal_process(self, base_amount: Decimal):
        pass

    # Helpers
    async def open_deal(self, amount: float) -> OpenedDealMessage:
        base_amount = self.get_base_amount(quote_amount=Decimal(amount))
        quote_amount, price = await self.open_deal_process(base_amount=base_amount)

        deal = await self.db_helper.get_deal()

        return OpenedDealMessage(
            title=f'Bot id: {self.bot_id} ({self.exchange.get_exchange_name()})',
            pair=self.pair,
            base_amount=0.1,  # TODO: remove magic number
            deal_id=deal.id,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            price=price,
            side=self.side.get_side_type()
        )

    async def average_deal(self, amount: float) -> AveragedDealMessage:
        base_amount = self.get_base_amount(quote_amount=Decimal(amount))
        safety_count, quote_amount = await self.average_deal_process(base_amount=base_amount)

        deal = await self.db_helper.get_deal()
        deal_stats = await self.db_helper.get_deal_stats(deal_id=deal.id)

        return AveragedDealMessage(
            title=f'Bot id: {self.bot_id} ({self.exchange.get_exchange_name()})',
            base_amount=0.1,  # TODO: remove magic number,
            deal_id=deal.id,
            pair=self.pair,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, quote_amount),
            safety_orders_count=safety_count,
            price='0',
            side=self.side.get_side_type(),
            total_quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair,
                                                                             deal_stats.total_quote_amount *
                                                                             self.contract_size)
        )

    async def close_deal(self, amount: float, deal: Union[Deal, None] = None) -> ClosedDealMessage:
        closed_deal = await self.close_deal_process(amount=amount, deal=deal)

        return ClosedDealMessage(
            title=f'Bot id: {self.bot_id} ({self.exchange.get_exchange_name()})',
            deal_id=closed_deal.deal.id,
            pair=self.pair,
            base_amount=0.1,  # TODO: remove magic number,
            quote_amount=self.exchange.ccxt_exchange.cost_to_precision(self.pair, closed_deal.quote_amount),
            safety_orders_count=closed_deal.deal.safety_order_count,
            duration=StrategyHelper.get_time_duration_string(date_open=closed_deal.deal.date_open,
                                                             date_close=datetime.now()),
            profit=self.exchange.ccxt_exchange.decimal_to_precision(closed_deal.deal.pnl, TRUNCATE, 4),
            profit_percentage=closed_deal.pnl_percentage,
            price='0',
            side=self.side.get_side_type()
        )

    def ensure_deal_opened(self):
        self.side.ensure_deal_opened(pair=self.pair)

    def ensure_deal_not_opened(self):
        self.side.ensure_deal_not_opened(pair=self.pair)

    def get_opened_position(self):
        return self.side.get_opened_position(pair=self.pair)

    def open_market_order(self, amount: Decimal) -> Order:
        order = self.side.open_market_order(pair=self.pair, amount=float(amount))

        return Order(
            price=Decimal(order['average']),
            volume=Decimal(order['amount']),
            quote_amount=Decimal(self.get_quote_amount(order))
        )

    def average_market_order(self, amount: Decimal) -> Order:
        order = self.side.open_market_order(pair=self.pair, amount=float(amount))

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
        return order['amount'] * float(self.contract_size) * order['average']

    def get_base_amount(self, quote_amount: Decimal) -> Decimal:
        # TODO: all types should be decimal
        return Decimal(self.side.exchange.get_base_amount(pair=self.pair, quote_amount=quote_amount))
