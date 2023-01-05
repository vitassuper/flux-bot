from pydantic import BaseModel, Field

class OpenSignal(BaseModel):
    pair: str = Field(max_length=255)
    amount: float

class AddSignal(OpenSignal):
    pass

class CloseSignal(BaseModel):
    pair: str = Field(max_length=255)
