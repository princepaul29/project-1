from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship, Session, select, func
from typing import Optional, List
from .click import Click

class ProductBase(SQLModel):
    name: str = Field(index=True)
    price: float = Field(index=True)
    url: str
    rating: float
    review_count: int
    query: Optional[str] = None
    source: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Use a lambda function

    def __repr__(self):
        return (f"Product(id={self.id}, name='{self.name}', price='{self.price}', "
                f"url='{self.url}', rating={self.rating}, review_count={self.review_count}, "
                f"query='{self.query}', source='{self.source}', timestamp={self.timestamp})")
    
class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship: one product has many clicks
    clicks: List["Click"] = Relationship(back_populates="product")

    __table_args__ = (
        UniqueConstraint("url", "source"),  # adjust if needed
    )

    def noc(self, session: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> int:
        statement = select(func.count()).where(Click.product_id == self.id)
        if start_date:
            statement = statement.where(Click.timestamp >= start_date)
        if end_date:
            statement = statement.where(Click.timestamp <= end_date)
        return session.exec(statement).one()
    
    def to_dict(self):
        """Convert Product instance to dictionary without relationship data"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "url": self.url,
            "rating": self.rating,
            "review_count": self.review_count,
            "query": self.query,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class ProductWithNOC(ProductBase):
    id: int
    noc: int