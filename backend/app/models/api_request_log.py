from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class ApiRequestLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint: str
    status_code: int
    method: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
