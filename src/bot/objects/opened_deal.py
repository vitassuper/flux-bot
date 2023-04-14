from src.bot.objects.base_deal import BaseDeal


class OpenedDeal(BaseDeal):
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        price: str
    ):
        super().__init__(pair=pair, quote_amount=quote_amount, price=price)
