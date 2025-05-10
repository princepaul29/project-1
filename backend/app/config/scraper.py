from sqlmodel import Session, select
from ..models.scraper_config import ScraperConfig
from app.config.db import engine

DEFAULT_SCRAPERS = [
    "flipkart",
    "amazon",
]

def init_scraper_config():
    with Session(engine) as session:
        for name in DEFAULT_SCRAPERS:
            exists = session.exec(
                select(ScraperConfig).where(ScraperConfig.name == name)
            ).first()
            if not exists:
                session.add(ScraperConfig(name=name, enabled=True))
        session.commit()