from domain.visit import Visit
from domain.price import Currency


def test_visit_calculate_price_with_green_waste():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": "10"}],
        person_id="person-123",
        visit_id="visit-456",
    )

    price = visit.calculate_price()

    assert price.amount == 1.0  # 10 kg * 0.1 euro/kg
    assert price.currency == Currency.EUR


def test_visit_calculate_price_with_construction_waste():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[
            {"fraction_type": "Construction waste", "amount_dropped": "10"}
        ],
        person_id="person-123",
        visit_id="visit-456",
    )

    price = visit.calculate_price()

    assert price.amount == 1.5  # 10 kg * 0.15 euro/kg
    assert price.currency == Currency.EUR


def test_visit_calculate_price_with_mixed_fractions():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[
            {"fraction_type": "Green waste", "amount_dropped": "10"},
            {"fraction_type": "Construction waste", "amount_dropped": "20"},
        ],
        person_id="person-123",
        visit_id="visit-456",
    )

    price = visit.calculate_price()

    assert price.amount == 4.0  # (10 * 0.1) + (20 * 0.15)
    assert price.currency == Currency.EUR


def test_visit_calculate_price_with_unknown_fraction():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[{"fraction_type": "Unknown waste", "amount_dropped": "10"}],
        person_id="person-123",
        visit_id="visit-456",
    )

    price = visit.calculate_price()

    assert price.amount == 0  # Unknown waste types default to 0
    assert price.currency == Currency.EUR


def test_visit_calculate_price_with_empty_fractions():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[],
        person_id="person-123",
        visit_id="visit-456",
    )

    price = visit.calculate_price()

    assert price.amount == 0
    assert price.currency == Currency.EUR


def test_visit_create_invoice():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[
            {"fraction_type": "Green waste", "amount_dropped": "10"},
            {"fraction_type": "Construction waste", "amount_dropped": "20"},
        ],
        person_id="person-123",
        visit_id="visit-456",
    )

    invoice = visit.create_invoice()

    assert invoice.price_amount == 4.0  # (10 * 0.1) + (20 * 0.15)
    assert invoice.person_id == "person-123"
    assert invoice.visit_id == "visit-456"
    assert invoice.price_currency == "EUR"


def test_visit_create_invoice_with_zero_price():
    visit = Visit(
        date="2023-09-01",
        dropped_fractions=[],
        person_id="person-123",
        visit_id="visit-456",
    )

    invoice = visit.create_invoice()

    assert invoice.price_amount == 0.0
    assert invoice.person_id == "person-123"
    assert invoice.visit_id == "visit-456"
    assert invoice.price_currency == "EUR"
