"""Household entity to represent groups of individual customers living at the same address."""

from typing import List, Set
from domain.entities.visitor import Visitor
from domain.types import HouseholdId, PersonId


class Household:
    """
    Household aggregate root representing individuals living at the same address.

    This aggregate ensures that exemption rules are applied at the household level
    rather than per individual visitor. Multiple people at the same address form
    one household that shares exemption limits.
    """

    def __init__(self, household_id: HouseholdId, address: str, city: str):
        """
        Initialize a household with its identity and address information.

        Args:
            household_id: Unique identifier for the household
            address: Street address of the household
            city: City where the household is located
        """
        self.household_id = household_id
        self.address = address
        self.city = city
        self.residents: List[Visitor] = []
        self._resident_ids: Set[PersonId] = set()

    @staticmethod
    def create_household_id(city: str, address: str) -> HouseholdId:
        """
        Create a unique household ID from city and address.

        Args:
            city: City where the household is located
            address: Street address of the household

        Returns:
            A unique household ID
        """
        # Normalize the address and create a deterministic ID
        normalized = f"{city.lower()}:{address.lower().replace(' ', '')}"
        return HouseholdId(f"household:{normalized}")

    def add_resident(self, visitor: Visitor) -> None:
        """
        Add a resident to the household.

        Args:
            visitor: Visitor entity representing a household resident
        """
        if visitor.type != "individual":
            raise ValueError("Only individual visitors can be household residents")

        if visitor.id in self._resident_ids:
            return  # Already a resident, nothing to do

        self.residents.append(visitor)
        self._resident_ids.add(visitor.id)

    def has_resident(self, visitor_id: PersonId) -> bool:
        """
        Check if a visitor is a resident of this household.

        Args:
            visitor_id: ID of the visitor to check

        Returns:
            True if the visitor is a resident, False otherwise
        """
        return visitor_id in self._resident_ids

    def __eq__(self, other):
        """Equal if same household ID."""
        if not isinstance(other, Household):
            return False
        return self.household_id == other.household_id

    def __hash__(self):
        """Hash based on household ID."""
        return hash(self.household_id)
