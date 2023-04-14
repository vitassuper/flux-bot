from src.bot.exchange.strategies.base_strategy import BaseStrategy


class GridStrategy(BaseStrategy):
    def _BaseStrategy__open_deal_process(self, amount: float):
        self.set_leverage(20)

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.open_market_order(amount=base_amount)

        quote_amount = self.get_quote_amount(order)

        self.open_deal_in_db()

        price = 0

        return quote_amount, price

    def _BaseStrategy__average_deal_process(self, amount: float):
        self.ensure_deal_opened()

        base_amount = self.get_base_amount(quote_amount=amount)

        order = self.average_market_order(amount=base_amount)

        quote_amount = self.get_quote_amount(order)

        safety_count = self.average_deal_in_db()

        return safety_count, quote_amount

    def _BaseStrategy__close_deal_process(self, amount: float = None):
        open_position = self.get_opened_position()

        base_amount = self.get_base_amount(quote_amount=amount)

        if round(base_amount / 100 * 125) > open_position['contracts']:
            base_amount = open_position['contracts']

        self.close_market_order(base_amount)

        deal = self.close_deal_in_db(pnl=0)

        return deal, '0'
