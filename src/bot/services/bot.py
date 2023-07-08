from typing import List

from src.bot.models import Bot
from src.bot.repositories import bot as repository
from src.bot.exceptions.not_found_exception import NotFoundException


async def get_bot(bot_id: int) -> Bot:
    bot = await repository.get_bot(bot_id=bot_id)

    if not bot:
        raise NotFoundException(
            'The bot with this id does not exist in the system')

    return bot


async def get_copy_bots(bot_id: int) -> List[Bot]:
    return await repository.get_copy_bots(bot_id=bot_id)
