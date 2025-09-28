"""Concrete pricing rules for specific business scenarios."""

from domain.business_rules.interface_pricing_rules import PricingRule, PricingContext
from domain.dropped_fraction import DroppedFraction
from domain.price import Price, Currency


class PinevillePricingRule(PricingRule):
    """Pricing rule for Pineville city."""

    INDIVIDUAL_RATES = {"Green waste": 0.05, "Construction waste": 0.15}

    BUSINESS_RATES = {"Green waste": 0.08, "Construction waste": 0.18}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to visitors from Pineville."""
        return context.city == "Pineville"

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Pineville rates."""
        fraction_name = str(fraction.fraction_type)

        if context.is_business_customer():
            rate = self.BUSINESS_RATES.get(fraction_name, 0.0)
        else:
            rate = self.INDIVIDUAL_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """High priority for city-specific rules."""
        return 10


class OakCityPricingRule(PricingRule):
    """Pricing rule for Oak City."""

    INDIVIDUAL_RATES = {"Green waste": 0.12, "Construction waste": 0.22}

    BUSINESS_RATES = {"Green waste": 0.15, "Construction waste": 0.25}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to visitors from Oak City."""
        return context.city == "Oak City"

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Oak City rates."""
        fraction_name = str(fraction.fraction_type)

        if context.is_business_customer():
            rate = self.BUSINESS_RATES.get(fraction_name, 0.0)
        else:
            rate = self.INDIVIDUAL_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """High priority for city-specific rules."""
        return 10


class BusinessCustomerDiscountRule(PricingRule):
    """General discount rule for business customers from unknown cities."""

    DISCOUNT_RATES = {"Green waste": 0.08, "Construction waste": 0.16}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to business customers from cities without specific rules."""
        return context.is_business_customer() and context.city not in [
            "Pineville",
            "Oak City",
        ]

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate discounted price for business customers."""
        fraction_name = str(fraction.fraction_type)
        rate = self.DISCOUNT_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """Medium priority for customer type rules."""
        return 50


class DefaultPricingRule(PricingRule):
    """Default pricing rule that serves as fallback when no other rules apply."""

    DEFAULT_RATES = {"Green waste": 0.10, "Construction waste": 0.19}

    def can_apply(self, context: PricingContext) -> bool:
        """Default rule always applies as fallback."""
        return True

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using default rates."""
        fraction_name = str(fraction.fraction_type)
        rate = self.DEFAULT_RATES.get(fraction_name, 0.0)

        from domain.price import Currency

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """Lowest priority - used as fallback."""
        return 1000
