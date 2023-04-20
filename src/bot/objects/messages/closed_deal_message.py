from src.bot.objects.base_deal import BaseDeal
from decimal import Decimal


class ClosedDealMessage(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: Decimal,
        safety_orders_count: int,
        duration: str,
        profit: str,
        profit_percentage: float,
        price: str
    ):
        self.safety_orders_count = safety_orders_count
        self.duration = duration
        self.profit = profit
        self.profit_percentage = profit_percentage

        super().__init__(pair=pair, quote_amount=quote_amount, price=price)

    def __str__(self):
        return (
            f'{self.pair}\n'
            f'Profit:{self.profit}💰💰💰 ({self.profit_percentage}%)\n'
            f'Size: {self.quote_amount}$\n'
            f'Duration: {self.duration}\n'
            f'Safety orders: {self.safety_orders_count}'
        )
