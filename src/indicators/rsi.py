from typing_extensions import Literal
from ta.momentum import RSIIndicator
import pandas as pd

from models.indicator import Indicator
from models.condition_operator import ConditionOperator


class RSI(Indicator):
    def __init__(self, window: int = 14, source: Literal['open','high','low','close'] = 'close'):
        self.window = window
        self.source = source
        super().__init__(
            name='rsi',
            allowed_conditions=[
                ConditionOperator.greater_than,
                ConditionOperator.in_range,
                ConditionOperator.less_than
            ]
        )

    def apply_to_df(self, df: pd.DataFrame ) -> pd.DataFrame:
        rsi_calc = RSIIndicator(close=df[self.source], window=self.window, fillna=True)
        df['rsi'] = rsi_calc.rsi()
        return df