from src.bot.objects.base_deal import BaseDeal
from decimal import Decimal


class AveragedDealMessage(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: Decimal,
        safety_orders_count: int,
        price: str
    ):
        self.safety_orders_count = safety_orders_count

        super().__init__(pair=pair, quote_amount=quote_amount, price=price)

    def __str__(self):
        return f'Averaged position, pair: {self.pair}, size: {self.quote_amount}$ safety orders: {self.safety_orders_count}'
