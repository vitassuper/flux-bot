from src.bot.exchange.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    def open_deal_process(self, amount: float):
        self.ensure_deal_not_opened()
        self.set_leverage(20)

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.open_market_order(amount=base_amount)

        quote_amount = self.get_quote_amount(order=order)

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.side.add_margin(self.pair, quote_amount * 0.06)

        self.open_deal_in_db()

        price = 0

        return quote_amount, price

    def average_deal_process(self, amount: float):
        self.ensure_deal_opened()

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.average_market_order(amount=base_amount)

        quote_amount = self.get_quote_amount(order=order)

        # TODO: only for okex, should be refactored
        if self.bot_id == 1 or self.bot_id == 3:
            self.side.add_margin(pair=self.pair, quote_amount=quote_amount * 0.06)

        safety_count = self.average_deal_in_db()

        return safety_count, quote_amount

    def close_deal_process(self, amount: float = None):
        open_position = self.get_opened_position()

        order = self.close_market_order(open_position['contracts'])

        pnl = self.strategy_helper.calculate_realized_pnl(open_position['contracts'], open_position['entryPrice'],
                                                          order['amount'], order['average'])

        pnl_percentage = self.strategy_helper.calculate_pnl_percentage(open_position['entryPrice'], order['average'])

        deal = self.close_deal_in_db(pnl=pnl)

        # quote_amount = self.get_quote_amount(order=order)

        return deal, pnl_percentage
