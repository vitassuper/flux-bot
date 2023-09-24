from typing import Literal, Optional, Union, Annotated
from pydantic import BaseModel, Field, PydanticUserError, RootModel


class OpenSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['open']
    pair: str
    amount: float
    position: Optional[Union[int, str]] = None


class CloseSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['close']
    pair: str
    position: Optional[Union[int, str]] = None
    amount: Optional[float] = None
    deal_id: Optional[int] = None


class AddSignal(BaseModel):
    bot_id: int
    type_of_signal: Literal['add']
    pair: str
    amount: float
    deal_id: Optional[int] = None
    position: Optional[Union[int, str]] = None
