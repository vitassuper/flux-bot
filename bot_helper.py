import argparse
import asyncio

from src.bot.utils.helper import Helper


def main():
    asyncio.run(process())


async def process():
    parser = argparse.ArgumentParser(description='Create bots in DB')
    parser.add_argument('--key', type=str, required=True, help='API key')
    parser.add_argument('--secret', type=str, required=True, help='API secret')

    args = parser.parse_args()

    print(Helper.encrypt_string(args.key))
    print(Helper.encrypt_string(args.secret))

    print('Done')


if __name__ == '__main__':
    main()
