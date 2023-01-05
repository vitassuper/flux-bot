import sys
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Body, Response

from src.app import schemas
from src.app.services import deal as service
from src.bot.connector import Connector
from src.core.config import settings


async def verify_secret(request: Request):
    json_body = await request.json()

    if json_body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise HTTPException(status_code=403)
    
router = APIRouter(dependencies=[Depends(verify_secret)])

@router.post("/open")
def open_signal(*, signal: schemas.OpenSignal) -> Any:
    connector = Connector()

    connector.open_short_position(signal.pair, signal.amount)

    return Response(status_code=204)

@router.post("/add")
def add_signal(signal: schemas.AddSignal) -> Any:
    connector = Connector()

    connector.add_to_short_position(signal.pair, signal.amount)

    return Response(status_code=204)


@router.post("/close")
def close_signal(signal: schemas.CloseSignal) -> Any:
    connector = Connector()

    connector.close_short_position(signal.pair)

    return Response(status_code=204)
