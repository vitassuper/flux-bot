from src.app.models import Bot
from src.app.repositories import bot as repository
from src.bot.exceptions.not_found_exception import NotFoundException


async def get_bot(bot_id: int) -> Bot:
    bot = await repository.get_bot(bot_id=bot_id)

    if not bot:
        raise NotFoundException(
            'The bot with this id does not exist in the system')

    return bot
