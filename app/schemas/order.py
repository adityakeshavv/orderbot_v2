from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrderOut(BaseModel):
    id:            int
    product:       str
    quantity:      int
    status:        str
    delivery_date: Optional[str] = None
    created_at:    str

    model_config = {"from_attributes": True}
