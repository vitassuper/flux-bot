from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from src.app import schemas
from src.bot.connector import Connector
from src.core.config import settings


async def verify_secret(request: Request):
    json_body = await request.json()

    if json_body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise HTTPException(status_code=403)
    
router = APIRouter(dependencies=[Depends(verify_secret)])

class Signal(BaseModel):
    pair: str = Field(max_length=255)
    amount: Optional[float]
    type_of_signal: str = Field(max_length=255)

@router.post("/")
async def open_signal(*, signal: Signal) -> Any:
    connector = Connector()

    if(signal.type_of_signal == 'open'):
        connector.open_short_position(signal.pair, signal.amount)

    if(signal.type_of_signal == 'close'):   
        connector.close_short_position(signal.pair)

    if(signal.type_of_signal == 'add'):
        connector.add_to_short_position(signal.pair, signal.amount)
    
    return Response(status_code=204)

# @router.post("/add")
# async def add_signal(signal: schemas.AddSignal) -> Any:
#     connector = Connector()

#     connector.add_to_short_position(signal.pair, signal.amount)

#     return Response(status_code=204)


# @router.post("/close")
# async def close_signal(signal: schemas.CloseSignal) -> Any:
#     connector = Connector()

#     connector.close_short_position(signal.pair)

#     return Response(status_code=204)
