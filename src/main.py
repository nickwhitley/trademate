from loguru import logger
from data import data
from constants import Asset, Timeframe
from indicators.bollinger_bands import BollingerBands
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
    bb_indicator = BollingerBands()
    entry_condition_rsi = TradeCondition(
        indicator=rsi_indicator,
        condition=Condition(operator=ConditionOperator.less_than, value=30),
    )
    entry_condition_ma = TradeCondition(
        indicator=ma_indicator,
        condition=Condition(operator=ConditionOperator.above_price)
    )
    entry_condition_bb = TradeCondition(
        indicator=bb_indicator,
        condition=Condition(operator=ConditionOperator.open_above_hband)
    )
    exit_condition = TradeCondition(
        indicator=rsi_indicator,
        condition=Condition(operator=ConditionOperator.greater_than, value=60),
    )
    bot_config = BotConfig(
        bot_name="ada_testing",
        assets=[Asset.ADA_USD, Asset.BNB_USD, Asset.BTC_USD, Asset.SOL_USD, Asset.XRP_USD],
        timeframe=Timeframe.H1,
        entry_conditions=[entry_condition_rsi,entry_condition_ma,],
        exit_conditions=[exit_condition],
        order_size_usd=100.0
    )
    backtest_config = BacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime.now(),
        starting_balance=10000.00,
    )
    result = run_backtest(bot_config=bot_config, backtest_config=backtest_config)
    print(len(result.trades))


if __name__ == "__main__":
    main()
