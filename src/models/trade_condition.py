from pydantic import BaseModel
from models.indicator import Indicator

class TradeCondition(BaseModel):
    indicator: Indicator
    support_indicator: Indicator
    condition: None
    condition_met: bool

