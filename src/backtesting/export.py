from datetime import datetime
from pathlib import Path
import pandas as pd
from models.backtest_result import BacktestResult
import matplotlib.pyplot as plt

from models.trade import Trade


# def export_results_to_excel(backtest_results: BacktestResult, filename: str) -> None:
#     results_folder = Path.cwd() / "results"
#     results_folder.mkdir(parents=True, exist_ok=True)

#     dest_path = results_folder / filename

#     # Convert trades to DataFrame
#     trades_df = pd.DataFrame([trade.model_dump() for trade in backtest_results.trades])
#     trades_df["entry_datetime"] = pd.to_datetime(trades_df["entry_datetime"])
#     trades_df["close_datetime"] = pd.to_datetime(trades_df["close_datetime"])

#     # Calculate cumulative balance for plotting
#     trades_df["cumulative_balance"] = trades_df["profit_loss"].cumsum()

#     # Dashboard DataFrame
#     dashboard_data = {
#         "Total Trades": [len(trades_df)],
#         "Largest Winner": [trades_df["profit_loss"].max()],
#         "Largest Loser": [trades_df["profit_loss"].min()],
#         "Total Gain/Loss": [backtest_results.gain_loss],
#         "Percent Gain/Loss": [backtest_results.percent_gain_loss],
#         "Max Drawdown": [backtest_results.max_drawdown],
#     }
#     dashboard_df = pd.DataFrame(dashboard_data)

#     # Create a plot for balance over time
#     plt.figure(figsize=(8, 4))
#     plt.plot(trades_df["close_datetime"], trades_df["cumulative_balance"], marker="o")
#     plt.title("Balance Over Time")
#     plt.xlabel("Close Time")
#     plt.ylabel("Cumulative Profit/Loss")
#     plt.tight_layout()
#     plot_path = results_folder / "balance_plot.png"
#     plt.savefig(plot_path)
#     plt.close()

#     # Write to Excel
#     with pd.ExcelWriter(dest_path, engine="xlsxwriter") as writer:
#         dashboard_df.to_excel(writer, sheet_name="Dashboard", index=False)
#         trades_df.to_excel(writer, sheet_name="Trades", index=False)

#         # Insert image into the Dashboard sheet
#         workbook = writer.book
#         worksheet = writer.sheets["Dashboard"]
#         worksheet.insert_image("H2", str(plot_path))


# # Create example data for testing
# example_trades = [
#     Trade(entry_datetime=datetime(2021, 1, 1, 9), entry_price=100, close_datetime=datetime(2021, 1, 1, 10),
#           close_price=110, quantity=1, profit_loss=10),
#     Trade(entry_datetime=datetime(2021, 1, 2, 9), entry_price=110, close_datetime=datetime(2021, 1, 2, 10),
#           close_price=105, quantity=1, profit_loss=-5),
#     Trade(entry_datetime=datetime(2021, 1, 3, 9), entry_price=105, close_datetime=datetime(2021, 1, 3, 10),
#           close_price=115, quantity=1, profit_loss=10),
# ]

# example_result = BacktestResult(
#     trades=example_trades,
#     ending_balance=115,
#     max_drawdown=-5,
#     average_drawdown=-2,
#     gain_loss=15,
#     percent_gain_loss=15.0,
# )

# export_results_to_excel(example_result, "backtest_results.xlsx")