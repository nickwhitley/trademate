from pydantic import BaseModel, PositiveFloat, PositiveInt
from datetime import datetime
from typing import Optional

class Trade(BaseModel):
    entry_datetime: datetime
    entry_price: PositiveFloat
    close_datetime: datetime
    close_price: PositiveFloat
    size: Optional[PositiveInt] = None
    size_usd: Optional[PositiveFloat] = None