"""Visitor entity - represents a person who visits the waste disposal facility."""

from __future__ import annotations
from dataclasses import dataclass
from domain.types import PersonId, CardId, EmailAddress


@dataclass
class Visitor:
    """
    Visitor Entity - A person who drops off waste.

    Entity characteristics:
    - Has identity (id)
    - Equality based on identity, not attributes
    - Mutable attributes (address, email can change)
    - Business rules and invariants
    """

    # Identity - what makes this entity unique
    id: PersonId

    # Attributes that can change over time
    type: str  # e.g., "individual", "business"
    address: str
    city: str
    card_id: CardId
    email: EmailAddress = EmailAddress("")

    def __post_init__(self):
        """Enforce entity invariants."""
        if not self.id:
            raise ValueError("Visitor must have a valid ID")
        if not self.city:
            raise ValueError("Visitor must have a city")
        if not self.card_id:
            raise ValueError("Visitor must have a card ID")

    def __eq__(self, other) -> bool:
        """Entity equality based on identity, not attributes.
        Two visitors are equal if they have the same ID, regardless of other attributes
        """

        if not isinstance(other, Visitor):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on identity for use in sets/dicts."""
        return hash(self.id)

    def update_email(self, new_email: str) -> None:
        """Business method to update email with validation."""
        if not new_email or "@" not in new_email:
            raise ValueError("Invalid email format")
        self.email = EmailAddress(new_email)

    def update_address(self, new_address: str, new_city: str) -> None:
        """Business method to update address with validation."""
        if not new_address or not new_city:
            raise ValueError("Address and city cannot be empty")
        self.address = new_address
        self.city = new_city

    def is_from_city(self, city_name: str) -> bool:
        """Business method to check if visitor is from a specific city."""
        return self.city.lower() == city_name.lower()

    def __str__(self) -> str:
        return f"Visitor(id={self.id}, city={self.city})"

    def __repr__(self) -> str:
        return f"Visitor(id='{self.id}', type='{self.type}', city='{self.city}')"
