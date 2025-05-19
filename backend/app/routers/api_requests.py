from fastapi import APIRouter, Query, Depends
from typing import Union
from sqlmodel import Session, func, select
from datetime import datetime
from app.models.api_request_log import ApiRequestLog
from app.config.db import get_session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.get("/{endpoint_name}/count")
async def api_request_count(
    endpoint_name: str,
    session: SessionDep,
    start_date: Union[datetime, None] = Query(default=None, description="Start date for filtering"),
    end_date: Union[datetime, None] = Query(default=None, description="End date for filtering"),
    status_code: Union[int, None] = Query(default=None, description="HTTP status code for filtering"),
    method: Union[str, None] = Query(default=None, description="HTTP method for filtering"),
):
    stmt = select(func.count()).select_from(ApiRequestLog).where(ApiRequestLog.endpoint == endpoint_name)

    if start_date:
        stmt = stmt.where(ApiRequestLog.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(ApiRequestLog.timestamp <= end_date)

    if status_code:
        stmt = stmt.where(ApiRequestLog.status_code == status_code)
    if method:
        stmt = stmt.where(ApiRequestLog.method == method.upper())

    count = session.exec(stmt).one()

    return {"count": count}

@router.get("/{endpoint_name}/log")
async def api_request_log(
    endpoint_name: str,
    session: SessionDep,
    start_date: Union[datetime, None] = Query(default=None, description="Start date for filtering"),
    end_date: Union[datetime, None] = Query(default=None, description="End date for filtering"),
    status_code: Union[int, None] = Query(default=None, description="HTTP status code for filtering"),
    method: Union[str, None] = Query(default=None, description="HTTP method for filtering"),
    limit: int = 50
):
    stmt = select(ApiRequestLog).where(ApiRequestLog.endpoint == endpoint_name)

    if start_date:
        stmt = stmt.where(ApiRequestLog.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(ApiRequestLog.timestamp <= end_date)

    if status_code:
        stmt = stmt.where(ApiRequestLog.status_code == status_code)
    if method:
        stmt = stmt.where(ApiRequestLog.method == method.upper())

    stmt = stmt.limit(limit)

    logs = session.exec(stmt).all()  # Execute the query

    return {"api-request-log": logs}
