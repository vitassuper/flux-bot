from dataclasses import dataclass

from src.bot.objects.messages.base_deal_message import BaseDeal


@dataclass
class AveragedDealMessage(BaseDeal):
    safety_orders_count: int

    def __str__(self):
        return (
            f'{super().__str__()}\n'
            f'Averaged position, pair: {self.pair}, size: {self.quote_amount}$ safety orders: {self.safety_orders_count}'
        )
