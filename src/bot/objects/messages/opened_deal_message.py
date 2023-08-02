from dataclasses import dataclass
from typing import Optional

from src.bot.objects.messages.base_deal_message import BaseDeal


@dataclass
class OpenedDealMessage(BaseDeal):
    positions: str = ''

    def __str__(self):
        return (
            f'{super().__str__()}\n'
            f'Size: {self.quote_amount}$'
        ) + (f'\nPositions: {self.positions}' if self.positions else '')
