from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set
from domain.values.price import Price
from domain.types import PersonId, VisitId, Year, Month


# Composite types that express domain concepts using shared types
VisitKey = tuple[
    Year, Month, VisitId
]  # Unique identifier for a visit in a specific month
PersonVisits = Set[VisitKey]  # All visits for a person
VisitRegistry = Dict[PersonId, PersonVisits]  # Registry mapping people to their visits


@dataclass
class MonthlyVisitTracker:
    """
    Domain service to track visits per person per month.

    Business Rule: When a person drops garbage 3 times or more in 1 month,
    an additional fee of 5% is added to the total price, starting from the 3rd visit.
    The counter restarts each month.
    """

    # Track visits per person per month using meaningful domain types
    visit_registry: VisitRegistry = field(default_factory=dict)

    def record_visit(self, person_id: str, visit_date: str, visit_id: str) -> None:
        """Record a visit for a person on a specific date."""
        # Convert to domain types for better type safety
        domain_person_id = PersonId(person_id)
        domain_visit_id = VisitId(visit_id)

        # Parse the date to get year and month
        date_obj = datetime.fromisoformat(visit_date.replace("Z", "+00:00"))
        year = Year(date_obj.year)
        month = Month(date_obj.month)

        # Initialize person's visits if not exists
        if domain_person_id not in self.visit_registry:
            self.visit_registry[domain_person_id] = set()

        # Add this visit using meaningful domain types
        visit_key: VisitKey = (year, month, domain_visit_id)
        self.visit_registry[domain_person_id].add(visit_key)

    def get_monthly_visit_count(self, person_id: str, visit_date: str) -> int:
        """Get the number of visits for a person in the month of the given date."""
        domain_person_id = PersonId(person_id)

        if domain_person_id not in self.visit_registry:
            return 0

        # Parse the date to get year and month
        date_obj = datetime.fromisoformat(visit_date.replace("Z", "+00:00"))
        target_year = Year(date_obj.year)
        target_month = Month(date_obj.month)

        # Count visits in the same month using meaningful domain types
        visits_in_month = [
            visit
            for visit in self.visit_registry[domain_person_id]
            if visit[0] == target_year and visit[1] == target_month
        ]

        return len(visits_in_month)

    def should_apply_surcharge(self, person_id: str, visit_date: str) -> bool:
        """
        Check if the 5% surcharge should be applied for this visit.

        Returns True if this is the 3rd or later visit in the month.
        """
        visit_count = self.get_monthly_visit_count(person_id, visit_date)
        return visit_count >= 3

    def apply_monthly_surcharge(
        self, base_price: Price, person_id: str, visit_date: str
    ) -> Price:
        """
        Apply 5% surcharge if this is the 3rd or later visit in the month.

        Args:
            base_price: The calculated price before surcharge
            person_id: The person making the visit
            visit_date: The date of the visit

        Returns:
            The final price with surcharge applied if applicable
        """
        if self.should_apply_surcharge(person_id, visit_date):
            # Apply 5% surcharge
            surcharge_amount = base_price.amount * 0.05
            surcharge = Price(surcharge_amount, base_price.currency)
            return base_price.add(surcharge)

        return base_price

    def clear_all_visits(self) -> None:
        """Clear all recorded visits. Used when starting a new scenario."""
        self.visit_registry.clear()
