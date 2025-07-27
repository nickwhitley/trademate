from typing_extensions import Literal
from ta.trend import SMAIndicator
import pandas as pd

from models.condition_operator import ConditionOperator
from models.indicator import Indicator


class MA(Indicator):
    def __init__(self, window: int = 9, source: Literal['open','high','low','close'] = 'close'):
        self.window = window
        self.source = source
        super().__init__(
            name='ma',
            allowed_conditions=[
                ConditionOperator.above_price,
                ConditionOperator.below_price,
                ConditionOperator.at_price,
                ConditionOperator.price_crossed_above,
                ConditionOperator.price_crossed_below
            ],
            output_column=f"ma_{window}_{source}"
        )
        
    def apply_to_df(self, df):
        ma_indicator = SMAIndicator(close=df[self.source], window=self.window, fillna=True)
        df[self.output_column] = ma_indicator.sma_indicator()
        return df
