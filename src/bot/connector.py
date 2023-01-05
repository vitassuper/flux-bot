import ccxt

from datetime import datetime
from src.app.schemas.deals import DealCreate, DealUpdate

from src.app.services.deal import create_deal, get_deal_by_exchange_id, get_opened_deals, increment_safety_orders_count, update_deal_by_exchange_id
from src.bot.notificator import Notificator
from decimal import Decimal, ROUND_DOWN

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

        self.notificator = Notificator()

        self.okx.load_markets()

    def db_add_new_deal(self, pair, posId, date_open):
        create_deal(DealCreate(pair=pair, exchange_id=posId, date_open=date_open))


    def convert_quote_to_contracts(self, symbol, amount):
        market = self.okx.market(symbol)
        price = self.okx.fetch_ticker(symbol)["last"]

        contractsSize = int(amount / price / market["contractSize"])

        contractsCost = contractsSize * price * market["contractSize"]

        return contractsSize, contractsCost

    def findElement(self, items, function):
        for item in items:
            if function(item):
                return item

    def get_open_positions(self):
        positions = self.okx.fetch_positions()
        positions.sort(key=lambda item: item["info"]["instId"])

        deals = get_opened_deals()

        result = ""
        for item in positions:
            deal = self.findElement(
                deals, (lambda deal: deal.pair == item["info"]["instId"])
            )

            result += (
                f"{item['info']['instId']}\n"
                f"margin: {Decimal(item['info']['margin']).quantize(Decimal('0.001'))}\n"
                f"entryPrice: {item['entryPrice']}\n"
                f"avgPrice: {item['info']['avgPx']}\n"
                f"unrealizedPnl: {Decimal(item['unrealizedPnl']).quantize(Decimal('0.0001'))} ({round(item['percentage'], 2)}%)\n"
                f"liquidationPrice: {item['liquidationPrice']}\n"
                f"Pos size: {Decimal(item['info']['notionalUsd']).quantize(Decimal('0.001'))}💰\n"
                f"Duration: {self.get_time_duration(deal.date_open, datetime.now()) if deal else 'Unknown info'}\n"
                f"Safety orders {deal.safety_order_count if deal else 'Unknown info'}\n\n"
            )

        return result

    def open_short_position(self, pair, amount, leverage=20):
        self.notificator.send_notification(
            f"Received open signal: pair: {pair}, amount: {amount}"
        )

        quantity, contractsCost = self.convert_quote_to_contracts(pair, amount)

        if quantity == 0:
            self.notificator.send_warning_notification(
                f"Can't open new position, low amount for pair: {pair}"
            )

            return

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None
        )

        if open_position:
            self.notificator.send_warning_notification(
                f"Can't open new position, position already exists pair: {pair}"
            )

            return

        self.okx.set_leverage(
            leverage=leverage,
            symbol=pair,
            params={"mgnMode": "isolated", "posSide": "short"},
        )

        order = self.okx.create_order(
            symbol=pair,
            side="sell",
            type="market",
            amount=quantity,
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None
        )

        self.db_add_new_deal(
            pair, open_position["info"]["posId"], datetime.now().timestamp()
        )

        self.okx.add_margin(symbol=pair, amount=contractsCost * 0.02, params={"posSide": "short"})

    def add_to_short_position(self, pair, amount):
        self.notificator.send_notification(
            f"Received signal type: add, pair: {pair}, amount: {amount}"
        )

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None
        )

        if not open_position:
            self.notificator.send_warning_notification(
                f"Can't average position, position not exists pair: {pair}"
            )

            return

        quantity, contractsCost = self.convert_quote_to_contracts(pair, amount)

        if quantity == 0:
            self.notificator.send_warning_notification(
                f"Can't average position, low amount for pair: {pair}"
            )

            return

        order = self.okx.create_order(
            symbol=pair,
            side="sell",
            type="market",
            amount=quantity,
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )

        self.okx.add_margin(symbol=pair, amount=contractsCost * 0.02, params={"posSide": "short"})

        deal = increment_safety_orders_count(open_position["info"]["posId"])

        self.notificator.send_notification(
            f"Averaged position ({deal.safety_order_count})"
        )

    def close_short_position(self, pair):
        self.notificator.send_notification(f"Received signal type: close, pair: {pair}")

        positions = self.okx.fetch_positions()

        open_position = next(
            (p for p in positions if p["info"]["instId"] == pair), None
        )

        if not open_position:
            self.notificator.send_warning_notification(
                f"Can't close position, position not exists pair: {pair}"
            )

            return

        order = self.okx.create_order(
            symbol=pair,
            side="buy",
            type="market",
            amount=int(open_position["contracts"]),
            params={
                "posSide": "short",
                "tdMode": "isolated",
            },
        )

        result = self.okx.fetch_order(order["id"], symbol=pair)

        deal = get_deal_by_exchange_id(open_position["info"]["posId"])

        update_deal_by_exchange_id(open_position["info"]["posId"], DealUpdate(pnl=result["info"]["pnl"], date_close=result["timestamp"]/1000))

        pnl = Decimal(result["info"]["pnl"]).quantize(
            Decimal("0.0001"), rounding=ROUND_DOWN
        )

        pnl_percentage = self.calculate_pnl_percentage(
            result["price"], open_position["entryPrice"], float(result["info"]["lever"]), result["info"]["posSide"]
        )

        duration = self.get_time_duration(
            datetime.fromtimestamp(deal.date_open), datetime.fromtimestamp(result["timestamp"] / 1000)
        )

        self.notificator.send_notification(
            (
                f"{result['symbol']}\n"
                f"Profit:{pnl}$ ({pnl_percentage}%)\n"
                f"Size: {result['info']['fillSz']}\n"
                f"Duration: {duration}"
            )
        )

    def get_time_duration(self, date_open, date_close):
        diff = date_close - date_open
        seconds_duration = diff.total_seconds()

        days, seconds = divmod(seconds_duration, 86400)
        hours, seconds = divmod(seconds_duration, 3600)
        minutes, seconds = divmod(seconds_duration, 60)

        hours, minutes = divmod(minutes, 60)

        return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

    def calculate_pnl_percentage(self, closePrice, avgPrice, leverage, posSide):
        sign = 1

        if posSide == "short":
            sign = -1

        return Decimal(
            ((closePrice - avgPrice) / avgPrice) * float(leverage) * 100 * sign
        ).quantize(Decimal("0.01"))
