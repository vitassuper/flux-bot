from decimal import Decimal
from dataclasses import dataclass


@dataclass
class BaseDeal:
    pair: str
    deal_id: int
    quote_amount: Decimal
    price: str
    base_amount: float
    title: str

    def __str__(self):
        return f'{self.title} - Deal id: #{self.deal_id}'
