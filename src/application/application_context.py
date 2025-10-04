"""Application setup with clean dependency management."""

from application.external_visitor_service import ExternalVisitorService
from application.price_calculator import PriceCalculator
from domain.business_rules.pricing_rule_engine import PricingRuleEngine
from domain.business_rules.concrete_pricing_rules import MonthlySurchargePricingRule
from domain.services.pricing_service import PricingService
from domain.services.construction_waste_exemption import (
    ConstructionWasteExemptionService,
)
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)
from infrastructure.repositories.in_memory_visitor_repository import (
    InMemoryVisitorRepository,
)


class ApplicationContext:
    """Dependency injection for the application."""

    def __init__(self):
        """Set up all dependencies in a clean, straightforward way."""
        # External services
        self.visitor_service = ExternalVisitorService()

        # Repositories (in-memory for workshop)
        self.visit_repository = InMemoryVisitRepository()
        self.visitor_repository = InMemoryVisitorRepository()

        # Set up pricing rules and engine
        pricing_engine = PricingRuleEngine()  # Creates with default pricing rules

        # Add monthly surcharge rule to the engine
        monthly_surcharge_rule = MonthlySurchargePricingRule(
            self.visit_repository, self.visitor_repository
        )
        pricing_engine.add_rule(monthly_surcharge_rule)

        # Domain services
        self.pricing_service = PricingService(pricing_engine=pricing_engine)

        # Application services
        self.price_calculator = PriceCalculator(
            self.visitor_service,
            self.pricing_service,
            self.visit_repository,
            self.visitor_repository,
        )

    def reset_for_new_scenario(self):
        """Reset state for testing scenarios."""
        self.visit_repository.clear_all_visits()
        self.visitor_service._users_cache = None
        # Reset the singleton exemption service
        ConstructionWasteExemptionService.reset_singleton()
