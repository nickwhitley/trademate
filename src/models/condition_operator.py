from enum import Enum
from typing import Optional

import pandas as pd
from pydantic import BaseModel


class ConditionOperator(str, Enum):
    greater_than = "greater_than"
    less_than = "less_than"
    in_range = "in_range"
    above_price = "above_price"
    below_price = "below_price"
    at_price = "at_price"
    price_crossed_above = "price_crossed_above"
    price_crossed_below = "price_crossed_below"


class Condition(BaseModel):
    operator: ConditionOperator
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None

    def validate_condition(self, actual: float, current_row: pd.Series, prev_row: pd.Series) -> bool:
        if self.operator == ConditionOperator.greater_than:
            return actual > self.value
        elif self.operator == ConditionOperator.less_than:
            return actual < self.value
        elif self.operator == ConditionOperator.in_range:
            return self.range[0] <= actual <= self.range[1]
        elif self.operator == ConditionOperator.below_price:
            return current_row.open > actual
        elif self.operator == ConditionOperator.above_price:
            return current_row.open < actual
        elif self.operator == ConditionOperator.at_price:
            return min(current_row.open, current_row.close) <= actual <= max(current_row.open, current_row.close)
        elif self.operator == ConditionOperator.price_crossed_above:
            return (current_row.open < actual < current_row.close) and prev_row.high < actual
        elif self.operator == ConditionOperator.price_crossed_below:
            return (current_row.open > actual > current_row.close) and prev_row.low > actual
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
    