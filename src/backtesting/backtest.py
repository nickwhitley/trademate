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
from openpyxl import load_workbook
# from backtesting.export import export_results_to_excel


def run_backtest(
    bot_config: BotConfig, backtest_config: BacktestConfig
) -> BacktestResult:
    assets = bot_config.assets
    timeframe = bot_config.timeframe
    balance = backtest_config.starting_balance
    total_profit_loss = 0.0
    trades = []
    balance_history = [balance]  # Track balance after each trade
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
                    balance_history.append(balance)  # log balance after trade

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

    # ✅ Compute drawdowns
    def compute_drawdowns(history: list[float]) -> tuple[float, float]:
        peak = history[0] if history else 0
        drawdowns = []
        for bal in history:
            if bal > peak:
                peak = bal
            drawdowns.append(peak - bal)
        max_dd = max(drawdowns) if drawdowns else 0
        avg_dd = sum(drawdowns) / len(drawdowns) if drawdowns else 0
        return max_dd, avg_dd

    max_dd, avg_dd = compute_drawdowns(balance_history)

    gain_loss = balance - backtest_config.starting_balance
    percent_gain_loss = (gain_loss / backtest_config.starting_balance) * 100 if backtest_config.starting_balance else 0

    results = BacktestResult(
        trades=trades,
        ending_balance=round(balance, 2),
        max_drawdown=round(max_dd, 2),
        average_drawdown=round(avg_dd, 2),
        gain_loss=round(gain_loss, 2),
        percent_gain_loss=round(percent_gain_loss, 2),
    )
    print(f"Total P/L: {total_profit_loss}")
    print(f"Final Balance: {balance}")
    print(f"Max DD: {max_dd} | Avg DD: {avg_dd} | % Gain: {percent_gain_loss:.2f}%")
    return results


# def export_results_to_excel(backtest_results: BacktestResult, backtest_config: BacktestConfig, filename: str) -> None:
#     template_path = Path('./src/backtesting/results/backtest_results_template.xlsx')
#     output_path = template_path.parent / f"{filename}.xlsx"

#     workbook = load_workbook(template_path)

#     trades_data = [
#         {
#             "asset": str(trade.asset),  # Adjust if asset has fields like trade.asset.symbol
#             "entry_datetime": trade.entry_datetime,
#             "entry_price": trade.entry_price,
#             "close_datetime": trade.close_datetime,
#             "close_price": trade.close_price,
#             "quantity": trade.quantity,
#             "profit_loss": trade.profit_loss
#         }
#         for trade in backtest_results.trades
#     ]
#     trades_df = pd.DataFrame(trades_data)

#     # 2. Prepare backtest summary row
#     headers = [
#         "start_date", "end_date", "starting_balance",
#         "ending_balance", "gain/loss", "percent_gain",
#         "max_drawdown", "average_drawdown"
#     ]
#     summary_row = [[
#         backtest_config.start_date,
#         backtest_config.end_date,
#         backtest_config.starting_balance,
#         backtest_results.ending_balance,
#         backtest_results.gain_loss,
#         backtest_results.percent_gain_loss,
#         backtest_results.max_drawdown,
#         backtest_results.average_drawdown
#     ]]
#     summary_df = pd.DataFrame(summary_row, columns=headers)

#     # 3. Save to Excel using openpyxl
#     with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#         # Use the loaded workbook with writer
#         writer = pd.ExcelWriter(template_path)  # Use private API only because `book` is not settable

#         # Write the sheets
#         trades_df.to_excel(writer, sheet_name='trades', index=False)
#         summary_df.to_excel(writer, sheet_name='backtest_data', index=False)

#     print(f"Exported backtest results to: {output_path}")
