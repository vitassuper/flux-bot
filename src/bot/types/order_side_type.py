from enum import Enum


class OrderSideType(str, Enum):
    buy = 'buy'
    sell = 'sell'
