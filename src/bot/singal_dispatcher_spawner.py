import asyncio
import json
import re
import traceback
from threading import Thread
from typing import Union

from src.bot.exceptions import SecretException, ConnectorException
from src.bot.exceptions.base_exception import BaseConnectorException
from src.bot.exceptions.disabled_exception import DisabledException
from src.bot.exceptions.json_decode_exception import JsonDecodeException
from src.bot.exchange.notifiers.telegram_notifier import TelegramNotifier
from src.bot.objects.messages.error_message import ErrorMessage
from src.bot.objects.messages.signal_message import SignalMessage
from src.bot.objects.messages.warning_message import WarningMessage
from src.bot.signal_dispatcher import SignalDispatcher
from src.core.config import settings
from src.db.session import DB
from src.schemas import AddSignal, OpenSignal, CloseSignal


async def run(signal_plain_text: bytes):
    notifier = TelegramNotifier()
    # init DB
    db = DB()

    try:
        signal = await parse_signal_from_text(signal_plain_text)
        dispatcher = await SignalDispatcher.create(signal)

        notifier.add_message_to_stack(
            str(
                SignalMessage(
                    signal=signal, bot=dispatcher.bot, exchange=dispatcher.exchange
                )
            )
        )

        notifier.add_message_to_stack(str(await dispatcher.dispatch()))

    except DisabledException as e:
        notifier.add_message_to_stack(str(WarningMessage(str(e))))

    except ConnectorException as e:
        notifier.add_message_to_stack(str(ErrorMessage(str(e))))
        traceback.print_tb(e.__traceback__)

    except BaseConnectorException as e:
        notifier.add_message_to_stack(str(ErrorMessage(str(e))))

    finally:
        # close DB connection
        await db.close()

        await notifier.send_message()


async def parse_signal_from_text(
    json_text: bytes,
) -> Union[AddSignal, OpenSignal, CloseSignal]:
    try:
        json_text = json_text.decode("utf-8")
        signal_json = json.loads(json_text)

    except json.JSONDecodeError:
        raise JsonDecodeException(json_text)

    if signal_json.get("connector_secret") != settings.CONNECTOR_SECRET:
        raise SecretException()

    signal = initialize_signal_object(signal_json)
    signal.position = remove_letters_and_convert_to_number(signal.position)

    return signal


def initialize_signal_object(
    data: dict,
) -> Union[AddSignal, OpenSignal, CloseSignal]:
    discriminator = data.get("type_of_signal")

    if discriminator == "open":
        return OpenSignal(**data)

    if discriminator == "add":
        return AddSignal(**data)

    if discriminator == "close":
        return CloseSignal(**data)

    raise ValueError("Invalid discriminator value")


# TODO temp function
def remove_letters_and_convert_to_number(s):
    if s is None:
        return None

    if isinstance(s, int):
        return s

    first_letter_removed = re.sub(r"[a-zA-Z]", "", s, 1)

    return int(first_letter_removed)


def thread_run(signal_plain_text: bytes):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(signal_plain_text))
    loop.close()


def spawn_and_dispatch(signal_plain_text: bytes):
    thread = Thread(target=thread_run, args=[signal_plain_text])
    thread.start()
