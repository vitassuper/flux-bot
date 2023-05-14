from typing import Union

from src.app import schemas
from importlib import import_module


class SignalDispatcherFactory:
    def create(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]):
        signal_dispatcher_module = import_module("src.bot.signal_dispatcher")

        return signal_dispatcher_module.SignalDispatcher(signal)

