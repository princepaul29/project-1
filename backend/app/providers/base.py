from abc import ABC, abstractmethod
import re
from currency_converter import CurrencyConverter

class BaseProvider(ABC):
    @abstractmethod
    def search(self, query, max_pages=1, filters=None):
        pass

    def apply_filters(self, products, filters):
        results = []

        min_price = filters.get("min_price")
        max_price = filters.get("max_price")

        for product in products:
            price = product.price

            if price is None:
                continue

            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue

            results.append(product)

        return results
    
    def parse_price(self, p):
        converter = CurrencyConverter()

        try:
            currency = self._detect_currency(p)

            # Extract only numbers and optional decimal part
            numeric = re.sub(r"[^\d.]", "", p)
            amount = float(numeric)

            # Convert to USD if needed
            if currency != "USD":
                amount = converter.convert(amount, currency, "USD")

            return int(amount)
        except:
            return None
    
    def _detect_currency(self, p):
        # Detect currency
        if "₹" in p:
            return "INR"
        elif "$" in p:
            return "USD"
        else:
            return None
        
class BaseScraper(BaseProvider):
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }