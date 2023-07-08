import abc
from typing import List

from ccxt.base.decimal_to_precision import TRUNCATE

from src.bot.services.deal import get_opened_deals
from src.bot.objects.messages.active_deal_message import ActiveDealMessage


class BaseExchange(metaclass=abc.ABCMeta):
    def __init__(self, exchange) -> None:
        self.exchange = exchange

    async def __aenter__(self):
        return self.exchange

    async def __aexit__(self, exc_type, exc, tb):
        await self.exchange.close()

    @abc.abstractmethod
    async def fetch_opened_positions(self):
        pass

    @abc.abstractmethod
    def get_exchange_name(self):
        pass

    async def get_open_positions_info(self) -> List[ActiveDealMessage]:
        deals = await get_opened_deals()

        exchange_positions = await self.fetch_opened_positions()

        async with self as exchange:
            tickers = await exchange.fetch_tickers(
                [item['symbol'] for item in exchange_positions])

            positions = []

            for item in exchange_positions:
                symbol = item['symbol']

                deal = next((x for x in deals if x.pair ==
                             symbol), None)

                liquidation_price = self.exchange.price_to_precision(
                    symbol, item['liquidationPrice']) if item['liquidationPrice'] else None

                positions.append(
                    ActiveDealMessage(
                        pair=item['symbol'],
                        margin=self.exchange.decimal_to_precision(
                            item['initialMargin'], TRUNCATE, 4),
                        avg_price=self.exchange.price_to_precision(
                            symbol, item['entryPrice']),
                        current_price=self.exchange.price_to_precision(
                            symbol, tickers[symbol]['last']),
                        liquidation_price=liquidation_price,
                        unrealized_pnl=self.exchange.decimal_to_precision(
                            item['unrealizedPnl'], TRUNCATE, 4) + f" ({round(item['percentage'], 2)}%)",
                        notional_size=self.exchange.decimal_to_precision(
                            item['notional'], TRUNCATE, 3),
                        deal=deal,
                        side=item['side']
                    ))

            return positions
