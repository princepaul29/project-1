from app.models.setting import Setting
from sqlmodel import Session, select
from datetime import timedelta

def get_scrape_cooldown(session: Session) -> timedelta:
    result = session.exec(select(Setting).where(Setting.key == "scrape_cooldown_minutes")).first()
    minutes = int(result.value) if result else 10  # default to 10 minutes
    return timedelta(minutes=minutes)