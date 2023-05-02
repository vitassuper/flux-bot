import argparse
import asyncio

from src.app.repositories.bot import create_bot
from src.bot.utils.helper import Helper


def main():
    asyncio.run(process())


async def process():
    parser = argparse.ArgumentParser(description='Create bots in DB')
    parser.add_argument('--fromId', type=int, required=True, help='start ID')
    parser.add_argument('--toId', type=int, required=True, help='end ID')
    parser.add_argument('--key', type=str, required=True, help='API key')
    parser.add_argument('--secret', type=str, required=True, help='API secret')

    args = parser.parse_args()

    for bot_id in range(args.fromId, args.toId):
        await create_bot(bot_id=bot_id, api_key=Helper.encrypt_string(args.key),
                         api_secret=Helper.encrypt_string(args.secret))

    print('Done')


if __name__ == '__main__':
    main()
