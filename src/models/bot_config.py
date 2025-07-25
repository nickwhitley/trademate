from pydantic import BaseModel, model_validator
from constants import Asset, Timeframe
from typing_extensions import Self

class BotConfig(BaseModel):
    assets: list[Asset]
    timeframes: list[Timeframe]

    @model_validator(mode='after')
    def check_pairs(self) -> Self:
        if not self.assets:
            raise ValueError(f"must provide at least one asset for backtesting")
        return self
    
    @model_validator(mode='after')
    def check_pairs(self) -> Self:
        if not self.timeframes:
            raise ValueError(f"must provide at least one timeframe for backtesting")
        return self