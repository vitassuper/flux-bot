from typing import Literal, Optional
from pydantic import BaseModel


class OpenSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['open']
    pair: str
    amount: float
    position: Optional[int]


class CloseSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['close']
    pair: str
    position: Optional[int]
    amount: Optional[float]
    deal_id: Optional[int]


class AddSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['add']
    pair: str
    amount: float
    deal_id: Optional[int]
    position: Optional[int]
