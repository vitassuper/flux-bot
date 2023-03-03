from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from typing import Tuple
import ccxt
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app.services.deal import create_deal, get_deal, get_opened_deals, increment_safety_orders_count, update_deal
from src.bot.exception import ConnectorException
from src.bot.exchange.base import BaseExchange
from src.bot.helper import calculate_position_pnl_for_position, get_time_duration_string
from src.bot.position import Position
from src.core.config import settings
from ccxt.base.decimal_to_precision import TRUNCATE


class Okex(BaseExchange):

    def get_exchange_name(self):
        return 'OKEX'

    def __init__(self) -> None:
        super().__init__()

        self.exchange = ccxt.okex({
            "apiKey": settings.API_KEY,
            "secret": settings.API_SECRET,
            "password": settings.API_PASSWORD,
            "options": {
                "defaultType": "swap",
            },
        })

        self.exchange.load_markets()

    def get_position(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def ensure_deal_not_opened(self, pair: str):
        positions = self.exchange.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def convert_quote_to_contracts(self, symbol: str, amount: float) -> Tuple[int, float]:
        market = self.exchange.market(symbol)
        price = self.exchange.fetch_ticker(symbol)["last"]

        contracts_size = int(amount / price / market["contractSize"])

        if not contracts_size:
            raise ConnectorException(f"low amount for pair: {symbol}")

        contracts_cost = contracts_size * price * market["contractSize"]

        return contracts_size, contracts_cost

    def get_open_positions_info(self):
        exchange_positions = self.exchange.fetch_positions()
        exchange_positions.sort(key=lambda item: item["info"]["instId"])

        deals = get_opened_deals()

        tickers = self.exchange.fetch_tickers(
            [item['info']['instId'] for item in exchange_positions if 'info' in item and 'instId' in item['info']])

        positions = []

        for item in exchange_positions:
            deal = next((x for x in deals if x.pair ==
                        item["info"]["instId"]), None)

            symbol = item['symbol']

            positions.append(
                Position(
                    ticker=item['info']['instId'],
                    margin=self.exchange.decimal_to_precision(
                        item['info']['margin'], TRUNCATE, 4),
                    avg_price=self.exchange.price_to_precision(
                        symbol, item['info']['avgPx']),
                    current_price=self.exchange.price_to_precision(
                        symbol, tickers[symbol]['last']),
                    liquidation_price=self.exchange.price_to_precision(
                        symbol, item['liquidationPrice']),
                    unrealized_pnl=self.exchange.decimal_to_precision(
                        item['unrealizedPnl'], TRUNCATE, 4) + f" ({round(item['percentage'], 2)}%)",
                    notional_size=self.exchange.decimal_to_precision(
                        item['info']['notionalUsd'], TRUNCATE, 3),
                    deal=deal
                ))

        return positions

    def dispatch_open_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received open signal: pair: {pair}, amount: {amount}")

        self.ensure_deal_not_opened(pair)

        quantity, contracts_cost = self.convert_quote_to_contracts(
            pair, amount)

        self.set_leverage_for_short_position(pair, 20)

        self.sell_short_position(pair, quantity)

        self.add_margin_to_short_position(pair, contracts_cost * 0.06)

        open_position = self.get_position(pair)

        create_deal(DealCreate(
            pair=pair, exchange_id=open_position["info"]["posId"], date_open=datetime.now()))

        self.notifier.send_notification(
            f"Opened position: {pair}, amount: {amount}")

    def dispatch_add_to_short_position(self, pair: str, amount: float):
        self.notifier.send_notification(
            f"Received signal type: add, pair: {pair}, amount: {amount}")

        open_position = self.get_position(pair)

        quantity, contracts_cost = self.convert_quote_to_contracts(
            pair, amount)

        self.sell_short_position(pair, quantity)

        self.add_margin_to_short_position(pair, contracts_cost * 0.06)

        safety_count = increment_safety_orders_count(
            open_position["info"]["posId"])

        self.notifier.send_notification(
            f"Averaged position, pair: {pair}, amount: {amount} safety orders: {safety_count}")

    def dispatch_close_short_position(self, pair: str):
        self.notifier.send_notification(
            f"Received signal type: close, pair: {pair}")

        open_position = self.get_position(pair)

        order = self.buy_short_position(pair, open_position["contracts"])

        result = self.exchange.fetch_order(order["id"], symbol=pair)

        deal = get_deal(open_position["info"]["posId"])

        update_deal(open_position["info"]["posId"], DealUpdate(
            pnl=result["info"]["pnl"], date_close=datetime.fromtimestamp(result["timestamp"]/1000)))

        pnl = Decimal(result["info"]["pnl"]).quantize(
            Decimal("0.0001"), rounding=ROUND_DOWN
        )

        pnl_percentage = calculate_position_pnl_for_position(
            result["price"], open_position["entryPrice"], float(
                result["info"]["lever"]), result["info"]["posSide"]
        )

        duration = get_time_duration_string(
            deal.date_open, datetime.fromtimestamp(result["timestamp"] / 1000))

        self.notifier.send_notification((
            f"{result['symbol']}\n"
            f"Profit:{pnl}$ ({pnl_percentage}%)\n"
            f"Size: {result['info']['fillSz']}\n"
            f"Duration: {duration}\n"
            f"Safery orders: {deal.safety_order_count}"
        ))

    def add_margin_to_short_position(self, pair: str, amount: float):
        self.exchange.add_margin(symbol=pair, amount=amount,
                                 params={"posSide": "short"})

    def set_leverage_for_short_position(self, pair: str, leverage: int):
        self.exchange.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={"mgnMode": "isolated", "posSide": "short"},
        )

    def sell_short_position(self, pair: str, amount: int):
        self.exchange.create_order(
            symbol=pair,
            side="sell",
            type="market",
            amount=amount,
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )

    def buy_short_position(self, pair: str, amount: int):
        return self.exchange.create_order(
            symbol=pair,
            side="buy",
            type="market",
            amount=amount,
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )
