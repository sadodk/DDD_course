from application.price_calculator import (
    PriceCalculator,
    Visit,
)


def test_calculate_price():
    calculator = PriceCalculator()
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[
            {"amount_dropped": 10, "fraction_type": "Green waste"},
            {"amount_dropped": 20, "fraction_type": "Construction waste"},
        ],
        person_id="person-123",
        visit_id="visit-456",
    )
    invoice = calculator.calculate(visit)
    assert invoice.price_amount == 4.0  # Assuming a fixed price for simplicity
    assert invoice.person_id == "person-123"
    assert invoice.visit_id == "visit-456"
    assert invoice.price_currency == "EUR"
