from pydantic import BaseModel
from typing import List


class InvoiceRequest(BaseModel):
    date: str
    dropped_fractions: List[str]
    person_id: str
    visit_id: str


class InvoiceResponse(BaseModel):
    price_amount: float
    person_id: str
    visit_id: str
    price_currency: str
