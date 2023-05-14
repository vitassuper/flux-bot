from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DealStats:
    average_price: float
    total_volume: float
    total_quote_amount: Decimal
