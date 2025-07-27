import pandas as pd
from typing_extensions import Literal
from models.condition_operator import ConditionOperator
from models.indicator import Indicator
from ta.volatility import AverageTrueRange

# TODO: Finish indicator
class ATR(Indicator):
    def __init__(self, window: int = 14, source: Literal['open','high','low','close'] = 'close'):
        self.window = window
        self.source = source
        super().__init__(
            name='rsi',
            allowed_conditions=[
                ConditionOperator.greater_than,
                ConditionOperator.in_range,
                ConditionOperator.less_than
            ],
            output_column=f"atr_{window}_{source}"
        )

    def apply_to_df(self, df: pd.DataFrame ) -> pd.DataFrame:
        atr_calc = AverageTrueRange(high=df['high'],low=df['low'],close=df['close'], window=self.window, fillna=True)
        df[self.output_column] = atr_calc.average_true_range()
        return df
    
    def evaluate_condition(self, condition, df: pd.DataFrame, index):
        value = df.iloc[index][self.output_column]
        return condition.validate_condition(value)