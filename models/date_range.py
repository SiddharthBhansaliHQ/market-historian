from datetime import date

from pydantic import BaseModel


class DateRange(BaseModel):
    start_date: date
    end_date: date
