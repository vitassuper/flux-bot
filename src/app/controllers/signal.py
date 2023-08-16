import json
import re
from typing import Union

from sanic import HTTPResponse, Request, response, exceptions, SanicException

from src.bot.singal_dispatcher_spawner import spawn_and_dispatch
from src.core.config import settings
from src.schemas import AddSignal, OpenSignal, CloseSignal


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


def parse_json(raw_body: bytes):
    raw_body = raw_body.decode('utf-8')

    try:
        return json.loads(raw_body)

    except json.JSONDecodeError as e:
        error_pos = e.pos
        error_location = max(0, error_pos - 20)

        raise SanicException(f"...{raw_body[error_location:error_pos + 20]}...", status_code=500)


async def handler(
    request: Request
) -> HTTPResponse:
    body = parse_json(request.body)

    if body.get('connector_secret') != settings.CONNECTOR_SECRET:
        raise exceptions.Forbidden()

    signal = initialize_signal_object(body)
    signal.position = remove_letters_and_convert_to_number(signal.position)

    spawn_and_dispatch(signal)

    return response.empty()
