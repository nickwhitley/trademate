from typing import Optional
import pandas as pd
from pydantic import BaseModel, ConfigDict, model_validator
from models.indicator import Indicator
from models.condition_operator import Condition

class TradeCondition(BaseModel):
    indicator: Indicator
    support_indicator: Optional[Indicator] = None
    condition: Condition

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def is_satisfied(self, row, prev_row) -> bool:
        value = getattr(row, self.indicator.output_column)
        return self.condition.validate_condition(value, row, prev_row)

    @model_validator(mode='after')
    def check_condition_allowed(self) -> 'TradeCondition':
        if self.condition.operator not in self.indicator.allowed_conditions:
            raise ValueError(
                f"Condition '{self.condition.operator}' is not allowed for indicator '{self.indicator.name}'. "
                f"Allowed: {self.indicator.allowed_conditions}"
            )
        return self

