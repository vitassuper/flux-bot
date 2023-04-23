from dataclasses import dataclass
from decimal import Decimal
from typing import Union

from src.bot.types.side_type import SideType


@dataclass
class BaseDeal:
    pair: str
    side: Union[SideType.long, SideType.short]
    deal_id: int
    quote_amount: Decimal
    price: str
    base_amount: float
    title: str

    def __str__(self):
        return f"{self.title} - Deal id: #{self.deal_id} {'🟥' if self.side == SideType.short else '🟩'}"
