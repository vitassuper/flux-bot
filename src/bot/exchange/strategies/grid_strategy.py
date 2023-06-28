from decimal import Decimal
from typing import Union

from src.app.models import Deal
from src.bot.exchange.strategies.base_strategy import BaseStrategy
from src.bot.objects.closed_deal import ClosedDeal


class GridStrategy(BaseStrategy):
    async def open_deal_process(self, base_amount: Decimal):
        self.set_leverage(20)
        order = self.open_market_order(amount=base_amount)

        price = order.price
        volume = order.volume

        deal = await self.db_helper.open_deal()

        await self.db_helper.create_open_order(deal_id=deal.id, price=price, volume=volume)

        return order.quote_amount, price

    async def average_deal_process(self, deal: Deal, base_amount: Decimal):
        # Not necessary for current strategy
        # self.ensure_deal_opened()

        self.set_leverage(20)
        order = self.average_market_order(amount=base_amount)

        await self.db_helper.create_average_order(deal_id=deal.id, price=order.price, volume=order.volume)

        safety_count = await self.db_helper.average_deal(deal_id=deal.id)

        return safety_count, order.quote_amount

    async def close_deal_process(self, deal: Deal, amount: float = None) -> ClosedDeal:
        self.ensure_deal_opened()

        deal_stats = await self.db_helper.get_deal_stats(deal_id=deal.id)

        order = self.close_market_order(deal_stats.total_volume)

        await self.db_helper.create_close_order(deal_id=deal.id, price=order.price,
                                                volume=order.volume)

        pnl = self.strategy_helper.calculate_realized_pnl(deal_stats.total_volume,
                                                          deal_stats.average_price,
                                                          order.volume,
                                                          order.price)

        pnl_percentage = self.strategy_helper.calculate_pnl_percentage(deal_stats.average_price, order.price)

        deal = await self.db_helper.close_deal(deal_id=deal.id, pnl=pnl)

        return ClosedDeal(deal=deal, pnl_percentage=pnl_percentage, price=order.price, quote_amount=order.quote_amount)
