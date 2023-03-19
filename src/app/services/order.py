from src.app.models.order import Order
from src.app.schemas.order import OrderBase, OrderCreate
from src.app.repositories.order import order as repository


def create_order(order: OrderCreate) -> Order:
    return repository.create(obj_in=order)
