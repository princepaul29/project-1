import requests
import os
from app.models.api_request_log import ApiRequestLog
from app.config.db import engine
from datetime import datetime
from sqlmodel import Session
from app.config.db import get_session
from .base import BaseProvider
from ..models.product import Product
class AmazonAPIWrapper(BaseProvider):
    BASE_URL = "https://get.scrapehero.com/amz/keyword-search/"

    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query, max_pages=1, filters=None):
        results = []

        for page in range(1, max_pages + 1):
            params = {
                "x-api-key": self.api_key,
                "keyword": query,
                "country_code": "US",
                "page": page
            }
            
            try:
                response = requests.get(self.BASE_URL, params=params)

                with Session(engine) as session:
                    log_entry = ApiRequestLog(endpoint="amazon_search", status_code=response.status_code, method=response.request.method, timestamp=datetime.utcnow(), query=query)
                    session.add(log_entry)
                    session.commit()

                if response.status_code != 200:
                    print(f"[ERROR] API failed on page {page}: {response.status_code}")
                    continue

                data = response.json()
                raw_products = data.get("search_results", [])

                products = self.parse_results(raw_products, query)

                if filters:
                    products = self.apply_filters(products, filters)

                results.extend(products)

                # Stop early if no next_page
                if not data.get("next_page"):
                    break

            except Exception as e:
                print(f"[ERROR] Exception during API request: {e}")
        
        return results
    
    def parse_results(self, raw_products, query):
        products = []

        for item in raw_products:
            try:
                name = item.get("name", "N/A")
                raw_price = float(item.get("sale_price", item.get("regular_price", "N/A")))
                url = item.get("product_url", "N/A")
                rating = round(float(item.get("rating") or 0.0), 1)
                review_count = int(item.get("review_count", "0"))
                
                price = self.parse_price(f"${raw_price}")

                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    rating=rating,
                    review_count=review_count,
                    query=query,
                    source="amazon"
                )

                products.append(product)
            except Exception as e:
                print(product)
                print(f"[ERROR] Failed to parse product: {e}")
        
        return products