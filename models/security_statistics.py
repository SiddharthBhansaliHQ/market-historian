from datetime import date

from pydantic import BaseModel


class SecurityStatistics(BaseModel):
    start_date: date
    end_date: date
    rate_of_return: float
