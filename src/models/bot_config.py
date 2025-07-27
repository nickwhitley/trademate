from typing import Optional
from pydantic import BaseModel, model_validator
from constants import Asset, Timeframe
from typing_extensions import Self

from models.trade_condition import TradeCondition


class BotConfig(BaseModel):
    bot_name: str
    assets: list[Asset]
    timeframe: Timeframe
    entry_conditions: list[TradeCondition]
    exit_conditions: list[TradeCondition]
    order_size_usd: Optional[float] = None
    risk_percent_per_trade: Optional[float] = None

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        if not self.assets:
            raise ValueError("must provide at least one asset for backtesting")
        
        if (self.order_size_usd is None) == (self.risk_percent_per_trade is None):
            raise ValueError("Set either 'order_size_usd' or 'risk_percent_per_trade', but not both.")
        
        return self
