from typing import Any

from fastapi import APIRouter

from src.app import schemas
from src.app.services import deals as service


router = APIRouter()


@router.post("/")
def create_deal(*, deal_in: schemas.DealCreate) -> Any:
    """
    Create new deal
    """
    return service.create_deal(deal_in)


@router.get("/{deal_id}")
def get_deal_by_id(deal_id: int) -> Any:
    """
    Get a specific deal by id.
    """
    return service.get_deal(deal_id)


@router.patch("/{deal_id}")
def update_deal(deal_id: int, deal_in: schemas.DealUpdate) -> Any:
    """
    Update a deal
    """
    return service.update_deal(deal_id, deal_in)
