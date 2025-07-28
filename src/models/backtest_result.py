from pydantic import BaseModel
from models.trade import Trade

class BacktestResult(BaseModel):
    trades: list[Trade]
    ending_balance: float
    max_drawdown: float
    average_drawdown: float
    gain_loss: float
    percent_gain_loss: float


def compute_drawdowns(balance_history: list[float]) -> tuple[float, float]:
    peak = balance_history[0]
    drawdowns = []

    for balance in balance_history:
        if balance > peak:
            peak = balance
        drawdowns.append(peak - balance)

    max_dd = max(drawdowns) if drawdowns else 0
    avg_dd = sum(drawdowns) / len(drawdowns) if drawdowns else 0
    return max_dd, avg_dd