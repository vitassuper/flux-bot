from datetime import datetime
from typing import Any, Dict, List, Union

from sqlalchemy import func

from src.app.repositories.base import CRUDBase, ModelType
from src.app.models.deal import Deal
from src.app.schemas.deals import DealCreate, DealUpdate

from src.db.session import SessionLocal


class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    def create(self, obj_in: DealCreate) -> Deal:
        db_obj = Deal(
            pair=obj_in.pair,
            date_open=obj_in.date_open,
            pnl=obj_in.pnl,
            bot_id=obj_in.bot_id
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

    def get_bot_last_deal(self, bot_id: int, pair: str) -> Deal:
        with SessionLocal() as session:
            return session.query(self.model).filter(self.model.bot_id == bot_id, self.model.pair == pair).order_by(
                self.model.id.desc()).first()

    def get_open_deals(self) -> List[ModelType]:
        with SessionLocal() as session:
            return session.query(self.model).filter(self.model.date_close == None).order_by(self.model.id.desc()).all()

    def increment_safety_orders_count(self, record) -> int:
        with SessionLocal() as session:
            safety_count = record.safety_order_count + 1
            record.safety_order_count = safety_count
            session.add(record)
            session.commit()

        return safety_count

    def get_pnl_sum(self, start_date: datetime = None):
        with SessionLocal() as session:
            pnl_query = session.query(func.sum(self.model.pnl))

            if start_date is None:
                result = pnl_query.scalar()
            else:
                result = pnl_query.filter(
                    self.model.date_close >= start_date).scalar()

            return result or 0


deal = CRUDDeal(Deal)
