from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class DealBase(BaseModel):
    id: Optional[int]
    pair: str = Field(max_length=255)
    safety_order_count: Optional[int]
    date_open: datetime
    date_close: Optional[datetime] = Field(default=None)
    pnl: Optional[float]
    bot_id: Optional[int]


# Properties to receive via API on creation
class DealCreate(BaseModel):
    bot_id: int
    pair: str = Field(max_length=255)
    date_open: datetime
    pnl: Optional[float]


# Properties to receive via API on update
class DealUpdate(BaseModel):
    safety_order_count: Optional[int]
    date_close: Optional[datetime] = Field(default=None)
    pnl: Optional[float]
