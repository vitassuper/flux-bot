import asyncio
from typing import Union

from fastapi.concurrency import run_in_threadpool

from src.app import schemas
from src.bot.signal_dispatcher import SignalDispatcher


def task(signal):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    future = loop.create_task(SignalDispatcher().dispatch(signal=signal))
    loop.run_until_complete(future)


async def run(signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]):
    await run_in_threadpool(lambda: task(signal))
