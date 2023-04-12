from typing import Union

from src.app import schemas
from src.bot.signal_dispatcher import SignalDispatcher


async def run(signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]):
    await SignalDispatcher().dispatch(signal=signal)
