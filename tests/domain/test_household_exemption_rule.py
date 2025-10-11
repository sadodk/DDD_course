"""Tests for the household exemption rule."""

from datetime import datetime
from domain.types import PersonId, CardId, EmailAddress
from domain.entities.visitor import Visitor
from domain.entities.household import Household
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.weight import Weight
from domain.business_rules.household_pricing_rules import (
    OakCityHouseholdConstructionExemptionRule,
)
from domain.business_rules.interface_pricing_rules import PricingContext
from infrastructure.repositories.in_memory_exemption_repository import (
    InMemoryExemptionRepository,
)
from infrastructure.repositories.in_memory_household_repository import (
    InMemoryHouseholdRepository,
)
from application.adapters.visitor_adapter import ExternalVisitorAdapter
from unittest.mock import MagicMock


class TestHouseholdExemptionRule:
    """Tests for household exemption rule."""

    def setup_method(self):
        """Set up test environment."""
        # Create mock adapter
        self.mock_adapter = MagicMock(spec=ExternalVisitorAdapter)

        # Create repositories
        self.exemption_repository = InMemoryExemptionRepository()
        self.household_repository = InMemoryHouseholdRepository(self.mock_adapter)

        # Create pricing rule
        self.rule = OakCityHouseholdConstructionExemptionRule(
            self.exemption_repository, self.household_repository
        )

        # Create test visitors/households
        self.address = "123 Oak St"
        self.city = "Oak City"

        # Create test visitors for the same household
        self.visitor1 = Visitor(
            id=PersonId("person1"),
            type="individual",
            address=self.address,
            city=self.city,
            card_id=CardId("card1"),
            email=EmailAddress("person1@example.com"),
        )

        self.visitor2 = Visitor(
            id=PersonId("person2"),
            type="individual",
            address=self.address,
            city=self.city,
            card_id=CardId("card2"),
            email=EmailAddress("person2@example.com"),
        )

        # Create a household and add visitors
        self.household_id = Household.create_household_id(self.city, self.address)
        self.household = Household(
            household_id=self.household_id,
            address=self.address,
            city=self.city,
        )
        self.household.add_resident(self.visitor1)
        self.household.add_resident(self.visitor2)

        # Save to repository
        self.household_repository.save(self.household)

        # Set up adapter mock to return our test visitors
        self.mock_adapter.get_visitor.side_effect = lambda id: {
            PersonId("person1"): self.visitor1,
            PersonId("person2"): self.visitor2,
        }.get(id)

    def test_rule_applicability(self):
        """Test rule applies to Oak City individuals dropping construction waste."""
        # Should apply for individual with construction waste in Oak City
        context = PricingContext(
            visitor_id="person1",
            customer_type="individual",
            city="Oak City",
            visit_date=datetime(2023, 5, 15),
        )
        assert self.rule.can_apply(context) is True

        # Should not apply for business visitors
        business_context = PricingContext(
            visitor_id="person1",
            customer_type="business",
            city="Oak City",
            visit_date=datetime(2023, 5, 15),
        )
        assert self.rule.can_apply(business_context) is False

        # Should not apply for other cities
        other_city_context = PricingContext(
            visitor_id="person1",
            customer_type="individual",
            city="Pine City",
            visit_date=datetime(2023, 5, 15),
        )
        assert self.rule.can_apply(other_city_context) is False

    def test_shared_household_exemption(self):
        """Test that household members share the exemption limit."""
        visit_date = datetime(2023, 5, 15)

        # Create contexts for both visitors
        context1 = PricingContext(
            visitor_id="person1",
            customer_type="individual",
            city="Oak City",
            visit_date=visit_date,
        )

        context2 = PricingContext(
            visitor_id="person2",
            customer_type="individual",
            city="Oak City",
            visit_date=visit_date,
        )

        # First visitor drops 400kg of construction waste (should be at low rate)
        fraction1 = DroppedFraction(
            fraction_type=FractionType.CONSTRUCTION_WASTE,
            weight=Weight(400),
        )

        price1 = self.rule.calculate_price(fraction1, context1)
        # Should be charged at the low rate: 400 * 0.125 = 50
        assert price1.amount == 50.0

        # Second visitor drops 200kg of construction waste
        # Since they share a household, 100kg should be at low rate, 100kg at high rate
        fraction2 = DroppedFraction(
            fraction_type=FractionType.CONSTRUCTION_WASTE,
            weight=Weight(200),
        )

        price2 = self.rule.calculate_price(fraction2, context2)
        # First 100kg at low rate (0.125), remaining 100kg at high rate (0.20)
        # 100 * 0.125 + 100 * 0.20 = 12.5 + 20 = 32.5
        assert price2.amount == 32.5

        # Check total exemption used for the household
        total_used = self.exemption_repository.get_used_exemption(
            self.household_id, visit_date.year
        )
        assert total_used == 600.0  # 400 from visitor1 + 200 from visitor2

    def test_different_year_exemption_reset(self):
        """Test that exemptions reset each calendar year."""
        # First visitor drops 400kg in 2023
        context1 = PricingContext(
            visitor_id="person1",
            customer_type="individual",
            city="Oak City",
            visit_date=datetime(2023, 5, 15),
        )

        fraction1 = DroppedFraction(
            fraction_type=FractionType.CONSTRUCTION_WASTE,
            weight=Weight(400),
        )

        price1 = self.rule.calculate_price(fraction1, context1)
        assert price1.amount == 50.0  # 400 * 0.125 = 50

        # Same visitor drops another 200kg in 2024 (new year should reset exemption)
        context2 = PricingContext(
            visitor_id="person1",
            customer_type="individual",
            city="Oak City",
            visit_date=datetime(2024, 1, 15),  # New year
        )

        fraction2 = DroppedFraction(
            fraction_type=FractionType.CONSTRUCTION_WASTE,
            weight=Weight(200),
        )

        price2 = self.rule.calculate_price(fraction2, context2)
        assert price2.amount == 25.0  # 200 * 0.125 = 25 (fresh exemption for new year)

        # Check exemption usage for each year
        usage_2023 = self.exemption_repository.get_used_exemption(
            self.household_id, 2023
        )
        usage_2024 = self.exemption_repository.get_used_exemption(
            self.household_id, 2024
        )

        assert usage_2023 == 400.0
        assert usage_2024 == 200.0
