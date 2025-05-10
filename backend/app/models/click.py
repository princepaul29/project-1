from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .product import Product


class Click(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship: each click belongs to one product
    product: Optional["Product"] = Relationship(back_populates="clicks")
