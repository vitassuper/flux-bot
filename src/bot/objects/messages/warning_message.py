class WarningMessage:
    def __init__(self, text: str):
        self._text = text

    def __str__(self):
        return f"⚠️{self._text}"
