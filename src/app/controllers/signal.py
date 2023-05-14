from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Body

from src.app.schemas import OpenSignal, CloseSignal, AddSignal
from src.bot.singal_dispatcher_spawner import spawn_and_dispatch
from src.core.config import settings


async def verify_secret(request: Request):
    json_body = await request.json()

    if json_body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise HTTPException(status_code=403)


router = APIRouter(dependencies=[Depends(verify_secret)])


@router.post('')
async def open_signal(
    *,
    signal: Union[AddSignal, OpenSignal, CloseSignal] = Body(..., discriminator='type_of_signal')
) -> Any:
    spawn_and_dispatch(signal)

    return Response(status_code=204)
