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
    open_above_hband = "open_above_hband"
    close_above_hband = "close_above_hband"
    open_below_lband = "open_below_lband"
    close_below_lband = "close_below_lband"
    inside_lband = "inside_lband"
    inside_hband = "inside_hband"
    inside_bands = "inside bands"


class Condition(BaseModel):
    operator: ConditionOperator
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None

    def validate_condition(self, actual: float) -> bool:
        if self.operator == ConditionOperator.greater_than:
            return actual > self.value
        elif self.operator == ConditionOperator.less_than:
            return actual < self.value
        elif self.operator == ConditionOperator.in_range:
            return self.range[0] <= actual <= self.range[1]
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
    