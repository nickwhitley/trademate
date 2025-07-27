from enum import Enum
from datetime import datetime

EARLIEST_BACKTEST_DATE = datetime(2023,1,1,0,0,0)

class Timeframe(Enum):
    M1 = 1
    M5 = 5
    M15 = 15
    M30 = 30
    H1 = 60
    H4 = 240
    D = 1440
    W = 10080
    D15 = 21600

class Asset(Enum):
    ADA_USD = "ADA_USD"
    BTC_USD = "BTC_USD"
    ETH_USD = "ETH_USD"
    XRP_USD = "XRP_USD"
    BNB_USD = "BNB_USD"
    SOL_USD = "SOL_USD"
