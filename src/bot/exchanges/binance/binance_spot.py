import ccxt
from src.db.services import get_deal, get_orders
from src.bot.exception import ConnectorException
from src.bot.exchanges.spot_base import SpotBaseExchange
from src.config import settings


class BinanceSpot(SpotBaseExchange):
    def get_exchange_name(self):
        return "Binance"

    def __init__(self, bot_id: int) -> None:
        exchange = ccxt.binance(
            {
                "apiKey": settings.API_KEY_BINANCE,
                "secret": settings.API_SECRET_BINANCE,
                "options": {
                    "defaultType": "spot",
                },
                "enableRateLimit": True,
            }
        )

        exchange.set_sandbox_mode(True)

        super().__init__(bot_id=bot_id, exchange=exchange)

    def market_sell(self, pair: str, amount: int):
        return self.exchange.create_order(
            symbol=pair, type="market", side="sell", amount=amount
        )

    def market_buy(self, pair: str, amount: int):
        return self.exchange.create_order(
            symbol=pair, type="market", side="buy", amount=amount
        )

    def get_base_amount(self, pair: str, quote_amount: float):
        market = self.exchange.market(pair)
        price = self.exchange.fetch_ticker(pair)["last"]

        min_notional_filter = next(
            filter(
                lambda x: x["filterType"] == "MIN_NOTIONAL", market["info"]["filters"]
            )
        )

        min_notional = float(min_notional_filter["minNotional"])
        minimal_quote_amount = market["limits"]["amount"]["min"] * price

        minimal_amount = max(minimal_quote_amount, min_notional)

        if quote_amount < minimal_amount:
            raise ConnectorException(
                f"low amount for pair {pair} - min amount: {minimal_amount}"
            )

        return self.exchange.amount_to_precision(pair, amount=quote_amount / price)

    def test(self, pair: str, amount: float):
        pair = self.guess_symbol_from_tv(symbol=pair)

        # base_amount = self.get_base_amount(pair=pair, quote_amount=amount)

        order = self.market_buy(pair=pair, amount=0.001)

        avg_price = quote_amount = order["amount"] * order["average"]

        # deal = get_deal(bot_id=self.bot_id, pair=pair)
        deal = get_deal(bot_id=4, pair="ICP")

        orders = get_orders(deal.id)

        print(orders)

        # update_deal(bot_id=self.bot_id, pair=pair, obj_in=DealUpdate(avg_price=deal.avg_price + avg_price))

        # create_deal(DealCreate(bot_id=self.bot_id, avg_price=avg_price,
        #             pair=order['symbol'], date_open=datetime.now()))

        # create_deal(DealCreate(bot_id=self.bot_id,
        #             pair=pair, date_open=datetime.now()))

        # print(base_amount)
