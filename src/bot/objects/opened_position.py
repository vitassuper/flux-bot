from src.bot.objects.base_position import BasePosition


class OpenedPosition(BasePosition):
    def __init__(
        self,
        pair: str,
        quote_amount: str,
    ):
        super().__init__(pair=pair, quote_amount=quote_amount)
