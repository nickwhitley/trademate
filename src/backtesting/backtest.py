import csv
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Union
import pandas as pd
from models.bot_config import BotConfig
from models.backtest_config import BacktestConfig
from models.backtest_result import BacktestResult
from models.trade import Trade
from data import data
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
# from backtesting.export import export_results_to_excel


def run_backtest(
    bot_config: BotConfig, backtest_config: BacktestConfig
) -> BacktestResult:
    assets = bot_config.assets
    timeframe = bot_config.timeframe
    balance = backtest_config.starting_balance
    total_profit_loss = 0.0
    trades = []
    in_trade = False
    current_trade = {
        "entry_price": float,
        "entry_date": datetime,
        "close_price": float,
        "close_date": datetime,
        "quantity": float
    }

    for asset in assets:
        df = data.get_df(asset, timeframe)
        df = df.loc[
            (df["timestamp"] >= backtest_config.start_date)
            & (df["timestamp"] <= backtest_config.end_date)
        ]

        for condition in chain(bot_config.entry_conditions, bot_config.exit_conditions):
            df = condition.indicator.apply_to_df(df)
        print(df)
        for index, row in enumerate(df.itertuples(), 0):
            if in_trade:
                all_exit_conditions_met = all(
                    cond.is_satisfied(df, index) for cond in bot_config.exit_conditions
                )
                if all_exit_conditions_met:
                    in_trade = False
                    current_trade["close_date"] = row.timestamp
                    current_trade["close_price"] = row.open
                    profit_loss = (current_trade['close_price'] * current_trade['quantity']) - (current_trade['entry_price'] * current_trade['quantity'])
                    total_profit_loss += profit_loss
                    balance += profit_loss

                    trade = Trade(
                        asset=asset,
                        entry_datetime=current_trade["entry_date"],
                        entry_price=current_trade["entry_price"],
                        close_datetime=current_trade["close_date"],
                        close_price=current_trade["close_price"],
                        quantity=current_trade["quantity"],
                        profit_loss=profit_loss
                    )
                    trades.append(trade)
                    current_trade.clear()
            else:
                all_entry_conditions_met = all(
                    cond.is_satisfied(df, index) for cond in bot_config.entry_conditions
                )
                if all_entry_conditions_met:
                    in_trade = True
                    current_trade["entry_date"] = row.timestamp
                    current_trade["entry_price"] = row.open
                    current_trade["quantity"] = bot_config.order_size_usd / row.open

    results = BacktestResult(
        trades=trades,
        ending_balance=balance,
        max_drawdown=0.0,
        average_drawdown=0.0,
        gain_loss=total_profit_loss,
        percent_gain_loss=0.0,
    )
    print(total_profit_loss)
    print(balance)
    export_results_to_excel(backtest_results=results, backtest_config=backtest_config, filename=bot_config.bot_name)
    return results


def export_results_to_excel(backtest_results: BacktestResult, backtest_config: BacktestConfig, filename: str) -> None:
    if not filename.lower().endswith(".xlsx"):
        filename += ".xlsx"

    results_folder = Path(__file__).parent / "results"
    results_folder.mkdir(parents=True, exist_ok=True)
    dest_path = results_folder / filename

    trade_data = []
    for trade in backtest_results.trades:
        trade_data.append({
            "asset": trade.asset.value,
            "entry_datetime": (
                trade.entry_datetime.isoformat() if trade.entry_datetime else ""
            ),
            "entry_price": trade.entry_price,
            "close_datetime": (
                trade.close_datetime.isoformat() if trade.close_datetime else ""
            ),
            "close_price": trade.close_price,
            "quantity": trade.quantity if trade.quantity is not None else "",
            "profit_loss": trade.profit_loss if trade.profit_loss is not None else "",
        })
    df_trades = pd.DataFrame(trade_data)

    wb = Workbook()

    ws_dashboard = wb.active
    ws_dashboard.title = "Dashboard"
    ws_dashboard["A1"] = "This sheet can be used for dashboard visuals."

    ws_data = wb.create_sheet("Backtest Data")

    ws_data["A1"] = "Backtest Configuration"
    config_items = {
        "start_date": backtest_config.start_date.isoformat(),
        "end_date": backtest_config.end_date.isoformat(),
        "starting_balance": backtest_config.starting_balance
    }
    for i, (key, value) in enumerate(config_items.items(), start=2):
        ws_data.cell(row=i, column=1, value=key)
        ws_data.cell(row=i, column=2, value=value)

    
    summary_items = {
        "ending_balance": backtest_results.ending_balance,
        "max_drawdown": backtest_results.max_drawdown,
        "average_drawdown": backtest_results.average_drawdown,
        "gain_loss": backtest_results.gain_loss,
        "percent_gain_loss": backtest_results.percent_gain_loss,
    }
    summary_start = len(config_items) + 4
    ws_data.cell(row=summary_start - 1, column=1, value="Backtest Result Summary")
    for i, (key, value) in enumerate(summary_items.items(), start=summary_start):
        ws_data.cell(row=i, column=1, value=key)
        ws_data.cell(row=i, column=2, value=value)

    trade_start = summary_start + len(summary_items) + 2
    for r_idx, row in enumerate(dataframe_to_rows(df_trades, index=False, header=True), start=trade_start):
        for c_idx, value in enumerate(row, start=1):
            ws_data.cell(row=r_idx, column=c_idx, value=value)

    wb.save(dest_path)

