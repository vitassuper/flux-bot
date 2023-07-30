from typing import Literal, Optional, Union
from pydantic import BaseModel


class OpenSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['open']
    pair: str
    amount: float
    position: Optional[Union[int, str]]


class CloseSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['close']
    pair: str
    position: Optional[Union[int, str]]
    amount: Optional[float]
    deal_id: Optional[int]


class AddSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['add']
    pair: str
    amount: float
    deal_id: Optional[int]
    position: Optional[Union[int, str]]
