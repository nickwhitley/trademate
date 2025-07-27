from typing_extensions import Literal
from ta.trend import SMAIndicator
import pandas as pd

from models.condition_operator import Condition, ConditionOperator
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
    
    def evaluate_condition(self, condition: Condition, df: pd.DataFrame, index: int) -> bool:
        row = df.iloc[index]
        prev_row = df.iloc[index - 1] if index > 0 else row
        prev2_row = df.iloc[index - 2] if index > 0 else row
        ma_value = row[self.output_column]

        match condition.operator:
            case ConditionOperator.above_price:
                return ma_value > prev_row['close']
            case ConditionOperator.below_price:
                return ma_value < prev_row['close']
            case ConditionOperator.at_price:
                return min(prev_row.open, prev_row.close) <= ma_value <= max(prev_row.open, prev_row.close)
            case ConditionOperator.price_crossed_above:
                return (
                    prev2_row['close'] < prev2_row[self.output_column] and
                    prev_row['close'] > prev_row[self.output_column]
                )
            case ConditionOperator.price_crossed_below:
                return (
                    prev2_row['close'] > prev2_row[self.output_column] and
                    prev_row['close'] < prev_row[self.output_column]
                )
            case _:
                raise ValueError(f"Unsupported operator for MA: {condition.operator}")
    

