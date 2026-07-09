from datetime import date

from pydantic import BaseModel


class MarketDataUnit(BaseModel):
    reference_date: date
    adjusted_close: float
