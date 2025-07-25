from pydantic import BaseModel, Float
from models.trade import Trade

class BacktestResult(BaseModel):
    trades: list[Trade]
    ending_balance: Float
    max_drawdown: Float
    average_drawdown: Float
    percent_gain_loss: Float
