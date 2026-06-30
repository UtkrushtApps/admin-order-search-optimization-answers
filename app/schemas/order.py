from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    created_at: datetime
    total_amount: float
    currency: str
    customer_email: str
