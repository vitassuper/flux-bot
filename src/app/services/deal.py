from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.models import Deal
from src.app.repositories.deal import deal as repository
from src.app.schemas import DealCreate
from src.app.schemas.deals import DealUpdate
from src.db.session import SessionLocal


def create_deal(deal: DealCreate) -> Deal:
    return repository.create(obj_in=deal)


def increment_safety_orders_count(exchange_id: int) -> int:
    last_record = get_deal(exchange_id)
    return repository.increment_safety_orders_count(last_record)


def get_deal(exchange_id: int) -> Deal:
    deal = repository.get_last_record_with_exchange_id(exchange_id)

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


def get_opened_deals() -> List[Deal]:
    return repository.get_open_deals()


def update_deal(exchange_id, obj_in: DealUpdate) -> Deal:
    deal = get_deal(exchange_id)

    if not deal:
        raise HTTPException(
            status_code=404,
            detail="The deal with this id does not exist in the system",
        )
    deal = repository.update(deal, obj_in)
    return deal
