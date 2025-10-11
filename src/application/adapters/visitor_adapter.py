"""Anti-corruption layer for external visitor service.

- Translates external DTOs (VisitorInfo) to domain entities (Visitor)
- Protects the domain from external service changes (anti-corruption pattern)
- Groups business visitors by address and city (domain concept)
- Creates domain-specific identifiers (BusinessId using Business.create_business_id)
- Acts as a boundary between external systems and pure domain model
"""

from typing import Dict, Optional, List
from domain.entities.visitor import Visitor
from domain.entities.business import Business
from domain.types import PersonId, BusinessId, CardId, EmailAddress
from application.external.visitor_api_client import ExternalVisitorService, VisitorInfo


class ExternalVisitorAdapter:
    """
    Anti-corruption layer between external visitor service and our domain model.

    This adapter:
    1. Translates between external VisitorInfo DTOs and our domain Visitor entities
    2. Handles identifying and grouping business customers by address + city
    3. Protects our domain model from changes in the external service
    """

    def __init__(self, external_visitor_service: ExternalVisitorService):
        """Initialize with the external visitor service."""
        self._external_service = external_visitor_service
        self._visitor_cache: Dict[str, Visitor] = {}
        self._business_map: Dict[str, List[Visitor]] = {}

    def get_visitor(self, visitor_id: PersonId) -> Optional[Visitor]:
        """
        Get a visitor by ID, translating from external service to domain model.

        Args:
            visitor_id: ID of the visitor to retrieve

        Returns:
            Domain Visitor entity if found, None otherwise
        """
        # Check cache first
        if visitor_id in self._visitor_cache:
            return self._visitor_cache[visitor_id]

        # Fetch from external service
        external_visitor = self._external_service.get_visitor_by_id(visitor_id)
        if not external_visitor:
            return None

        # Convert to domain entity
        visitor = self._to_domain_visitor(external_visitor)

        # Cache for future use
        self._visitor_cache[visitor_id] = visitor

        # If business visitor, add to business map
        if visitor.type == "business":
            business_id = Business.create_business_id(visitor.city, visitor.address)
            if business_id not in self._business_map:
                self._business_map[business_id] = []
            self._business_map[business_id].append(visitor)

        return visitor

    def get_all_visitors(self) -> List[Visitor]:
        """
        Get all visitors from the external service, converted to domain entities.

        Returns:
            List of domain Visitor entities
        """
        external_visitors = self._external_service._get_all_users()
        visitors = [self._to_domain_visitor(info) for info in external_visitors]

        # Update cache and business map
        for visitor in visitors:
            self._visitor_cache[visitor.id] = visitor
            if visitor.type == "business":
                business_id = Business.create_business_id(visitor.city, visitor.address)
                if business_id not in self._business_map:
                    self._business_map[business_id] = []
                if visitor not in self._business_map[business_id]:
                    self._business_map[business_id].append(visitor)

        return visitors

    def get_all_business_visitors(self) -> Dict[BusinessId, List[Visitor]]:
        """
        Get all business visitors grouped by business.

        This method ensures all business visitors are loaded from the external service
        and properly mapped to businesses by address and city.

        Returns:
            Dictionary mapping business IDs to lists of visitor entities
        """
        # Ensure all visitors are loaded
        if not self._business_map:
            self.get_all_visitors()

        # Convert string keys to BusinessId type
        return {BusinessId(k): v for k, v in self._business_map.items()}

    def get_business_visitors(self, business_id: BusinessId) -> List[Visitor]:
        """
        Get all visitors belonging to a specific business.

        Args:
            business_id: ID of the business

        Returns:
            List of visitor entities belonging to the business
        """
        # Ensure all visitors are loaded
        if not self._business_map:
            self.get_all_visitors()

        return self._business_map.get(business_id, [])

    def get_business_for_visitor(self, visitor_id: PersonId) -> Optional[BusinessId]:
        """
        Get the business ID for a visitor.

        Args:
            visitor_id: ID of the visitor

        Returns:
            Business ID if the visitor belongs to a business, None otherwise
        """
        visitor = self.get_visitor(visitor_id)
        if not visitor or visitor.type != "business":
            return None

        return Business.create_business_id(visitor.city, visitor.address)

    def _to_domain_visitor(self, info: VisitorInfo) -> Visitor:
        """
        Convert external VisitorInfo DTO to domain Visitor entity.

        Args:
            info: External visitor information

        Returns:
            Domain Visitor entity
        """
        return Visitor(
            id=PersonId(info.id),
            type=info.type,
            address=info.address,
            city=info.city,
            card_id=CardId(info.card_id),
            email=EmailAddress(info.email if info.email else ""),
        )

    def clear_cache(self) -> None:
        """Clear the adapter cache."""
        self._visitor_cache.clear()
        self._business_map.clear()
        self._external_service.clear_cache()
