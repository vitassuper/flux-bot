from typing import Union, Any

from src.schemas import AddSignal, OpenSignal, CloseSignal


class ErrorMessage:
    def __init__(self, signal: Union[AddSignal, OpenSignal, CloseSignal], e: Any):
        self._signal = signal
        self._e = e

    def __str__(self):
        return (
            f'Bot id: {self._signal.bot_id}\n'
            f'🚨Cant {self._signal.type_of_signal}: {str(self._e)}'
        )
