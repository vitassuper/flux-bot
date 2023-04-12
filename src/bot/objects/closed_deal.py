from src.bot.objects.base_deal import BaseDeal


class ClosedDeal(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        safety_orders_count: int,
        duration: str,
        profit: str,
        profit_percentage: str,
        price: str
    ):
        self.safety_orders_count = safety_orders_count
        self.duration = duration
        self.profit = profit
        self.profit_percentage = profit_percentage

        super().__init__(pair=pair, quote_amount=quote_amount, price=price)
