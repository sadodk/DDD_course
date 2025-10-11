"""In-memory implementation of the Business repository."""

from typing import Dict, Optional, List
from domain.entities.business import Business
from domain.entities.visitor import Visitor
from domain.repositories.business_repository import BusinessRepository
from domain.types import BusinessId, PersonId
from application.adapters.visitor_adapter import ExternalVisitorAdapter


class InMemoryBusinessRepository(BusinessRepository):
    """
    In-memory implementation of the Business repository.

    This repository maintains the consistency boundary of the Business aggregate,
    ensuring that businesses and their employees are managed correctly.
    """

    def __init__(self, visitor_adapter: ExternalVisitorAdapter):
        """
        Initialize the repository with external visitor adapter.

        Args:
            visitor_adapter: Anti-corruption layer for external visitor service
        """
        self._visitor_adapter = visitor_adapter
        self._businesses: Dict[BusinessId, Business] = {}
        self._visitor_to_business_map: Dict[PersonId, BusinessId] = {}

    def save(self, business: Business) -> None:
        """
        Save or update a business entity and all its employees.

        Args:
            business: Business aggregate root to save
        """
        self._businesses[business.business_id] = business

        # Update visitor to business map
        for employee in business.employees:
            self._visitor_to_business_map[employee.id] = business.business_id

    def find_by_id(self, business_id: BusinessId) -> Optional[Business]:
        """
        Find a business by its ID.

        Args:
            business_id: Unique identifier for the business

        Returns:
            Business entity if found, None otherwise
        """
        return self._businesses.get(business_id)

    def find_by_visitor_id(self, visitor_id: PersonId) -> Optional[Business]:
        """
        Find a business by the ID of one of its employees.

        Args:
            visitor_id: ID of a visitor (employee)

        Returns:
            Business entity if found, None otherwise
        """
        if visitor_id not in self._visitor_to_business_map:
            # Try to find the business through the adapter
            business_id = self._visitor_adapter.get_business_for_visitor(visitor_id)
            if not business_id:
                return None

            # If we have the business locally, return it
            if business_id in self._businesses:
                return self._businesses[business_id]

            # Otherwise, create it
            visitor = self._visitor_adapter.get_visitor(visitor_id)
            if not visitor:
                return None
            return self.get_or_create_business_for_visitor(visitor)

        business_id = self._visitor_to_business_map[visitor_id]
        return self._businesses.get(business_id)

    def get_or_create_business_for_visitor(self, visitor: Visitor) -> Business:
        """
        Get an existing business for a visitor or create a new one if none exists.

        Args:
            visitor: A visitor entity that should be part of a business

        Returns:
            Existing or newly created business entity
        """
        if visitor.type != "business":
            raise ValueError("Can only create business for business-type visitors")

        # Generate business ID from visitor
        business_id = Business.create_business_id(visitor.city, visitor.address)

        # If we already have this business, add the visitor and return it
        if business_id in self._businesses:
            business = self._businesses[business_id]
            if not business.has_employee(visitor.id):
                business.add_employee(visitor)
                self._visitor_to_business_map[visitor.id] = business_id
            return business

        # Otherwise, create a new business
        business = Business(
            business_id=business_id,
            name=f"Business at {visitor.address}, {visitor.city}",  # Default name
            address=visitor.address,
            city=visitor.city,
        )
        business.add_employee(visitor)

        # Save the new business
        self.save(business)

        return business

    def get_all(self) -> List[Business]:
        """
        Get all businesses.

        Returns:
            List of all business entities
        """
        return list(self._businesses.values())

    def clear(self) -> None:
        """Clear all businesses from the repository."""
        self._businesses.clear()
        self._visitor_to_business_map.clear()

    def clear_all_businesses(self) -> None:
        """Alias for clear() method for backwards compatibility."""
        self.clear()
