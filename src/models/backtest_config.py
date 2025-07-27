from pydantic import BaseModel, PositiveFloat, model_validator
from datetime import datetime
from typing_extensions import Self


class BacktestConfig(BaseModel):
    start_date: datetime
    end_date: datetime
    starting_balance: PositiveFloat

    @model_validator(mode="after")
    def check_start_date(self) -> Self:
        min_date = datetime(2023, 1, 1)
        if self.start_date < min_date:
            raise ValueError(f"{self.start_date} is invalid, minimum start date: {min_date}")
        return self

    @model_validator(mode="after")
    def check_end_date(self) -> Self:
        max_date = datetime.now()
        if self.end_date > max_date:
            raise ValueError(f"{self.end_date} is invalid future date")
        return self
