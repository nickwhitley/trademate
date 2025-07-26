from abc import abstractmethod
from typing import List, Optional
import pandas as pd
from models.condition_operator import ConditionOperator

class Indicator:
    def __init__(self, name: str, allowed_conditions: List[ConditionOperator]):
        self.name = name
        self.allowed_conditions = allowed_conditions

    @abstractmethod
    def apply_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

