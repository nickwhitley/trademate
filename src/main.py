from loguru import logger
from data import data
from constants import Asset, Timeframe
from indicators.simple_ma import MA
from models.trade_condition import TradeCondition
from models.indicator import Indicator
from models.condition_operator import Condition
from models.condition_operator import ConditionOperator
from indicators.rsi import RSI
from models.bot_config import BotConfig
from backtesting.backtest import run_backtest
from models.backtest_config import BacktestConfig
from datetime import datetime


@logger.catch
def main():
    rsi_indicator = RSI()
    ma_indicator = MA()
    entry_condition_rsi = TradeCondition(
        indicator=rsi_indicator,
        condition=Condition(operator=ConditionOperator.less_than, value=30),
    )
    entry_condition_ma = TradeCondition(
        indicator=ma_indicator,
        condition=Condition(operator=ConditionOperator.above_price)
    )
    exit_condition = TradeCondition(
        indicator=rsi_indicator,
        condition=Condition(operator=ConditionOperator.greater_than, value=60),
    )
    bot_config = BotConfig(
        assets=[Asset.ADA_USD],
        timeframe=Timeframe.H1,
        entry_conditions=[entry_condition_rsi,entry_condition_ma],
        exit_conditions=[exit_condition],
    )
    backtest_config = BacktestConfig(
        start_date=datetime(2020, 1, 1),
        end_date=datetime.now(),
        starting_balance=100.00,
    )
    result = run_backtest(bot_config=bot_config, backtest_config=backtest_config)
    print(len(result.trades))


if __name__ == "__main__":
    main()
