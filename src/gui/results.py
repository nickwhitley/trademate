from nicegui import ui
from models.backtest_result import BacktestResult
from models.backtest_config import BacktestConfig
from datetime import datetime, timedelta
from typing import Optional
from models.bot_config import BotConfig, Asset, Timeframe
from models.condition_operator import ConditionOperator
from models.indicator import Indicator
from models.trade_condition import TradeCondition
from models.trade import Trade
from models.trade_condition import Condition
import pandas as pd
from gui.shared_state import backtest_result_data


class FakeIndicator(Indicator):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            allowed_conditions=[
                ConditionOperator.greater_than,
                ConditionOperator.less_than,
                ConditionOperator.price_crossed_below,  # ✅ Add this
            ],
            output_column=f"{name.lower()}_val"
)

    def apply_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # Dummy implementation just to satisfy the abstract method
        df[self.output_column] = 50  # or some static/fake value
        return df

    def evaluate_condition(self, condition: Condition, df: pd.DataFrame, index: int) -> bool:
        # Dummy logic: always return True
        return True

TradeCondition(
    indicator=FakeIndicator('RSI'),
    condition=Condition(operator=ConditionOperator.greater_than)
)

# Fake assets
fake_assets = [Asset.BTC_USD, Asset.ETH_USD]

fake_entry_conditions = [
    TradeCondition(
        indicator=FakeIndicator('RSI'),
        condition=Condition(operator=ConditionOperator.greater_than)
    )
]

fake_exit_conditions = [
    TradeCondition(
        indicator=FakeIndicator('Simple MA'),
        condition=Condition(operator=ConditionOperator.price_crossed_below)
    )
]

# Fake trades
fake_trades = [
    Trade(
        asset=Asset.BTC_USD,
        entry_datetime=datetime.now() - timedelta(days=2),
        entry_price=10000.0,
        close_datetime=datetime.now() - timedelta(days=1),
        close_price=10500.0,
        quantity=0.5,
        profit_loss=250.0
    ),
    Trade(
        asset=Asset.BTC_USD,
        entry_datetime=datetime.now() - timedelta(days=1),
        entry_price=10500.0,
        close_datetime=datetime.now(),
        close_price=10300.0,
        quantity=0.5,
        profit_loss=-100.0
    )
]

# Fake config and result
fake_bot_config = BotConfig(
    bot_name='TestBot X',
    assets=fake_assets,
    timeframe=Timeframe.H1,
    entry_conditions=fake_entry_conditions,
    exit_conditions=fake_exit_conditions,
    # order_size_usd=500.0         ❌ remove this
    risk_percent_per_trade=2.5  # ✅ Only this one
)

fake_backtest_result = BacktestResult(
    trades=fake_trades,
    ending_balance=11500.0,
    max_drawdown=600.0,
    average_drawdown=300.0,
    gain_loss=1500.0,
    percent_gain_loss=15.0
)

fake_backtest_config = BacktestConfig(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    starting_balance=10000.0
)

def show_results(config: BotConfig, result: BacktestResult):
    ui.label("📊 Backtest Results").classes('text-2xl font-bold mb-4')
    ui.link("🔙 Go to Main Page", '/').classes('mb-4')

    with ui.card().classes('w-full'):
        ui.label(f'🔧 Bot Name: {config.bot_name}').classes('text-lg font-bold')
        ui.label(f'🕒 Timeframe: {config.timeframe}')
        ui.label(f'💰 Assets: {", ".join(asset.value for asset in config.assets)}')
        if config.order_size_usd:
            ui.label(f'📦 Order Size (USD): ${config.order_size_usd:,.2f}')
        if config.risk_percent_per_trade:
            ui.label(f'⚠️ Risk per Trade: {config.risk_percent_per_trade:.2f}%')

    stats = {
        'Ending Balance': f"${result.ending_balance:,.2f}",
        'Max Drawdown': f"%{result.max_drawdown:,.2f}",
        'Average Drawdown': f"%{result.average_drawdown:,.2f}",
        'Gain/Loss': f"${result.gain_loss:,.2f}",
        'Percent Gain/Loss': f"%{result.percent_gain_loss:.2f}%",
        'Number of Trades': len(result.trades),
    }

    with ui.row().classes('flex-wrap justify-between gap-4 mt-4'):
        for label, value in stats.items():
            with ui.card().classes('w-[30%] min-w-[200px]'):
                ui.label(label).classes('font-medium')
                ui.label(str(value)).classes('text-xl font-bold')



@ui.page('/results')
def results_func():
    show_results(fake_bot_config, fake_backtest_result)

  # for production
@ui.page('/results-dynamic')
def results_dynamic():
    config = backtest_result_data.get('config')
    result = backtest_result_data.get('result')

    if not config or not result:
        ui.label("⚠️ No results found. Please run a backtest first.")
        ui.link("Back to Main", '/')
        return

    show_results(config, result)

