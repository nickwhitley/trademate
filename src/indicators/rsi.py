from typing_extensions import Literal
from ta.momentum import RSIIndicator
import pandas as pd

def apply_rsi(
        df: pd.DataFrame, 
        window: int = 14, 
        source: Literal['open','high','low','close'] = 'close'
) -> pd.DataFrame:
    rsi = RSIIndicator(close = df['close'], window=14, fillna=True)
    df['RSI'] = rsi.rsi()
    return df