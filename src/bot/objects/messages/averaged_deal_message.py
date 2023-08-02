from dataclasses import dataclass
from decimal import Decimal

from src.bot.objects.messages.base_deal_message import BaseDeal


@dataclass
class AveragedDealMessage(BaseDeal):
    safety_orders_count: int
    total_quote_amount: Decimal

    def __str__(self):
        return (
            f'{super().__str__()}\n'
            f'Size: {self.quote_amount}$ (safety orders: {self.safety_orders_count})\n'
            f'Total amount: {self.total_quote_amount}$'
        )
