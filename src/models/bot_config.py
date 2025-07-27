from pydantic import BaseModel, model_validator
from constants import Asset, Timeframe
from typing_extensions import Self

from models.trade_condition import TradeCondition


class BotConfig(BaseModel):
    assets: list[Asset]
    timeframe: Timeframe
    entry_conditions: list[TradeCondition]
    exit_conditions: list[TradeCondition]

    @model_validator(mode="after")
    def check_assets(self) -> Self:
        if not self.assets:
            raise ValueError(f"must provide at least one asset for backtesting")
        return self
