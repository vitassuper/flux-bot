from dataclasses import dataclass

from src.bot.objects.messages.base_deal_message import BaseDeal


@dataclass
class ClosedDealMessage(BaseDeal):
    safety_orders_count: int
    duration: str
    profit: str
    profit_percentage: float
    positions: str = ''

    def __str__(self):
        return (
            f'{super().__str__()}\n'
            f"Profit: <b>{self.profit}</b> {'💰💰💰' if float(self.profit) > 0 else '💀💀💀'} ({self.profit_percentage}%)\n"
            f'Size: {self.quote_amount}$ (safety orders: {self.safety_orders_count})\n'
            f'Duration: {self.duration}\n'
        ) + (f'\nPositions: {self.positions}' if self.positions else '')
