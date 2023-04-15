from src.bot.exchange.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    async def open_deal_process(self, amount: float):
        self.ensure_deal_not_opened()
        self.set_leverage(20)

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.open_market_order(amount=base_amount)

        price = order['average']
        volume = order['amount']

        quote_amount = self.get_quote_amount(order=order)

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.side.add_margin(self.pair, quote_amount * 0.06)

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

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.side.add_margin(pair=self.pair, quote_amount=quote_amount * 0.06)

        return safety_count, quote_amount

    async def close_deal_process(self, amount: float = None):
        open_position = self.get_opened_position()

        order = self.close_market_order(open_position['contracts'])

        price = order['average']
        volume = order['amount']

        deal = await self.db_helper.get_deal()

        db_order = await self.db_helper.create_close_order(deal_id=deal.id, price=price, volume=volume)

        pnl = self.strategy_helper.calculate_realized_pnl(open_position['contracts'], open_position['entryPrice'],
                                                          order['amount'], order['average'])

        pnl_percentage = self.strategy_helper.calculate_pnl_percentage(open_position['entryPrice'], order['average'])

        deal = await self.db_helper.close_deal(deal_id=deal.id, pnl=pnl)

        # quote_amount = self.get_quote_amount(order=order)

        return deal, pnl_percentage
