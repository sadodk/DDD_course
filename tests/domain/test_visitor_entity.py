"""Tests for Visitor entity."""

import pytest
from domain.entities.visitor import Visitor
from domain.types import PersonId, CardId, EmailAddress


class TestVisitorEntity:
    def test_visitor_creation_with_valid_data(self):
        """Test creating a visitor with valid data."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
            email=EmailAddress("user@example.com"),
        )

        assert visitor.id == PersonId("user123")
        assert visitor.city == "Oak City"
        assert visitor.card_id == CardId("CARD001")
        assert visitor.email == EmailAddress("user@example.com")

    def test_visitor_creation_without_email_uses_default(self):
        """Test creating a visitor without email uses empty default."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        assert visitor.email == EmailAddress("")

    def test_visitor_requires_valid_id(self):
        """Test that visitor must have a valid ID."""
        with pytest.raises(ValueError, match="Visitor must have a valid ID"):
            Visitor(
                id=PersonId(""),  # Empty ID should fail
                type="individual",
                address="123 Main St",
                city="Oak City",
                card_id=CardId("CARD001"),
            )

    def test_visitor_requires_city(self):
        """Test that visitor must have a city."""
        with pytest.raises(ValueError, match="Visitor must have a city"):
            Visitor(
                id=PersonId("user123"),
                type="individual",
                address="123 Main St",
                city="",  # Empty city should fail
                card_id=CardId("CARD001"),
            )

    def test_visitor_requires_card_id(self):
        """Test that visitor must have a card ID."""
        with pytest.raises(ValueError, match="Visitor must have a card ID"):
            Visitor(
                id=PersonId("user123"),
                type="individual",
                address="123 Main St",
                city="Oak City",
                card_id=CardId(""),  # Empty card ID should fail
            )

    def test_visitor_equality_based_on_identity(self):
        """Test that visitor equality is based on identity (ID), not attributes."""
        visitor1 = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        visitor2 = Visitor(
            id=PersonId("user123"),  # Same ID
            type="business",  # Different attributes
            address="456 Other St",
            city="Pineville",
            card_id=CardId("CARD002"),
        )

        visitor3 = Visitor(
            id=PersonId("user456"),  # Different ID
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        # Same ID = equal entities
        assert visitor1 == visitor2

        # Different ID = not equal
        assert visitor1 != visitor3
        assert visitor2 != visitor3

    def test_visitor_hash_based_on_identity(self):
        """Test that visitor hash is based on identity for use in sets/dicts."""
        visitor1 = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        visitor2 = Visitor(
            id=PersonId("user123"),  # Same ID
            type="business",  # Different attributes
            address="456 Other St",
            city="Pineville",
            card_id=CardId("CARD002"),
        )

        # Same ID should have same hash
        assert hash(visitor1) == hash(visitor2)

        # Should work in sets
        visitor_set = {visitor1, visitor2}
        assert len(visitor_set) == 1  # Only one unique visitor

    def test_update_email_with_valid_email(self):
        """Test updating visitor email with valid email."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        visitor.update_email("new@example.com")
        assert visitor.email == EmailAddress("new@example.com")

    def test_update_email_with_invalid_email_fails(self):
        """Test that updating with invalid email fails."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            visitor.update_email("invalid-email")

        with pytest.raises(ValueError, match="Invalid email format"):
            visitor.update_email("")

    def test_update_address(self):
        """Test updating visitor address and city."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        visitor.update_address("456 New St", "Pineville")
        assert visitor.address == "456 New St"
        assert visitor.city == "Pineville"

    def test_update_address_with_empty_values_fails(self):
        """Test that updating address with empty values fails."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        with pytest.raises(ValueError, match="Address and city cannot be empty"):
            visitor.update_address("", "Pineville")

        with pytest.raises(ValueError, match="Address and city cannot be empty"):
            visitor.update_address("456 New St", "")

    def test_is_from_city(self):
        """Test checking if visitor is from a specific city."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        assert visitor.is_from_city("Oak City") is True
        assert visitor.is_from_city("oak city") is True  # Case insensitive
        assert visitor.is_from_city("OAK CITY") is True
        assert visitor.is_from_city("Pineville") is False

    def test_visitor_string_representations(self):
        """Test string representations of visitor."""
        visitor = Visitor(
            id=PersonId("user123"),
            type="individual",
            address="123 Main St",
            city="Oak City",
            card_id=CardId("CARD001"),
        )

        assert "user123" in str(visitor)
        assert "Oak City" in str(visitor)
        assert "individual" in repr(visitor)
