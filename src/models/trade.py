from pydantic import BaseModel, PositiveFloat
from datetime import datetime
from typing import Optional

class Trade(BaseModel):
    entry_datetime: datetime
    entry_price: PositiveFloat
    close_datetime: datetime
    close_price: PositiveFloat
    quantity: Optional[PositiveFloat] = None
    profit_loss: Optional[float] = None