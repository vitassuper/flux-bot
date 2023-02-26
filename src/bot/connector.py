from typing import Tuple, Union
import ccxt

from datetime import datetime
from src.app.schemas.deals import DealCreate, DealUpdate
from src.app import schemas

from src.app.services.deal import create_deal, get_deal, get_opened_deals, increment_safety_orders_count, update_deal
from src.bot.exception import ConnectorException
from src.bot.notifier import Notifier
from decimal import Decimal, ROUND_DOWN
from src.bot.helper import calculate_position_pnl_for_position, get_time_duration_string

from src.core.config import settings


class Connector:
    def __init__(self):
        self.okx = ccxt.okex(
            {
                "apiKey": settings.API_KEY,
                "secret": settings.API_SECRET,
                "password": settings.API_PASSWORD,
                "options": {
                    "defaultType": "swap",
                },
            }
        )

        self.notifier = Notifier()

        self.okx.load_markets()

    def dispatch(self, signal: Union[schemas.AddSignal, schemas.OpenSignal, schemas.CloseSignal]) -> None:
        return
        try:
            match signal.type_of_signal:
                case 'open':
                    connector.dispatch_open_short_position(
                        signal.pair, signal.amount)
                case 'close':
                    connector.dispatch_close_short_position(signal.pair)
                case 'add':
                    connector.dispatch_add_to_short_position(
                        signal.pair, signal.amount)
                case _:
                    raise ConnectorException('unknown type of signal')

        except ConnectorException as e:
            self.notifier.send_warning_notification(
                f"Cant {signal.type_of_signal}: {str(e)}")
            pass

        except ccxt.BaseError as ccxt_error:
            self.notifier.send_warning_notification(str(ccxt_error))
            pass

    def get_position(self, pair: str):
        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None)

        if not open_position:
            raise ConnectorException('position not exists')

        return open_position

    def ensure_deal_not_opened(self, pair: str):
        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None)

        if open_position:
            raise ConnectorException(f"position already exists: {pair}")

    def convert_quote_to_contracts(self, symbol: str, amount: float) -> Tuple[int, float]:
        market = self.okx.market(symbol)
        price = self.okx.fetch_ticker(symbol)["last"]

        contracts_size = int(amount / price / market["contractSize"])

        if not contracts_size:
            raise ConnectorException(f"low amount for pair: {symbol}")

        contracts_cost = contracts_size * price * market["contractSize"]

        return contracts_size, contracts_cost

    def get_open_positions_info(self):
        positions = self.okx.fetch_positions()
        positions.sort(key=lambda item: item["info"]["instId"])

        deals = get_opened_deals()

        tickers = self.okx.fetch_tickers(
            [item['info']['instId'] for item in positions if 'info' in item and 'instId' in item['info']])

        result = ""
        for item in positions:
            deal = next((x for x in deals if x.pair ==
                        item["info"]["instId"]), None)

            symbol = item['symbol']

            result += (
                f"{item['info']['instId']}\n"
                f"margin: {Decimal(item['info']['margin']).quantize(Decimal('0.001'))}\n"
                f"currentPrice: {tickers[symbol]['last']}\n"
                f"avgPrice: {self.okx.price_to_precision(symbol, item['info']['avgPx'])}\n"
                f"unrealizedPnl: {Decimal(item['unrealizedPnl']).quantize(Decimal('0.0001'))} ({round(item['percentage'], 2)}%)\n"
                f"liquidationPrice: {self.okx.price_to_precision(symbol, item['liquidationPrice'])}\n"
                f"Pos size: {Decimal(item['info']['notionalUsd']).quantize(Decimal('0.001'))}💰\n"
            )

            if (deal):
                result += (
                    f"Duration: {get_time_duration_string(deal.date_open, datetime.now())}\n"
                    f"Safety orders {deal.safety_order_count}\n\n"
                )

        return result

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

        result = self.okx.fetch_order(order["id"], symbol=pair)

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
        self.okx.add_margin(symbol=pair, amount=amount,
                            params={"posSide": "short"})

    def set_leverage_for_short_position(self, pair: str, leverage: int):
        self.okx.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={"mgnMode": "isolated", "posSide": "short"},
        )

    def sell_short_position(self, pair: str, amount: int):
        self.okx.create_order(
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
        return self.okx.create_order(
            symbol=pair,
            side="buy",
            type="market",
            amount=amount,
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )


connector = Connector()
