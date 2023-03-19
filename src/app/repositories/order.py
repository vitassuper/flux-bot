from src.app.models.order import Order
from src.app.repositories.base import CRUDBase
from src.app.schemas.order import OrderCreate
from src.db.session import SessionLocal


class CRUDOrder(CRUDBase[Order, OrderCreate]):
    def create(self, obj_in: OrderCreate) -> Order:
        db_obj = Order(
            deal_id=obj_in.deal_id,
            side=obj_in.side,
            price=obj_in.price,
            volume=obj_in.volume,
        )

        with SessionLocal() as session:
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

        return db_obj


order = CRUDOrder(Order)
