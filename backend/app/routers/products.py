from fastapi import APIRouter, Depends
from typing import Union, Optional, List
from sqlmodel import Session
from app.models.product import ProductWithNOC
from app.models.date_range import TimeFrame
from app.config.db import get_session
from app.services.storage import StorageManager
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.get("/", response_model=dict[str, List[ProductWithNOC]])
def get_products(
    session: SessionDep,
    query: Union[str, None] = None, 
    min_price: Union[int, None] = None,
    max_price: Union[int, None] = None,
    limit: int = 20,
    time_frame: Optional[TimeFrame] = None
):

    print(f"Query: {query}")

    storage = StorageManager(session)

    data_range = time_frame.get_date_range() if time_frame else None
    
    if data_range:
        start_date = data_range.start_date
        end_date = data_range.end_date
    else:
        start_date = None
        end_date = None
    
    results = storage.get_products_with_noc(query=query, min_price=min_price, max_price=max_price, start_date=start_date, end_date=end_date, limit=limit)

    return {
        "results": results
    }