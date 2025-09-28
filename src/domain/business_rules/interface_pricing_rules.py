"""Domain objects for pricing business rules."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from domain.price import Price

if TYPE_CHECKING:
    from domain.dropped_fraction import DroppedFraction


@dataclass(frozen=True)
class PricingContext:
    """Context information needed for pricing calculations."""

    customer_type: Optional[str] = None  # 'individual' or 'business'
    city: Optional[str] = None
    visitor_id: Optional[str] = None  # For tracking exemptions per visitor
    visit_date: Optional[datetime] = None  # For calendar year tracking

    def is_business_customer(self) -> bool:
        """Check if this is a business customer."""
        return self.customer_type == "business"

    def is_individual_customer(self) -> bool:
        """Check if this is an individual customer."""
        return self.customer_type == "individual"


class PricingRule(ABC):
    """Abstract base class for pricing business rules.

    Pricing rules encapsulate the business logic for calculating
    prices based on various factors like customer type, city, etc.
    """

    @abstractmethod
    def can_apply(self, context: PricingContext) -> bool:
        """Check if this rule can be applied to the given context.

        Args:
            context: The pricing context to evaluate

        Returns:
            True if this rule applies, False otherwise
        """
        pass

    @abstractmethod
    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate the price for a dropped fraction.

        Args:
            fraction: The dropped fraction to price
            context: The pricing context

        Returns:
            The calculated price for the fraction
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get the priority of this rule for ordering.

        Lower numbers = higher priority.
        Rules with higher priority are evaluated first.

        Returns:
            Priority value (0 = highest priority)
        """
        pass
