import pytest
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.price import Currency, Price
from domain.values.weight import Weight
from domain.services.pricing_service import PricingService


def test_parse_fraction_type() -> None:
    assert FractionType.from_string("Green waste")


def test_incorrect_fraction_type() -> None:
    with pytest.raises(ValueError):
        FractionType.from_string("incorrect")


def test_parse_correctly() -> None:
    assert DroppedFraction(FractionType.from_string("Green waste"), Weight(10))


def test_from_string_creation() -> None:
    """Test creating DroppedFraction from string inputs."""
    fraction = DroppedFraction.from_string("Green waste", 10)
    assert fraction.fraction_type == FractionType.GREEN_WASTE
    assert fraction.weight == Weight(10)


def test_price_for_green_waste() -> None:
    """Test pricing through domain service."""
    green_waste = DroppedFraction(FractionType.from_string("Green waste"), Weight(10))
    pricing_service = PricingService()
    price = pricing_service.calculate_price(green_waste)
    assert Price(10 * 0.1, Currency.EUR) == price


def test_price_for_construction_waste() -> None:
    """Test pricing through domain service."""
    construction_waste = DroppedFraction(
        FractionType.from_string("Construction waste"), Weight(20)
    )
    pricing_service = PricingService()
    price = pricing_service.calculate_price(construction_waste)
    assert Price(20 * 0.19, Currency.EUR) == price


def test_price_for_multiple_fractions() -> None:
    """Test total pricing through domain service."""
    construction_waste = DroppedFraction(
        FractionType.from_string("Construction waste"), Weight(20)
    )
    green_waste = DroppedFraction(FractionType.from_string("Green waste"), Weight(10))

    pricing_service = PricingService()
    total_price = pricing_service.calculate_total_price(
        [construction_waste, green_waste]
    )
    assert Price(20 * 0.19 + 10 * 0.10, Currency.EUR) == total_price
