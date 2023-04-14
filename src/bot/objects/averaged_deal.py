from src.bot.objects.base_deal import BaseDeal


class AveragedDeal(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        safety_orders_count: int,
        price: str
    ):
        self.safety_orders_count = safety_orders_count

        super().__init__(pair=pair, quote_amount=quote_amount, price=price)
