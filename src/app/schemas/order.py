from dataclasses import Field
from typing import Optional
from pydantic import BaseModel


class OrderBase(BaseModel):
    id: Optional[int]
    deal_id: Optional[int]
    side: str = Field(max_length=10)
    price: Optional[float]
    volume: Optional[float]


class OrderCreate(BaseModel):
    deal_id: int
    side: str = Field(max_length=10)
    price: float
    volume: float
