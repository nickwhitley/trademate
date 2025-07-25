from typing_extensions import Literal
from ta.trend import SMAIndicator
import pandas as pd


def apply_sma(
        df: pd.DataFrame, 
        window: int = 9, 
        source: Literal['open','high','low','close'] = 'close'
) -> pd.DataFrame:
    
    sma_indicator = SMAIndicator(close=df['close'], window=9, fillna=True)
    df[f'sma_{window}'] = sma_indicator.sma_indicator()
    return df