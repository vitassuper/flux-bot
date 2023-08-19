from typing import Union

from src.bot.signal_dispatcher import SignalDispatcher
from src.schemas import AddSignal, OpenSignal, CloseSignal


class SignalDispatcherFactory:
    @classmethod
    async def create(cls, signal: Union[AddSignal, OpenSignal, CloseSignal]):
        return await SignalDispatcher.create(signal)
