from datetime import datetime, timedelta, timezone
from enum import Enum
from pydantic import BaseModel, ValidationInfo, field_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, info: ValidationInfo):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    

class TimeFrame(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"

    def get_date_range(self) -> DateRange:
        now = datetime.now(timezone.utc)
        if self == TimeFrame.day:
            return DateRange(start_date=now - timedelta(days=1), end_date=now)
        elif self == TimeFrame.week:
            return DateRange(start_date=now - timedelta(weeks=1), end_date=now)
        elif self == TimeFrame.month:
            return DateRange(start_date=now - timedelta(days=30), end_date=now)
        elif self == TimeFrame.year:
            return DateRange(start_date=now - timedelta(days=365), end_date=now)
        else:
            # fallback to a wide range if needed
            return DateRange(start_date=datetime.min, end_date=now)