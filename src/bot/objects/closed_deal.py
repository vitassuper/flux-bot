from dataclasses import dataclass
from decimal import Decimal

from src.db.models import Deal


@dataclass
class ClosedDeal:
    price: Decimal
    pnl_percentage: float
    quote_amount: Decimal
    deal: Deal
