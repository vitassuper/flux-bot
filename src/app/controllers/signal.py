from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Body, BackgroundTasks

from src.app import schemas
from src.bot.connector import run
from src.core.config import settings


async def verify_secret(request: Request):
    json_body = await request.json()

    if json_body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise HTTPException(status_code=403)

router = APIRouter(dependencies=[Depends(verify_secret)])


@router.post('')
async def open_signal(*, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal] = Body(..., discriminator='type_of_signal'), background_tasks: BackgroundTasks) -> Any:
    background_tasks.add_task(run, signal)

    return Response(status_code=204)
