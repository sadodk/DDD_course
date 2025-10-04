"""Business entity - represents a business customer with multiple employees."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Optional, List
from domain.entities.visitor import Visitor
from domain.types import BusinessId


@dataclass
class Business:
    """
    Business Entity - Aggregate root representing a business with multiple employees.

    Entity characteristics:
    - Has identity (business_id)
    - Contains a collection of Visitor entities (employees)
    - Enforces business-level rules and invariants
    - Acts as an aggregate root with employees in its boundary
    """

    # Identity - what makes this business unique
    business_id: BusinessId

    # Business details
    name: str
    address: str
    city: str
    type: str = "business"  # Always "business"

    # Collection of employees (visitors) who are part of this business
    _employees: Set[Visitor] = field(default_factory=set)

    def __post_init__(self):
        """Enforce entity invariants."""
        if not self.business_id:
            raise ValueError("Business must have a valid ID")
        if not self.city:
            raise ValueError("Business must have a city")
        if not self.address:
            raise ValueError("Business must have an address")
        if self.type != "business":
            raise ValueError("Business entity must have type 'business'")

    def __eq__(self, other) -> bool:
        """Entity equality based on identity, not attributes."""
        if not isinstance(other, Business):
            return False
        return self.business_id == other.business_id

    def __hash__(self) -> int:
        """Hash based on identity for use in sets/dicts."""
        return hash(self.business_id)

    @property
    def employees(self) -> List[Visitor]:
        """Get a list of all employees (visitors) of this business."""
        return list(self._employees)

    def add_employee(self, employee: Visitor) -> None:
        """Add an employee to this business, enforcing business rules."""
        if employee.type != "business":
            raise ValueError("Only business-type visitors can be added as employees")

        # Verify the employee's address and city match the business
        if employee.city != self.city or employee.address != self.address:
            raise ValueError(
                f"Employee must have matching address and city to be part of the business. "
                f"Business: {self.city}, {self.address}. "
                f"Employee: {employee.city}, {employee.address}"
            )

        self._employees.add(employee)

    def has_employee(self, visitor_id: str) -> bool:
        """Check if a visitor is an employee of this business."""
        return any(employee.id == visitor_id for employee in self._employees)

    def get_employee(self, visitor_id: str) -> Optional[Visitor]:
        """Get an employee by their visitor ID."""
        for employee in self._employees:
            if employee.id == visitor_id:
                return employee
        return None

    @staticmethod
    def create_business_id(city: str, address: str) -> BusinessId:
        """Create a unique business ID based on city and address."""
        return BusinessId(f"{city}|{address}")
