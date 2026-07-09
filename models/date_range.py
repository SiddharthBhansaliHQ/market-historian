from datetime import date

from pydantic import BaseModel, ConfigDict


class DateRange(BaseModel):
    model_config = ConfigDict(frozen=True)

    start_date: date
    end_date: date
