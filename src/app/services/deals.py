from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.models import Deal
from src.app.repositories.deals import deal as repository
from src.app.schemas import DealCreate
from src.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    return db


def create_deal(deal: DealCreate, db: Session = get_db()):
    return repository.create(db=db, obj_in=deal)


def get_deal(deal_id: int, db: Session = get_db()) -> Deal:
    deal = repository.get(db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


def update_deal(deal_id, obj_in, db: Session = get_db()):
    deal = get_deal(deal_id, db)
    if not deal:
        raise HTTPException(
            status_code=404,
            detail="The deal with this id does not exist in the system",
        )
    deal = repository.update(db, deal, obj_in)
    return deal
