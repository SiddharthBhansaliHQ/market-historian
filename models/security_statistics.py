from datetime import date

from pydantic import BaseModel


class SecurityStatistics(BaseModel):
    start_date: date
    end_date: date
    rate_of_return: float
    annualized_log_rate_of_return: float
    annualized_log_volatility: float
    annualized_log_sharpe_ratio_rf_zero: float
