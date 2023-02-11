from typing import Any, Dict, List, Union

from sqlalchemy.orm import Session

from src.app.repositories.base import CRUDBase, ModelType
from src.app.models.deal import Deal
from src.app.schemas.deals import DealCreate, DealUpdate

from src.db.session import SessionLocal


class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    def create(self, obj_in: DealCreate) -> Deal:
        db_obj = Deal(
            pair=obj_in.pair,
            exchange_id=obj_in.exchange_id,
            date_open=obj_in.date_open,
            pnl=obj_in.pnl
        )

        with SessionLocal() as session:
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

        return db_obj

    def update(self, db_obj: Deal, obj_in: Union[DealUpdate, Dict[str, Any]]) -> Deal:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

            return super().update(db_obj=db_obj, obj_in=update_data)

    def get_last_record_with_exchange_id(self, exchange_id):
        with SessionLocal() as session:
            return session.query(self.model).filter(self.model.exchange_id == exchange_id).order_by(self.model.id.desc()).first()

    def get_open_deals(self) -> List[ModelType]:
        with SessionLocal() as session:
            return session.query(self.model).filter(self.model.date_close == None).all()

    def increment_safety_orders_count(self, record):
        with SessionLocal() as session:
            record.safety_order_count += 1
            session.add(record)
            session.commit()

            return True


deal = CRUDDeal(Deal)
