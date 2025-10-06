"""Pricing rule for individual household construction waste exemptions."""

from domain.business_rules.interface_pricing_rules import PricingRule, PricingContext
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.price import Price, Currency
from domain.repositories.exemption_repository import ExemptionRepository
from domain.repositories.household_repository import HouseholdRepository
from domain.types import PersonId


class OakCityHouseholdConstructionExemptionRule(PricingRule):
    """Pricing rule for Oak City individual household customers with construction waste exemptions.

    Individual household customers in Oak City get exemptions on construction waste:
    - First 500kg per calendar year: 0.125 euro/kg
    - Over 500kg: 0.20 euro/kg

    Exemptions reset every calendar year.

    Note: The exemption applies at the household level, not per individual visitor.
    Multiple people living at the same address share the household exemption limit.
    """

    LOW_RATE = 0.125  # euro/kg for first 500kg
    HIGH_RATE = 0.20  # euro/kg over 500kg
    EXEMPTION_LIMIT_KG = 500.0  # Exemption limit in kg

    def __init__(
        self,
        exemption_repository: ExemptionRepository,
        household_repository: HouseholdRepository,
    ):
        """Initialize with repositories.

        Args:
            exemption_repository: Repository for tracking construction waste exemptions.
            household_repository: Repository for identifying and retrieving households.
        """
        self._exemption_repository = exemption_repository
        self._household_repository = household_repository

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to Oak City individual customers dropping construction waste."""
        return (
            context.city == "Oak City"
            and context.is_individual_customer()
            and context.visitor_id is not None
            and context.visit_date is not None
        )

    def get_priority(self) -> int:
        """High priority to override regular Oak City rules."""
        return 5

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Oak City household construction waste exemption rules."""
        # Type guards for required fields
        if context.visitor_id is None or context.visit_date is None:
            raise ValueError(
                "visitor_id and visit_date are required for exemption tracking"
            )

        # Only apply to construction waste
        if fraction.fraction_type != FractionType.CONSTRUCTION_WASTE:
            # Fall back to regular Oak City individual rate for other fraction types
            rate = 0.05 if fraction.fraction_type == FractionType.GREEN_WASTE else 0.15
            return Price(rate * fraction.weight.weight, Currency.EUR)

        # Find the household for this visitor
        household = self._household_repository.find_by_visitor_id(
            PersonId(context.visitor_id)
        )
        if not household:
            # If we can't find a household, fall back to standard individual pricing
            return Price(self.HIGH_RATE * fraction.weight.weight, Currency.EUR)

        # Apply tiered pricing for construction waste at the household level
        weight_kg = fraction.weight.weight
        low_rate_weight, high_rate_weight = (
            self._exemption_repository.calculate_tiered_weights(
                household.household_id,
                weight_kg,
                context.visit_date,
                self.EXEMPTION_LIMIT_KG,
            )
        )

        # Calculate total price
        low_rate_amount = self.LOW_RATE * low_rate_weight
        high_rate_amount = self.HIGH_RATE * high_rate_weight
        total_price = Price(low_rate_amount + high_rate_amount, Currency.EUR)

        # Record the construction waste for future exemption tracking
        self._exemption_repository.record_waste(
            household.household_id, weight_kg, context.visit_date
        )

        return total_price
