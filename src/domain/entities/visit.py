"""Visit entity - represents a waste disposal visit by a visitor."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List
from domain.types import VisitId, PersonId
from domain.dropped_fraction import DroppedFraction
from domain.price import Price


@dataclass
class Visit:
    """
    Visit Entity - A waste disposal visit made by a visitor.

    Entity characteristics:
    - Has identity (id)
    - Equality based on identity, not attributes
    - Contains business logic for price calculation
    - Aggregates DroppedFraction value objects
    """

    # Identity - what makes this entity unique
    id: VisitId

    # Attributes
    visitor_id: PersonId  # Reference to the Visitor entity
    date: datetime
    dropped_fractions: List[DroppedFraction]

    def __post_init__(self):
        """Enforce entity invariants."""
        if not self.id:
            raise ValueError("Visit must have a valid ID")
        if not self.visitor_id:
            raise ValueError("Visit must be associated with a visitor")
        if not self.dropped_fractions:
            raise ValueError("Visit must have at least one dropped fraction")
        if not isinstance(self.date, datetime):
            raise ValueError("Visit date must be a datetime object")

    def __eq__(self, other) -> bool:
        """Entity equality based on identity, not attributes.
        Two visits are equal if they have the same ID, regardless of other attributes
        """
        if not isinstance(other, Visit):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on identity for use in sets/dicts."""
        return hash(self.id)

    def calculate_base_price(
        self, visitor_city: str | None = None, customer_type: str | None = None
    ) -> Price:
        """
        Calculate the base price for this visit based on dropped fractions.
        Delegates to domain value objects

        Args:
            visitor_city: The city of the visitor for city-specific pricing
            customer_type: The customer type ('individual' for private, 'business' for business)

        Returns:
            The calculated base price before any surcharges
        """
        return DroppedFraction.sum(
            self.dropped_fractions, 
            visitor_city, 
            customer_type,
            str(self.visitor_id),  # Pass visitor_id for exemption tracking
            self.date  # Pass visit_date for exemption tracking
        )

    def get_total_weight(self) -> int:
        """Get the total weight of all dropped fractions in this visit.
        Aggregate calculation
        """
        return sum(fraction.weight.weight for fraction in self.dropped_fractions)

    def has_fraction_type(self, fraction_type_name: str) -> bool:
        """Check if this visit contains a specific type of waste fraction.
        Business query
        """
        return any(
            str(fraction.fraction_type) == fraction_type_name
            for fraction in self.dropped_fractions
        )

    def get_year_month(self) -> tuple[int, int]:
        """Get the year and month of this visit for monthly tracking."""
        return (self.date.year, self.date.month)

    def is_same_month(self, other_visit: Visit) -> bool:
        """Check if this visit is in the same month as another visit."""
        return self.get_year_month() == other_visit.get_year_month()

    def add_dropped_fraction(self, fraction: DroppedFraction) -> None:
        """Add a new dropped fraction to this visit."""
        if not isinstance(fraction, DroppedFraction):
            raise ValueError("Must add a valid DroppedFraction")
        self.dropped_fractions.append(fraction)

    def __str__(self) -> str:
        return f"Visit(id={self.id}, visitor_id={self.visitor_id}, date={self.date.date()})"

    def __repr__(self) -> str:
        return (
            f"Visit(id='{self.id}', visitor_id='{self.visitor_id}', "
            f"date={self.date.isoformat()}, fractions={len(self.dropped_fractions)})"
        )
