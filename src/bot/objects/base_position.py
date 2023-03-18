class BasePosition:
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        base_amount: str = '',
        bot_name: str = 'Test bot',
    ):
        self.bot_name = bot_name
        self.pair = pair
        self.quote_amount = quote_amount
        self.base_amount = base_amount
