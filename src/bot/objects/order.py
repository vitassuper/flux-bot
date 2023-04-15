from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Order:
    price: Decimal
    volume: Decimal
