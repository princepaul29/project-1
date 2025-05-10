from sqlmodel import Session, select, func
from typing import List, Optional
from app.models.product import Product
from app.models.click import Click
from app.models.api_request_log import ApiRequestLog

from sqlalchemy import or_, and_

from dataclasses import asdict, is_dataclass
from datetime import datetime

class StorageManager:
    def __init__(self, session: Session):
        self.session = session


    def _prepare_entry(self, item):
        # Assuming item is a Product instance or a dictionary
        if isinstance(item, dict):
            item = Product(**item)  # Convert dict to Product instance

        # if "timestamp" not in item:
        #    item["timestamp"] = datetime.now().isoformat()
        return item

    def add_or_update_product(self, product_data: Product) -> Product:
        existing = self.session.exec(
            select(Product).where(
                Product.url == product_data.url,
                Product.source == product_data.source,
            )
        ).first()

        if existing:
            # Update the existing record
            existing.name = product_data.name
            existing.price = product_data.price
            existing.timestamp = product_data.timestamp
        else:
            self.session.add(product_data)

        self.session.commit()
        self.session.refresh(existing or product_data)
        return existing or product_data


    def save_products(self, entries: List[Product]) -> List[Product]:
        if not entries:
            return []

        prepared_entries = [self._prepare_entry(e) for e in entries]

        # Extract URLs and sources for batch query
        urls_sources = [(p.url, p.source) for p in prepared_entries]

        # Query existing products in batch
        from sqlalchemy import tuple_
        existing_products = self.session.exec(
            select(Product).where(
                tuple_(Product.url, Product.source).in_(urls_sources)
            )
        ).all()

        # Create a lookup dictionary for existing products
        existing_lookup = {(p.url, p.source): p for p in existing_products}

        saved_products = []

        for product in prepared_entries:
            key = (product.url, product.source)
            if key in existing_lookup:
                existing = existing_lookup[key]
                existing.name = product.name
                existing.price = product.price
                existing.timestamp = product.timestamp
                saved_products.append(existing)
            else:
                self.session.add(product)
                saved_products.append(product)

        self.session.commit()

        print(f"[INFO] Saved {len(prepared_entries)} entries to the database.")
        return saved_products

    def get_products(
        self,
        query: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[Product]:
        stmt = select(Product)

        if query:
            # stmt = stmt.where(
            #     (Product.query.ilike(f"%{query}%")) |
            #     (Product.name.ilike(f"%{query}%"))
            # )

            keywords = query.lower().split()
            conditions = [
                or_(
                    Product.name.ilike(f"%{kw}%"),
                    Product.query.ilike(f"%{kw}%")
                )
                for kw in keywords
            ]
            stmt = stmt.where(and_(*conditions))
        if source:
            stmt = stmt.where(Product.source == source)
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)

        if limit is not None:
            stmt = stmt.limit(limit)

        return self.session.exec(stmt).all()

    def get_products_with_noc(
        self,
        query: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list:
        products = self.get_products(query, source, min_price, max_price, limit)

        enriched_products = []
        for product in products:
            noc = product.noc(self.session, start_date=start_date, end_date=end_date)
            product_dict = product.model_dump()
            product_dict["noc"] = noc
            enriched_products.append(product_dict)

        return enriched_products
