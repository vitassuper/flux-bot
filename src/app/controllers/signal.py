import re
from typing import Union

from sanic import HTTPResponse, Request, response, exceptions

from src.app.schemas import OpenSignal, CloseSignal, AddSignal
from src.bot.singal_dispatcher_spawner import spawn_and_dispatch
from src.core.config import settings


def initialize_signal_object(data: dict) -> Union[AddSignal, OpenSignal, CloseSignal]:
    discriminator = data.get('type_of_signal')

    if discriminator == 'open':
        return OpenSignal(**data)

    if discriminator == 'add':
        return AddSignal(**data)

    if discriminator == 'close':
        return CloseSignal(**data)

    raise ValueError("Invalid discriminator value")


# TODO temp function
def remove_letters_and_convert_to_number(s):
    if s is None:
        return None

    if isinstance(s, int):
        return s

    first_letter_removed = re.sub(r'[a-zA-Z]', '', s, 1)

    return int(first_letter_removed)


async def handler(
    request: Request
) -> HTTPResponse:
    body = request.json

    if body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise exceptions.Forbidden()

    signal = initialize_signal_object(body)
    signal.position = remove_letters_and_convert_to_number(signal.position)

    spawn_and_dispatch(signal)

    return response.empty()
