from pydantic import BaseModel


class MarketDataUnit(BaseModel):
    adjusted_close: float
