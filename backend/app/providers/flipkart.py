import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseScraper
from ..models.product import Product
from ..services.storage import StorageManager

class FlipkartScraper(BaseScraper):
    BASE_URL = "https://www.flipkart.com/search?"
    
    SELECTORS = {
        "product": "div.slAVV4",
        "name": "a.wjcEIp",
        "price": "div.Nx9bqj",
        "link_class": "wjcEIp",
        "rating": "div.XQDdHH",
        "ratings_count": "span.Wphh3N"
    }

    ALTERNATIVE_SELECTORS = {
        "product": "a.CGtC98",
        "name": "div.KzDlHZ",
        "price": "div.Nx9bqj",
        "link_class": "CGtC98",
        "rating": "div.XQDdHH",
        "ratings_count": "span.Wphh3N"
    }

    THIRD_SELECTORS = {
        "product": "._1sdMkc",
        "name": "a.WKTcLC",
        "price": "div.Nx9bqj",
        "link_class": "rPDeLR"
    }

    def __init__(self):
        super().__init__(self.BASE_URL)
    
    def search(self, query, max_pages=5, filters=None):
        results = []

        def scrape_page(page):
            html = self.get_html(query, page)
            if not html:
                return []
            products = self.parse_html(html, query)
            return self.apply_filters(products, filters) if filters else products


        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scrape_page, page) for page in range(1, max_pages + 1)]

            for future in as_completed(futures):
                try:
                    page_results = future.result()
                    results.extend(page_results)
                except Exception as e:
                    print(f"[ERROR] Exception while scraping: {e}")

        return results

    def get_html(self, query, page=1):
        params = {"q": query, "page": page}
        url = f"{self.BASE_URL}{urlencode(params)}"
        response = requests.get(url, headers=self.headers)
        return response.text if response.status_code == 200 else None

    def _clean_url(self, url):
        parsed = urlparse(url)
        # Define query parameters to keep (e.g., 'pid' is important)
        allowed_params = {'pid'}
        query_params = dict(parse_qsl(parsed.query))
        filtered_params = {k: v for k, v in query_params.items() if k in allowed_params}
        cleaned_query = urlencode(filtered_params)
        cleaned_url = urlunparse(parsed._replace(query=cleaned_query))
        return cleaned_url

    def parse_html(self, html, query):
        soup = BeautifulSoup(html, "html.parser")
        products = []
        
        containers = (
            soup.select(self.SELECTORS["product"]) or
            soup.select(self.ALTERNATIVE_SELECTORS["product"]) or
            soup.select(self.THIRD_SELECTORS["product"])
        )


        if not containers:
            print("[WARN] No products found on this page.")

        for container in containers:
            try:
                name_elem, price_elem, link_elem, rating_elem, ratings_count_elem = self._select_elements(container)

                name = self._extract_name(name_elem)
                price = self.parse_price(price_elem.get_text(strip=True)) if price_elem else None
                raw_url = f"https://www.flipkart.com{link_elem['href']}" if link_elem else None
                url = self._clean_url(raw_url)
                rating = self._aggregate_rating(float(rating_elem.get_text(strip=True))) if rating_elem else 0.0
                ratings_count = self._extract_ratings_count(ratings_count_elem)

                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    rating=rating,
                    review_count=ratings_count,
                    query=query,
                    source="flipkart"
                )

                products.append(product)

            except Exception as e:
                print(f"[ERROR] Failed to process product: {e} of {container.name}")
                continue
        
        return products
    
    def _select_elements(self, container):
        container_classes = container.get("class", [])

        for selector_set in [self.SELECTORS, self.ALTERNATIVE_SELECTORS, self.THIRD_SELECTORS]:
            if selector_set["product"].strip(".") not in container_classes:
                # print(f"[INFO] Skipping container with class {container_classes} for selector {selector_set['product']}")
                continue
            
            name_elem = container.select_one(selector_set["name"])
            price_elem = container.select_one(selector_set["price"])
            rating_elem = container.select_one(selector_set["rating"]) if "rating" in selector_set else None
            ratings_count_elem = container.select_one(selector_set["ratings_count"]) if "ratings_count" in selector_set else None
            link_elem = container.select_one(f'a.{selector_set["link_class"]}[href]')

            return name_elem, price_elem, link_elem, rating_elem, ratings_count_elem

        return None, None, None, None, None

    
    def _extract_ratings_count(self, ratings_count_elem):
        if not ratings_count_elem:
            return 0

        # Get all visible text inside, with whitespace normalized
        text = ratings_count_elem.get_text(separator=' ', strip=True)

        # Case 1: Match like "(962)"
        match = re.search(r'\(([\d,]+)\)', text)
        if match:
            return int(match.group(1).replace(',', ''))

        # Case 2: Match like "15,014 Ratings" (inside nested spans)
        match = re.search(r'([\d,]+)\s+Ratings', text)
        if match:
            return int(match.group(1).replace(',', ''))

        return 0

    
    def _aggregate_rating(self, rating):
        return round(rating * 0.97, 1)

    def _extract_name(self, elem):
        return elem.get("title") or elem.get_text(strip=True) if elem else "N/A"

# TODO: Used for testing purposes! Remove later
if __name__ == "__main__":
    scraper = FlipkartScraper()
    query = "phone"
    results = scraper.search(query, max_pages=2, filters={"min_price": 50})

    storage = StorageManager()

    # Save both results
    storage.save_products(results, query)
