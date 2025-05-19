from fastapi import APIRouter, Depends
from typing import Optional
from sqlmodel import Session, func, select
from app.models.date_range import TimeFrame
from app.models.visitor import Visitor
from app.config.db import get_session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.get("/count")
async def visitor_count(session: SessionDep):
    count = session.exec(select(func.count()).select_from(Visitor)).one()
    return {"total_visitors": count}

@router.get("/log")
async def visitor_log(
    session: SessionDep,
    limit: int = 50,
    time_frame: Optional[TimeFrame] = None
):
    statement = select(Visitor).order_by(Visitor.timestamp.desc()).limit(limit)
    if time_frame:
        data_range = time_frame.get_date_range()
        start_date = data_range.start_date
        end_date = data_range.end_date
        statement = statement.where(Visitor.timestamp >= start_date).where(Visitor.timestamp <= end_date)

    visitors = session.exec(statement).all()
    return {"visitors": visitors}