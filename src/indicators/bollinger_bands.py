import pandas as pd
from typing_extensions import Literal
from models.condition_operator import Condition, ConditionOperator
from models.indicator import Indicator
from ta.volatility import BollingerBands as BB


class BollingerBands(Indicator):
    def __init__(self, window: int = 20, window_dev: int = 2, source: Literal['open','high','low','close'] = 'close'):
        self.window = window
        self.window_dev = window_dev
        self.source = source
        super().__init__(
            name='bollinger_bands',
            allowed_conditions=[
                ConditionOperator.open_above_hband,
                ConditionOperator.open_below_lband, 
                ConditionOperator.close_above_hband,
                ConditionOperator.close_below_lband,
                ConditionOperator.inside_lband,
                ConditionOperator.inside_hband,
                ConditionOperator.inside_bands
            ],
            output_column=f"bb_{window}_{source}"
        )

    def apply_to_df(self, df: pd.DataFrame ) -> pd.DataFrame:
        bb_calc = BB(close=df[self.source], window=self.window, window_dev=self.window_dev, fillna=True)
        df[f"{self.output_column}_hband"] = bb_calc.bollinger_hband()
        df[f"{self.output_column}_lband"] = bb_calc.bollinger_lband()
        df[f"{self.output_column}_mavg"] = bb_calc.bollinger_mavg()
        return df
    
    def evaluate_condition(self, condition: Condition, df: pd.DataFrame, index: int) -> bool:
        row = df.iloc[index]
        prev = df.iloc[index - 1] if index > 0 else row

        match condition.operator:
            case ConditionOperator.open_above_hband:
                return row['open'] > row[f"{self.output_column}_hband"]
            case ConditionOperator.open_below_lband:
                return row['open'] < row[f"{self.output_column}_lband"]
            case ConditionOperator.close_above_hband:
                return prev['close'] > prev[f"{self.output_column}_hband"]
            case ConditionOperator.close_below_lband:
                return prev['close'] < prev[f"{self.output_column}_lband"]
            case ConditionOperator.inside_lband:
                return row[f"{self.output_column}_lband"] < row['open'] < row[f"{self.output_column}_mavg"]
            case ConditionOperator.inside_hband:
                return row[f"{self.output_column}_hband"] > row['open'] > row[f"{self.output_column}_mavg"]
            case ConditionOperator.inside_bands:
                return row[f"{self.output_column}_hband"] > row['open'] > row[f"{self.output_column}_lband"]
            case _:
                raise ValueError(f"Unsupported operator {condition.operator} for BollingerBands")