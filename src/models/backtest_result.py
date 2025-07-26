from pydantic import BaseModel
from models.trade import Trade

class BacktestResult(BaseModel):
    trades: list[Trade]
    ending_balance: float
    max_drawdown: float
    average_drawdown: float
    percent_gain_loss: float
