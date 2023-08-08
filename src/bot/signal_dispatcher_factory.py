from importlib import import_module
from typing import Union

from src.schemas import AddSignal, OpenSignal, CloseSignal


class SignalDispatcherFactory:
    @classmethod
    async def create(cls, signal: Union[AddSignal, OpenSignal, CloseSignal]):
        signal_dispatcher_module = import_module("src.bot.signal_dispatcher")

        return await signal_dispatcher_module.SignalDispatcher.create(signal)
