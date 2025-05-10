from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Visitor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ip: str
    user_agent: str
    path: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))