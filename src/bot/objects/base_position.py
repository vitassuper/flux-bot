class BasePosition:
    def __init__(
        self,
        pair: str,
        quote_amount: str,
        base_amount: str = ''
    ):
        self.pair = pair
        self.quote_amount = quote_amount
        self.base_amount = base_amount
