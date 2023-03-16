from src.bot.objects.base_position import BasePosition


class AveragedPosition(BasePosition):
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        safety_orders_count: int
    ):
        self.safety_orders_count = safety_orders_count

        super().__init__(pair=pair, quote_amount=quote_amount)
