from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd
from models.condition_operator import Condition, ConditionOperator

class Indicator(ABC):
    def __init__(self, name: str, allowed_conditions: List[ConditionOperator], output_column: str):
        self.name = name
        self.allowed_conditions = allowed_conditions
        self.output_column = output_column

    @abstractmethod
    def apply_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def evaluate_condition(self, condition: Condition, df: pd.DataFrame, index: int) -> bool:
        pass
