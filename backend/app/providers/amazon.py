import requests
import os
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

                if response.status_code != 200:
                    print(f"[ERROR] API failed on page {page}: {response.status_code}")
                    continue

                data = response.json()
                raw_products = data.get("search_results", [])

                products = self.parse_results(raw_products)

                if filters:
                    products = self.apply_filters(products, filters)

                results.extend(products)

                # Stop early if no next_page
                if not data.get("next_page"):
                    break

            except Exception as e:
                print(f"[ERROR] Exception during API request: {e}")

        return results
    
    def parse_results(self, raw_products):
        products = []

        for item in raw_products:
            try:
                name = item.get("name", "N/A")
                raw_price = item.get("sale_price", item.get("regular_price", "N/A"))
                url = item.get("product_url", "N/A")
                
                price = self.parse_price(f"${raw_price}")


                products.append(Product(name, price, url))
            except Exception as e:
                print(f"[ERROR] Failed to parse product: {e}")
        
        return products