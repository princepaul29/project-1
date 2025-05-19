from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from typing import Union, Annotated, List, Dict
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from app.config.db import init_db, get_session
from app.config.scraper import init_scraper_config
from app.routers import admin, clicks, products, api_requests, visitors, websockets
from app.middleware.visitor import VisitorMiddleware
from app.providers.flipkart import FlipkartScraper
from app.providers.amazon import AmazonAPIWrapper
from app.services.storage import StorageManager
from app.services.settings import get_scrape_cooldown
from app.services.websocket import manager as websocket_manager
from app.models.product import Product
from app.models.click import Click
from app.models.scraper_config import ScraperConfig
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from urllib.parse import unquote
import os
import uuid
import asyncio

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Called on startup
    init_db()
    init_scraper_config()
    yield
    # Called on shutdown if needed

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or "*" for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(VisitorMiddleware)

app.include_router(clicks.router)
app.include_router(products.router, prefix="/products")
app.include_router(api_requests.router, prefix="/api-requests")
app.include_router(visitors.router, prefix="/visitors")
app.include_router(admin.router, prefix="/admin")
app.include_router(websockets.router) # Add the WebSocket router

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/search", response_model=Dict[str, Union[List[Product], str, Dict]])
async def search(
    background_tasks: BackgroundTasks,
    session: SessionDep,
    query: Union[str, None] = None, 
    pages: int = 1, 
    min_price: Union[int, None] = None,
    max_price: Union[int, None] = None
):
    filters = {}
    if min_price:
        filters["min_price"] = min_price
    if max_price:
        filters["max_price"] = max_price

    print(f"Query: {query}")
    print(f"Max Pages: {pages}")
    print(f"Filters: {filters}")

    configs = session.exec(select(ScraperConfig)).all()
    enabled_scrapers = {cfg.name: cfg.enabled for cfg in configs}
    print(f"Enabled Scrapers: {enabled_scrapers}")
    
    storage = StorageManager(session)

    # Generate a unique search ID for this request
    search_id = str(uuid.uuid4())
    
    cached_results = {}
    has_cached_results = False

    # Try loading from DB first
    for scraper in ("flipkart", "amazon"):
        if not enabled_scrapers.get(scraper, False):
            continue
        cached = storage.get_products(query, source=scraper, limit=25, min_price=min_price, max_price=max_price)
        if cached:
            cached_results[scraper] = cached
            has_cached_results = True

    should_scrape = True
    cooldown = get_scrape_cooldown(session)
    now = datetime.now(timezone.utc)

    # Flatten all cached products from all sources
    all_cached_products = []
    for products in cached_results.values():
        all_cached_products.extend(products)

    if all_cached_products:
        latest_timestamp = max(
            p.timestamp.replace(tzinfo=timezone.utc) if p.timestamp.tzinfo is None else p.timestamp
            for p in all_cached_products
        )

        if now - latest_timestamp < cooldown:
            should_scrape = False
            print("Using cached results, no need to scrape.")

    print(f"Should scrape: {should_scrape}")

    if should_scrape:
        # Always scrape in the background
        background_tasks.add_task(
            run_scrapers_and_update,
            query=query,
            pages=pages,
            filters=filters,
            enabled_scrapers=enabled_scrapers,
            search_id=search_id  # Pass the search ID
        )

    if has_cached_results:
        return {
            "results": cached_results,
            "search_id": search_id,  # Include search_id in the response
            "status": "cached"
        }
    else:
        return {
            "message": "Loading… scraping in progress.",
            "search_id": search_id,  # Include search_id in the response
            "status": "pending"
        }

async def run_scrapers_and_update(
    query, 
    pages, 
    filters, 
    enabled_scrapers, 
    search_id
):
    """
    Run scrapers in the background and update results via WebSockets.
    """
    results = {}
    
    # Create a new session for this background task since the original might be closed
    from app.config.db import engine
    with Session(engine) as session:
        storage = StorageManager(session)
        
        if enabled_scrapers.get("flipkart", True):
            flipkart_scraper = FlipkartScraper()
            flipkart_results = await run_in_threadpool(flipkart_scraper.search, query, max_pages=pages, filters=filters)
            flipkart_products = storage.save_products(flipkart_results)
            results["flipkart"] = flipkart_products
            
            for product in flipkart_products:
                session.refresh(product)

            # Notify clients immediately after Flipkart results are available
            await websocket_manager.broadcast_to_search(
                search_id, 
                {
                    "type": "update",
                    "source": "flipkart",
                    "results": [p.model_dump(mode="json") for p in flipkart_products],
                    "query": query
                }
            )

        if enabled_scrapers.get("amazon", True):
            amazon_api = AmazonAPIWrapper(os.environ.get("SCRAPEHERO_API"))
            amazon_results = await run_in_threadpool(amazon_api.search, query, max_pages=pages, filters=filters)
            amazon_products = storage.save_products(amazon_results)
            results["amazon"] = amazon_products

            for product in amazon_products:
                session.refresh(product)
            
            # Notify clients immediately after Amazon results are available
            await websocket_manager.broadcast_to_search(
                search_id, 
                {
                    "type": "update",
                    "source": "amazon",
                    "results": [p.model_dump(mode="json") for p in amazon_products],
                    "query": query
                }
            )

        # Send final completion message
        await websocket_manager.broadcast_to_search(
            search_id, 
            {
                "type": "complete",
                "query": query,
                "sources": list(results.keys())
            }
        )

    print(f"Scraping completed for query: {query}")

@app.get("/r")
def click(
    url: str,
    product_id: int,
    session: SessionDep,
):
    click = Click(product_id=int(product_id))
    session.add(click)
    session.commit()
    session.refresh(click)
    print(f"Click registered for product ID: {product_id}")

    return RedirectResponse(url=unquote(url))
