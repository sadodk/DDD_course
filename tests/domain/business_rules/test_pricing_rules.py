"""Tests for pricing business rules."""

from domain.business_rules.interface_pricing_rules import PricingContext
from domain.business_rules.concrete_pricing_rules import (
    PinevillePricingRule,
    DefaultPricingRule,
)
from domain.business_rules.pricing_rule_engine import PricingRuleEngine
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.weight import Weight
from domain.values.price import Price, Currency


class TestPricingContext:
    """Tests for PricingContext."""

    def test_is_business_customer(self):
        """Test business customer detection."""
        context = PricingContext(customer_type="business", city="Pineville")
        assert context.is_business_customer() is True
        assert context.is_individual_customer() is False

    def test_is_individual_customer(self):
        """Test individual customer detection."""
        context = PricingContext(customer_type="individual", city="Pineville")
        assert context.is_individual_customer() is True
        assert context.is_business_customer() is False

    def test_unknown_customer_type(self):
        """Test handling of unknown customer type."""
        context = PricingContext(customer_type="unknown", city="Pineville")
        assert context.is_individual_customer() is False
        assert context.is_business_customer() is False


class TestPinevillePricingRule:
    """Tests for PinevillePricingRule."""

    def test_can_apply_pineville(self):
        """Test rule applies to Pineville."""
        rule = PinevillePricingRule()
        context = PricingContext(customer_type="individual", city="Pineville")
        assert rule.can_apply(context) is True

    def test_cannot_apply_other_city(self):
        """Test rule doesn't apply to other cities."""
        rule = PinevillePricingRule()
        context = PricingContext(customer_type="individual", city="Oak City")
        assert rule.can_apply(context) is False

    def test_individual_green_waste_pricing(self):
        """Test individual customer green waste pricing in Pineville."""
        rule = PinevillePricingRule()
        context = PricingContext(customer_type="individual", city="Pineville")
        fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(10))

        price = rule.calculate_price(fraction, context)
        expected = Price(1.0, Currency.EUR)  # 0.10 * 10

        assert price == expected

    def test_business_construction_waste_pricing(self):
        """Test business customer construction waste pricing in Pineville."""
        rule = PinevillePricingRule()
        context = PricingContext(customer_type="business", city="Pineville")
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(5))

        price = rule.calculate_price(fraction, context)
        expected = Price(0.13 * 5, Currency.EUR)  # 0.13 * 5

        assert price == expected


class TestPricingRuleEngine:
    """Tests for PricingRuleEngine."""

    def test_pineville_individual_rule_selection(self):
        """Test engine selects Pineville rule for individual customers."""
        engine = PricingRuleEngine()
        context = PricingContext(customer_type="individual", city="Pineville")
        fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(10))

        price = engine.calculate_price(fraction, context)
        expected = Price(1.0, Currency.EUR)  # Pineville individual rate: 0.10 * 10

        assert price == expected

    def test_oak_city_business_rule_selection(self):
        """Test engine selects Oak City rule for business customers."""
        engine = PricingRuleEngine()
        context = PricingContext(customer_type="business", city="Oak City")
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(4))

        price = engine.calculate_price(fraction, context)
        expected = Price(0.84, Currency.EUR)  # Oak City business rate: 0.21 * 4

        assert price == expected

    def test_business_discount_rule_for_unknown_city(self):
        """Test engine selects business discount rule for unknown cities."""
        engine = PricingRuleEngine()
        context = PricingContext(customer_type="business", city="Unknown City")
        fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(13))

        price = engine.calculate_price(fraction, context)
        expected = Price(1.3, Currency.EUR)  # Business discount rate: 0.10 * 13

        assert price == expected

    def test_default_rule_fallback(self):
        """Test engine falls back to default rule when no other rules apply."""
        engine = PricingRuleEngine()
        context = PricingContext(customer_type="individual", city="Unknown City")
        fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(8))

        price = engine.calculate_price(fraction, context)
        expected = Price(0.8, Currency.EUR)  # Default rate: 0.10 * 8.0

        assert price == expected

    def test_get_applicable_rules(self):
        """Test getting all applicable rules for a context."""
        engine = PricingRuleEngine()
        context = PricingContext(customer_type="individual", city="Pineville")

        applicable_rules = engine.get_applicable_rules(context)

        # Should have PinevillePricingRule and DefaultPricingRule
        assert len(applicable_rules) == 2
        assert isinstance(applicable_rules[0], PinevillePricingRule)
        assert isinstance(applicable_rules[1], DefaultPricingRule)
