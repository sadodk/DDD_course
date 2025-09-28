# Architecture Improvement: refactored code in dropped_fraction.py

## Before(Hardcoded)

```py
def price(self, city, customer_type):
    # 40+ lines of hardcoded rate tables and logic
    default_private_rates = {"green_waste": 0.10, ...}
    city_private_rates = {"Pineville": {"green_waste": 0.10, ...}}
    # Complex nested conditionals...
```

## After (Business rule objects)

```py
def price(self, city, customer_type):
    context = PricingContext(customer_type=customer_type, city=city)
    engine = PricingRuleEngine()
    return engine.calculate_price(self, context)
```
