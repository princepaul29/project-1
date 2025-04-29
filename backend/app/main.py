from fastapi import FastAPI
from typing import Union
from app.providers.flipkart import FlipkartScraper
from app.providers.amazon import AmazonAPIWrapper
from app.services.storage import StorageManager
from fastapi.responses import RedirectResponse
import os

app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/search")
def search(query: Union[str, None] = None, pages: int = 1, min_price: Union[int, None] = None, max_price: Union[int, None] = None):
    filters = {}
    if min_price:
        filters["min_price"] = min_price
    if max_price:
        filters["max_price"] = max_price

    print(f"Query: {query}")
    print(f"Max Pages: {pages}")
    print(f"Filters: {filters}")

    flipkart_scraper = FlipkartScraper()
    flipkart_results = flipkart_scraper.search(query, max_pages=pages, filters=filters)

    amazon_api = AmazonAPIWrapper(os.environ.get("SCRAPEHERO_API"))
    amazon_results= amazon_api.search(query, max_pages=pages, filters=filters)

    storage = StorageManager()
    storage.save_products(flipkart_results, query=query, source="Flipkart")
    storage.save_products(amazon_results, query=query, source="Amazon")

    return {"flipkart_results": flipkart_results, "amazon_results": amazon_results}