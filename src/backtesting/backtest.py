import pandas as pd
from models.bot_config import BotConfig
from models.backtest_config import BacktestConfig
from models.backtest_result import BacktestResult

def run_backtest(
        df: pd.DataFrame,
        bot_config: BotConfig, 
        backtest_config: BacktestConfig
) -> BacktestResult:
    pass