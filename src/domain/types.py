"""Shared domain type aliases for expressing ubiquitous language."""

from typing import NewType

# Domain-specific type aliases for better expressiveness
PersonId = NewType("PersonId", str)
VisitId = NewType("VisitId", str)
VisitDate = NewType("VisitDate", str)
Year = NewType("Year", int)
Month = NewType("Month", int)
CardId = NewType("CardId", str)
EmailAddress = NewType("EmailAddress", str)
BusinessId = NewType("BusinessId", str)
HouseholdId = NewType("HouseholdId", str)
