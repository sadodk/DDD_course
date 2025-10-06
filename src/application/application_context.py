"""Application setup with clean dependency management."""

from application.external_visitor_service import ExternalVisitorService
from application.external_visitor_adapter import ExternalVisitorAdapter
from application.price_calculator import PriceCalculator
from domain.business_rules.pricing_rule_engine import PricingRuleEngine
from domain.business_rules.concrete_pricing_rules import MonthlySurchargePricingRule
from domain.services.pricing_service import PricingService
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)
from infrastructure.repositories.in_memory_visitor_repository import (
    InMemoryVisitorRepository,
)
from infrastructure.repositories.in_memory_exemption_repository import (
    InMemoryExemptionRepository,
)
from infrastructure.repositories.in_memory_business_repository import (
    InMemoryBusinessRepository,
)
from infrastructure.repositories.in_memory_household_repository import (
    InMemoryHouseholdRepository,
)

# Add rules that require explicit dependencies
from domain.business_rules.concrete_pricing_rules import (
    OakCityBusinessConstructionExemptionRule,
)
from domain.business_rules.household_pricing_rules import (
    OakCityHouseholdConstructionExemptionRule,
)


class ApplicationContext:
    """Dependency injection for the application."""

    def __init__(self):
        """Set up all dependencies in a clean, straightforward way."""
        # External services
        self.visitor_service = ExternalVisitorService()

        # Anti-corruption layer
        self.external_visitor_adapter = ExternalVisitorAdapter(self.visitor_service)

        # Repositories (in-memory for workshop)
        self.visit_repository = InMemoryVisitRepository()
        self.visitor_repository = InMemoryVisitorRepository()
        self.exemption_repository = InMemoryExemptionRepository()
        self.business_repository = InMemoryBusinessRepository(
            self.external_visitor_adapter
        )
        self.household_repository = InMemoryHouseholdRepository(
            self.external_visitor_adapter
        )

        # Set up pricing rules and engine
        pricing_engine = PricingRuleEngine()  # Creates with default rules

        # Add the Oak City business construction exemption rule with our exemption repository
        oak_city_business_exemption_rule = OakCityBusinessConstructionExemptionRule(
            self.exemption_repository, self.business_repository
        )
        pricing_engine.add_rule(oak_city_business_exemption_rule)

        # Add the Oak City household construction exemption rule with our exemption repository
        oak_city_household_exemption_rule = OakCityHouseholdConstructionExemptionRule(
            self.exemption_repository, self.household_repository
        )
        pricing_engine.add_rule(oak_city_household_exemption_rule)

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
        # Clear the repositories
        self.exemption_repository.clear_all_exemptions()
        self.business_repository.clear()
        self.household_repository.clear()
        # Reset the adapter
        self.external_visitor_adapter._visitor_cache = {}
        self.external_visitor_adapter._business_map = {}
