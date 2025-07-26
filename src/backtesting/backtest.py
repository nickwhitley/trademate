import pandas as pd
from models.bot_config import BotConfig
from models.backtest_config import BacktestConfig
from models.backtest_result import BacktestResult

def run_backtest(
        bot_config: BotConfig, 
        backtest_config: BacktestConfig
) -> BacktestResult:
    assets = bot_config.assets
    timeframes = bot_config.timeframes
    print(assets)
    print(timeframes)
    