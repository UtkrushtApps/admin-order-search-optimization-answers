from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.metrics import get_query_count, reset_query_count
from app.db.session import get_db
from app.schemas.order import OrderResponse
from app.services.orders import list_orders

router = APIRouter(prefix="/api")


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    response: Response,
    status: str = Query(..., min_length=1, max_length=32),
    created_from: date = Query(..., alias="from"),
    limit: int = Query(100, ge=1, le=250),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    reset_query_count()
    orders = list_orders(
        db=db,
        status=status,
        created_from=created_from,
        limit=limit,
        offset=offset,
    )
    response.headers["X-SQL-Statements"] = str(get_query_count())
    return orders
