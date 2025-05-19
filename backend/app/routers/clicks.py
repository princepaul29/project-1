from fastapi import APIRouter, Query, Depends
from typing import Union
from datetime import datetime
from sqlmodel import Session, select, func
from app.models.click import Click
from app.models.product import Product
from app.config.db import get_session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.get("/products/noc")
async def get_total_clicks(
    session: SessionDep,
    start_date: Union[datetime, None] = Query(default=None, description="Start date for filtering"),
    end_date: Union[datetime, None] = Query(default=None, description="End date for filtering")
):
    stmt_total = select(func.count()).select_from(Click)
    stmt_flipkart = (
        select(func.count())
        .select_from(Click)
        .join(Product, Product.id == Click.product_id)
        .where(Product.source == "flipkart")
    )

    stmt_amazon = (
        select(func.count())
        .select_from(Click)
        .join(Product, Product.id == Click.product_id)
        .where(Product.source == "amazon")
    )

    if start_date:
        stmt = stmt.where(Click.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(Click.timestamp <= end_date)

    total = session.exec(stmt_total).one()
    flipkart = session.exec(stmt_flipkart).one()
    amazon = session.exec(stmt_amazon).one()

    return {"number_of_clicks": {"total": total, "flipkart": flipkart, "amazon": amazon}}


@router.get("/products/noc/total")
async def get_total_clicks(
    session: SessionDep,
    start_date: Union[datetime, None] = Query(default=None, description="Start date for filtering"),
    end_date: Union[datetime, None] = Query(default=None, description="End date for filtering")
):
    statement = select(func.count()).select_from(Click)

    if start_date:
        stmt = stmt.where(Click.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(Click.timestamp <= end_date)

    total = session.exec(statement).one()

    return {"number_of_clicks": total}

@router.get("/products/noc/{source}")
async def get_total_clicks(
    source: str,
    session: SessionDep,
    start_date: Union[datetime, None] = Query(default=None, description="Start date for filtering"),
    end_date: Union[datetime, None] = Query(default=None, description="End date for filtering")
):
    statement = (
        select(func.count())
        .select_from(Click)
        .join(Product, Product.id == Click.product_id)
        .where(Product.source == source)
    )

    if start_date:
        stmt = stmt.where(Click.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(Click.timestamp <= end_date)

    total = session.exec(statement).one()

    return {"number_of_clicks": total}