from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.scraper_config import ScraperConfig
from app.models.setting import Setting
from app.config.db import get_session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.post("/scrapers/{scraper_name}/enable")
def enable_scraper(scraper_name: str, session: SessionDep):
    config = session.exec(select(ScraperConfig).where(ScraperConfig.name == scraper_name)).first()
    if config:
        config.enabled = True
        session.commit()
        return {"status": "enabled"}
    else:
        return {"status": "not found"}

@router.post("/scrapers/{scraper_name}/disable")
def disable_scraper(scraper_name: str, session: SessionDep):
    config = session.exec(select(ScraperConfig).where(ScraperConfig.name == scraper_name)).first()
    if config:
        config.enabled = False
        session.commit()
        return {"status": "disabled"}
    else:
        return {"status": "not found"}

@router.get("/scrapers")
def get_scraper_configs(session: SessionDep):
    configs = session.exec(select(ScraperConfig)).all()
    return {"configs": configs}

@router.get("/scrapers/{scraper_name}")
def get_scraper_config(scraper_name: str, session: SessionDep):
    config = session.exec(select(ScraperConfig).where(ScraperConfig.name == scraper_name)).first()
    if config:
        return {"config": config}
    else:
        return {"status": "not found"}
    
@router.post("/cooldown")
def set_cooldown(minutes: int, session: Session = Depends(get_session)):
    setting = session.exec(select(Setting).where(Setting.key == "scrape_cooldown_minutes")).first()
    if setting:
        setting.value = str(minutes)
    else:
        setting = Setting(key="scrape_cooldown_minutes", value=str(minutes))
        session.add(setting)
    session.commit()
    return {"message": f"Cooldown updated to {minutes} minutes"}

@router.get("/cooldown")
def get_cooldown(session: Session = Depends(get_session)):
    setting = session.exec(select(Setting).where(Setting.key == "scrape_cooldown_minutes")).first()
    if setting:
        return {"cooldown": int(setting.value)}
    else:
        return {"cooldown": 10}