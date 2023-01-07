from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.models import Deal
from src.app.repositories.deal import deal as repository
from src.app.schemas import DealCreate
from src.app.schemas.deals import DealUpdate
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

def increment_safety_orders_count(exchange_id: int, db: Session = get_db()):
    deal = db.query(Deal).filter(Deal.date_close == None, exchange_id == exchange_id).order_by(Deal.id.desc()).first()
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

    return repository.update(db, deal, DealUpdate(safety_order_count=deal.safety_order_count + 1))

def get_deal_by_exchange_id(exchange_id: int, db: Session = get_db()):
    deal = db.query(Deal).filter(exchange_id == exchange_id).order_by(Deal.id.desc()).first()

    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal

def get_opened_deals(db: Session = get_db()):
    deals = db.query(Deal).filter(Deal.date_close == None).all()

    return deals

def update_deal_by_exchange_id(exchange_id, obj_in: DealUpdate, db: Session = get_db()):
    return update_deal(get_deal_by_exchange_id(exchange_id, db), obj_in, db)

def update_deal_by_id(id, obj_in: DealUpdate):
    return update_deal(get_deal(id), obj_in)

def update_deal(deal, obj_in: DealUpdate, db: Session = get_db()):
    if not deal:
        raise HTTPException(
            status_code=404,
            detail="The deal with this id does not exist in the system",
        )
    deal = repository.update(db, deal, obj_in)
    return deal
