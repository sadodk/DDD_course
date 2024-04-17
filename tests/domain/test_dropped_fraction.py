import pytest
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.price import Currency, Price
from domain.weight import Weight


def test_parse_fraction_type() -> None:
    assert FractionType.from_string("Green waste")


def test_incorrect_fraction_type() -> None:
    with pytest.raises(ValueError):
        FractionType.from_string("incorrect")


def test_parse_correctly() -> None:
    assert DroppedFraction(FractionType.from_string("Green waste"), Weight(10))


def test_price_for_green_waste() -> None:
    green_waste = DroppedFraction(FractionType.from_string("Green waste"), Weight(10))
    assert Price(10 * 0.1, Currency.EUR) == green_waste.price()


def test_price_for_construction_waste() -> None:
    construction_waste = DroppedFraction(
        FractionType.from_string("Construction waste"), Weight(20)
    )

    assert Price(20 * 0.15, Currency.EUR) == construction_waste.price()


def test_price_for_multiple_fractions() -> None:
    construction_waste = DroppedFraction(
        FractionType.from_string("Construction waste"), Weight(20)
    )
    green_waste = DroppedFraction(FractionType.from_string("Green waste"), Weight(10))

    assert Price(20 * 0.15 + 10 * 0.10, Currency.EUR) == DroppedFraction.sum(
        [construction_waste, green_waste]
    )
