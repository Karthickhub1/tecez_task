from pydantic import BaseModel
from typing import List


class CustomerCreate(BaseModel):
    customer_id: str
    name: str
    address: str
    email: str
    contact: str


class ProductCreate(BaseModel):
    item_id: str
    description: str
    unit_price: float


class OrderItem(BaseModel):
    item_id: str
    quantity: int


class OrderCreate(BaseModel):
    order_id: str
    customer_id: str
    line_items: List[OrderItem]