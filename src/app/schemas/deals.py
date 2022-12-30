from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class DealBase(BaseModel):
    id: Optional[int]
    pair: str = Field(max_length=255)
    exchangeId: str = Field(max_length=255)
    safety_order_count: int
    date_open: int
    date_close: Optional[int] = Field(default=None)
    pnl: Optional[float]


# Properties to receive via API on creation
class DealCreate(DealBase):
    pair: str = Field(max_length=255)
    exchangeId: str = Field(max_length=255)
    safety_order_count: int
    date_open: int
    pnl: Optional[float]


# Properties to receive via API on update
class DealUpdate(DealBase):
    safety_order_count: int
    date_close: int = Field(default=None)
    pnl: float
