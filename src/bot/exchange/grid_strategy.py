from datetime import datetime
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, get_deal, increment_safety_orders_count, update_deal
from src.bot.exchange.base_strategy import BaseStrategy
from src.bot.helper import get_time_duration_string
from src.bot.objects.averaged_position import AveragedPosition
from src.bot.objects.closed_position import ClosedPosition
from src.bot.objects.opened_position import OpenedPosition


class GridStrategy():
    def __init__(self, bot_id: int, strategy: BaseStrategy) -> None:
        self.bot_id = bot_id
        self.strategy = strategy

    def open_deal(self, pair: str, amount: float):
        self.strategy.set_leverage(pair, 20)

        base_amount = self.strategy.get_base_amount(
            pair=pair, quote_amount=amount)

        order = self.strategy.open_market_order(pair=pair, amount=base_amount)

        market = self.strategy.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        create_deal(DealCreate(bot_id=self.bot_id,
                    pair=order['symbol'], date_open=datetime.now()))

        return OpenedPosition(pair=pair, quote_amount=self.strategy.exchange.exchange.cost_to_precision(order['symbol'], quote_amount))

    def average_deal(self, pair: str, amount: float):
        self.strategy.ensure_deal_opened(pair)

        base_amount = self.strategy.get_base_amount(
            pair=pair, quote_amount=amount)

        order = self.strategy.average_market_order(
            pair=pair, amount=base_amount)

        market = self.strategy.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        safety_count = increment_safety_orders_count(
            bot_id=self.bot_id, pair=pair)

        return AveragedPosition(
            pair=pair,
            quote_amount=self.strategy.exchange.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=safety_count
        )

    def close_deal(self, pair: str, amount: float):
        open_position = self.strategy.get_opened_position(pair)

        base_amount = self.strategy.get_base_amount(
            pair=pair, quote_amount=amount)

        if (round(base_amount / 100 * 125) > open_position['contracts']):
            base_amount = open_position['contracts']

        order = self.strategy.close_market_order(pair, base_amount)

        deal = get_deal(bot_id=self.bot_id, pair=pair)

        update_deal(bot_id=self.bot_id, pair=pair, obj_in=DealUpdate(
            pnl=0, date_close=datetime.now()))

        duration = get_time_duration_string(
            date_open=deal.date_open, date_close=datetime.now())

        market = self.strategy.exchange.exchange.market(order['symbol'])
        quote_amount = order['amount'] * \
            market['contractSize'] * order['average']

        return ClosedPosition(
            pair=pair,
            quote_amount=self.strategy.exchange.exchange.cost_to_precision(
                order['symbol'], quote_amount),
            safety_orders_count=deal.safety_order_count,
            duration=duration,
            profit='Non available',
            profit_percentage='Non available'
        )
