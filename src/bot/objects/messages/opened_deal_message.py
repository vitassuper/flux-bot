from dataclasses import dataclass

from src.bot.objects.messages.base_deal_message import BaseDeal


@dataclass
class OpenedDealMessage(BaseDeal):
    def __str__(self):
        return (
            f'{super().__str__()}\n'
            f'Opened position: {self.pair}, size: {self.quote_amount}$'
        )
