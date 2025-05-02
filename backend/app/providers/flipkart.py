import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
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
        "link_class": "wjcEIp"
    }

    ALTERNATIVE_SELECTORS = {
        "product": "a.CGtC98",
        "name": "div.KzDlHZ",
        "price": "div.Nx9bqj",
        "link_class": "CGtC98" 
    }

    def __init__(self):
        super().__init__(self.BASE_URL)
    
    def search(self, query, max_pages=5, filters=None):
        results = []

        def scrape_page(page):
            html = self.get_html(query, page)
            if not html:
                return []
            products = self.parse_html(html)
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

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        products = []
        containers = soup.select(self.SELECTORS["product"])
        
        if not containers:
            containers = soup.select(self.ALTERNATIVE_SELECTORS["product"])

        if not containers:
            print("[WARN] No products found on this page.")

        for container in containers:
            try:
                name_elem, price_elem, link_elem = self._select_elements(container)

                if not link_elem:
                    link_elem = container

                name = self._extract_name(name_elem)
                price = self.parse_price(price_elem.get_text(strip=True)) if price_elem else "N/A"
                url = f"https://www.flipkart.com{link_elem['href']}" if link_elem else "N/A"

                products.append(Product(name, price, url))

            except Exception as e:
                print(f"[ERROR] Failed to process product: {e}\n{container}")
                continue
        
        return products

    def _select_elements(self, container):
        name_elem = container.select_one(self.SELECTORS["name"])
        if not name_elem:
            name_elem = container.select_one(self.ALTERNATIVE_SELECTORS["name"])
        price_elem = container.select_one(self.SELECTORS["price"])
        if not price_elem:
            price_elem = container.select_one(self.ALTERNATIVE_SELECTORS["price"])
        link_elem = container.find("a", href=True, class_=self.SELECTORS["link_class"])

        return (name_elem, price_elem, link_elem)

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
