from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Body

from src.app import schemas
from src.bot.connector import connector
from src.core.config import settings

async def verify_secret(request: Request):
    json_body = await request.json()

    if json_body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise HTTPException(status_code=403)
    
router = APIRouter(dependencies=[Depends(verify_secret)])

@router.post("")
async def open_signal(*, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal] = Body(..., discriminator='type_of_signal')) -> Any:
    if(signal.type_of_signal == 'open'):
        connector.open_short_position(signal.pair, signal.amount)

    if(signal.type_of_signal == 'close'):   
        connector.close_short_position(signal.pair)

    if(signal.type_of_signal == 'add'):
        connector.add_to_short_position(signal.pair, signal.amount)
    
    return Response(status_code=204)
