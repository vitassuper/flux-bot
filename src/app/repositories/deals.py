from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from src.app.repositories.base import CRUDBase
from src.app.models.deals import Deal
from src.app.schemas.deals import DealCreate, DealUpdate


class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    def create(self, db: Session, *, obj_in: DealCreate) -> Deal:
        db_obj = Deal(
            pair=obj_in.pair,
            exchangeId=obj_in.pair,
            safety_order_count=obj_in.safety_order_count,
            date_open=obj_in.date_open,
            pnl=obj_in.pnl
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Deal, obj_in: Union[DealUpdate, Dict[str, Any]]) -> Deal:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


deal = CRUDDeal(Deal)
