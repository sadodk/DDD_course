"""Pricing rule engine for orchestrating business rules."""

from typing import List, Optional
from domain.business_rules.interface_pricing_rules import (
    PricingRule,
    PricingContext,
)
from domain.business_rules.concrete_pricing_rules import (
    OakCityBusinessConstructionExemptionRule,
    PinevillePricingRule,
    OakCityPricingRule,
    BusinessCustomerDiscountRule,
    DefaultPricingRule,
)
from domain.values.dropped_fraction import DroppedFraction
from domain.values.price import Price


class PricingRuleEngine:
    """Engine for selecting and applying pricing rules.

    This engine maintains a registry of pricing rules and applies
    the most appropriate rule based on the pricing context.
    """

    def __init__(self, rules: Optional[List[PricingRule]] = None):
        """Initialize the pricing rule engine.

        Args:
            rules: List of pricing rules to use. If None, default rules are loaded.
        """
        if rules is None:
            self._rules = self._get_default_rules()
        else:
            self._rules = list(rules)

        # Sort rules by priority (lower number = higher priority)
        self._rules.sort(key=lambda rule: rule.get_priority())

    def _get_default_rules(self) -> List[PricingRule]:
        """Get the default set of pricing rules."""
        return [
            OakCityBusinessConstructionExemptionRule(),  # Uses singleton exemption service
            PinevillePricingRule(),
            OakCityPricingRule(),
            BusinessCustomerDiscountRule(),
            DefaultPricingRule(),  # Always add fallback rule last
        ]

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price for a dropped fraction using appropriate rule.

        Args:
            fraction: The dropped fraction to price
            context: The pricing context

        Returns:
            The calculated price

        Raises:
            ValueError: If no applicable rule is found (should not happen with DefaultPricingRule)
        """
        applicable_rule = self._find_applicable_rule(context)

        if applicable_rule is None:
            raise ValueError("No applicable pricing rule found")

        result = applicable_rule.calculate_price(fraction, context)
        return result

    def _find_applicable_rule(self, context: PricingContext) -> Optional[PricingRule]:
        """Find the first applicable rule for the given context.

        Rules are evaluated in priority order (highest priority first).

        Args:
            context: The pricing context to evaluate

        Returns:
            The first applicable rule, or None if no rule applies
        """
        for rule in self._rules:
            if rule.can_apply(context):
                return rule

        return None

    def add_rule(self, rule: PricingRule) -> None:
        """Add a new pricing rule to the engine.

        Args:
            rule: The pricing rule to add
        """
        self._rules.append(rule)
        # Re-sort to maintain priority order
        self._rules.sort(key=lambda r: r.get_priority())

    def get_applicable_rules(self, context: PricingContext) -> List[PricingRule]:
        """Get all rules that can apply to the given context.

        This is useful for debugging and testing purposes.

        Args:
            context: The pricing context to evaluate

        Returns:
            List of applicable rules in priority order
        """
        return [rule for rule in self._rules if rule.can_apply(context)]

    def apply_post_processing(
        self, base_price: Price, context: PricingContext
    ) -> Price:
        """Apply post-processing rules like surcharges to a base price.

        This method finds all applicable rules that implement calculate_surcharge_for_base_price
        and applies them to the base price.

        Args:
            base_price: The base price to post-process
            context: The pricing context

        Returns:
            Final price after applying all post-processing rules
        """
        final_price = base_price

        # Apply post-processing for rules that support it
        for rule in (
            self._rules
        ):  # Check ALL rules, not just applicable ones for post-processing
            if hasattr(rule, "calculate_surcharge_for_base_price"):
                # Use getattr to safely access the dynamic method
                surcharge_method = getattr(rule, "calculate_surcharge_for_base_price")
                surcharge = surcharge_method(base_price, context)
                final_price = final_price.add(surcharge)

        return final_price
