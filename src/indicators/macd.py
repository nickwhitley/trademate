import pandas as pd
from models.condition_operator import Condition, ConditionOperator
from models.indicator import Indicator
from ta.trend import macd


class MACD(Indicator):
    def __init__(self, window_slow: int = 26, window_fast: int = 12):
        self.window_slow = window_slow
        self.window_fast = window_fast
        super().__init__(
            name='macd',
            allowed_conditions=[
                ConditionOperator.slow_crossed_over_fast,
                ConditionOperator.slow_crossed_under_fast,
                ConditionOperator.slow_above_fast,
                ConditionOperator.slow_below_fast
                
            ],
            output_column=f"macd_{window_fast}_{window_slow}"
        )

    def apply_to_df(self, df: pd.DataFrame ) -> pd.DataFrame:
        macd_calc = macd(close=df['close'],window_slow=self.window_slow, window_fast=self.window_fast, fillna=True)
        df[self.output_column] = macd_calc
        return df
    
    def evaluate_condition(self, condition: Condition, df: pd.DataFrame, index: int) -> bool:
        row = df.iloc[index]
        prev = df.iloc[index - 1] if index > 0 else row

        match condition.operator:
            case ConditionOperator.slow_above_fast:
                return False
            case ConditionOperator.slow_below_fast:
                return False
            case ConditionOperator.slow_crossed_over_fast:
                return False
            case ConditionOperator.slow_crossed_under_fast:
                return False
            case _:
                raise ValueError(f"Unsupported operator {condition.operator} for BollingerBands")