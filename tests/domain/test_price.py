from domain.price import Price, Currency
import pytest


def test_price_should_be_positive():
    with pytest.raises(ValueError):
        Price(-1, Currency.EUR)


def test_price_with_invalid_currency():
    with pytest.raises(ValueError):
        Price(1, "UR")


def test_with_valid_price():
    assert Price(1, Currency.EUR)
