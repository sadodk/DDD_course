"""Price calculation domain event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from domain.events.domain_event import DomainEvent
from domain.values.price import Price


@dataclass(frozen=True)
class PriceCalculatedEvent(DomainEvent):
    """
    Event emitted when a price has been calculated for a visit.

    This event is used to trigger side effects like:
    - Sending invoices to business customers
    - Logging pricing decisions
    - Analytics tracking
    """

    visitor_id: str
    visit_id: str
    calculated_price: Price
    customer_type: str  # 'individual' or 'business'
    customer_email: Optional[str] = None
    customer_city: Optional[str] = None
    occurred_at: datetime = field(default_factory=datetime.now)

    def is_business_customer(self) -> bool:
        """Check if this is a business customer requiring an invoice."""
        return self.customer_type == "business"
