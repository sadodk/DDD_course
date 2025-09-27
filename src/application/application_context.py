"""Application setup with clean dependency management."""

from application.external_visitor_service import ExternalVisitorService
from application.price_calculator import PriceCalculator
from domain.services.monthly_surcharge_service import MonthlySurchargeService
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)


class ApplicationContext:
    """Dependency injection for the application."""

    def __init__(self):
        """Set up all dependencies in a clean, straightforward way."""
        # External services
        self.visitor_service = ExternalVisitorService()

        # Repositories (in-memory for workshop)
        self.visit_repository = InMemoryVisitRepository()

        # Domain services
        self.surcharge_service = MonthlySurchargeService(self.visit_repository)

        # Application services
        self.price_calculator = PriceCalculator(
            self.visitor_service, self.surcharge_service, self.visit_repository
        )

    def reset_for_new_scenario(self):
        """Reset state for testing scenarios."""
        self.visit_repository.clear_all_visits()
        self.visitor_service._users_cache = None
