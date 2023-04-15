from src.bot.exchange.strategies.base_strategy import BaseStrategy


class GridStrategy(BaseStrategy):
    async def open_deal_process(self, amount: float):
        self.set_leverage(20)

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.open_market_order(amount=base_amount)

        price = order['average']
        volume = order['amount']

        quote_amount = self.get_quote_amount(order)

        deal = await self.db_helper.open_deal()

        db_order = await self.db_helper.create_open_order(deal_id=deal.id, price=price, volume=volume)

        return quote_amount, price

    async def average_deal_process(self, amount: float):
        self.ensure_deal_opened()

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.average_market_order(amount=base_amount)

        price = order['average']
        volume = order['amount']

        deal = await self.db_helper.get_deal()
        db_order = await self.db_helper.create_average_order(deal_id=deal.id, price=price, volume=volume)

        safety_count = await self.db_helper.average_deal(deal_id=deal.id)

        quote_amount = self.get_quote_amount(order=order)

        return safety_count, quote_amount

    async def close_deal_process(self, amount: float = None):
        open_position = self.get_opened_position()

        deal = await self.db_helper.get_deal()

        base_amount = await self.db_helper.get_deal_base_amount(deal_id=deal.id)

        order = self.close_market_order(base_amount)

        price = order['average']
        volume = order['amount']

        db_order = await self.db_helper.create_close_order(deal_id=deal.id, price=price, volume=volume)

        pnl = self.strategy_helper.calculate_realized_pnl(open_position['contracts'], open_position['entryPrice'],
                                                          order['amount'], order['average'])

        pnl_percentage = self.strategy_helper.calculate_pnl_percentage(open_position['entryPrice'], order['average'])

        deal = await self.db_helper.close_deal(deal_id=deal.id, pnl=pnl)

        return deal, pnl_percentage
