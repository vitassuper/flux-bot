from src.bot.exchange.strategies.base_strategy import BaseStrategy


class GridStrategy(BaseStrategy):
    async def open_deal_process(self, amount: float):
        self.set_leverage(20)

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.open_market_order(amount=base_amount)

        price = order.price
        volume = order.volume

        deal = await self.db_helper.open_deal()

        await self.db_helper.create_open_order(deal_id=deal.id, price=price, volume=volume)

        return order.quote_amount, price

    async def average_deal_process(self, amount: float):
        # Not necessary for current strategy
        # self.ensure_deal_opened()

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.average_market_order(amount=base_amount)

        deal = await self.db_helper.get_deal()
        await self.db_helper.create_average_order(deal_id=deal.id, price=order.price, volume=order.volume)

        safety_count = await self.db_helper.average_deal(deal_id=deal.id)

        return safety_count, order.quote_amount

    async def close_deal_process(self, amount: float = None):
        self.ensure_deal_opened()

        deal = await self.db_helper.get_deal()

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

        return deal, pnl_percentage
