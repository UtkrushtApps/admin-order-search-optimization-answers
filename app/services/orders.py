from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Customer, Order
from app.schemas.order import OrderResponse


def _start_of_day(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _as_float(value: Decimal) -> float:
    return float(value)


def list_orders(
    db: Session,
    status: str,
    created_from: date,
    limit: int,
    offset: int,
) -> list[OrderResponse]:
    """Return a page of admin order search results.

    The previous implementation loaded the page of orders and then queried the
    customer table once per order. This version keeps the public response shape
    and offset/limit semantics, but performs the search and customer lookup in a
    single SQL statement that can use the composite orders search index.
    """
    created_at_lower_bound = _start_of_day(created_from)

    statement = (
        select(
            Order.id.label("id"),
            Order.order_number.label("order_number"),
            Order.status.label("status"),
            Order.created_at.label("created_at"),
            Order.total_amount.label("total_amount"),
            Order.currency.label("currency"),
            Customer.email.label("customer_email"),
        )
        .join(Customer, Customer.id == Order.customer_id)
        .where(
            Order.status == status,
            Order.created_at >= created_at_lower_bound,
        )
        .order_by(Order.created_at.desc(), Order.id.desc())
        .offset(offset)
        .limit(limit)
    )

    rows = db.execute(statement).mappings().all()

    return [
        OrderResponse(
            id=row["id"],
            order_number=row["order_number"],
            status=row["status"],
            created_at=row["created_at"],
            total_amount=_as_float(row["total_amount"]),
            currency=row["currency"],
            customer_email=row["customer_email"],
        )
        for row in rows
    ]
