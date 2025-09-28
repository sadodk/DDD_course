# Notes

## Engine

The engine has a list business rules which is a list of type PricingRule (interface).

```py
    def _get_default_rules(self) -> List[PricingRule]:
        """Get the default set of pricing rules."""
        return [
            PinevillePricingRule(),
            OakCityPricingRule(),
            BusinessCustomerDiscountRule(),
            DefaultPricingRule(),  # Always add fallback rule last
        ]
```

It has a findapplicable rule method which uses a can apply method using PriceContext type to find the appropriate business rules for the specific visit.

Finally the engine delegates the calculation of the price to the specific rule object. So every Pricing Rule contains its rule and a calculation price method and a way to check if the rule applies to a specific visit using bool.
