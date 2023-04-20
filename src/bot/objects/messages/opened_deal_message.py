from src.bot.objects.base_deal import BaseDeal
from decimal import Decimal


class OpenedDealMessage(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: Decimal,
        price: str
    ):
        super().__init__(pair=pair, quote_amount=quote_amount, price=price)

    def __str__(self):
        return f'Opened position: {self.pair}, size: {self.quote_amount}$'
