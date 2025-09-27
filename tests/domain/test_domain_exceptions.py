"""Tests for domain exceptions."""

import pytest
from domain.exceptions import (
    DomainException,
    RepositoryException,
    VisitorNotFoundException,
    VisitNotFoundException,
    DuplicateVisitorException,
    DuplicateVisitException,
    InvalidDateRangeException,
)


class TestDomainExceptions:
    """Tests for domain exception classes."""

    def test_domain_exception_inheritance(self):
        """Test that domain exceptions have proper inheritance."""
        assert issubclass(RepositoryException, DomainException)
        assert issubclass(VisitorNotFoundException, RepositoryException)
        assert issubclass(VisitNotFoundException, RepositoryException)
        assert issubclass(DuplicateVisitorException, RepositoryException)
        assert issubclass(DuplicateVisitException, RepositoryException)
        assert issubclass(InvalidDateRangeException, DomainException)

    def test_domain_exception_with_details(self):
        """Test DomainException with details."""
        exception = DomainException("Test message", "Test details")

        assert str(exception) == "Test message"
        assert exception.message == "Test message"
        assert exception.details == "Test details"

    def test_domain_exception_without_details(self):
        """Test DomainException without details."""
        exception = DomainException("Test message")

        assert str(exception) == "Test message"
        assert exception.message == "Test message"
        assert exception.details is None

    def test_visitor_not_found_exception(self):
        """Test VisitorNotFoundException."""
        visitor_id = "user123"
        exception = VisitorNotFoundException(visitor_id)

        assert "user123" in str(exception)
        assert "not found" in str(exception)
        assert exception.visitor_id == visitor_id
        assert exception.details == f"Visitor ID: {visitor_id}"

    def test_visit_not_found_exception(self):
        """Test VisitNotFoundException."""
        visit_id = "visit123"
        exception = VisitNotFoundException(visit_id)

        assert "visit123" in str(exception)
        assert "not found" in str(exception)
        assert exception.visit_id == visit_id
        assert exception.details == f"Visit ID: {visit_id}"

    def test_duplicate_visitor_exception(self):
        """Test DuplicateVisitorException."""
        visitor_id = "user123"
        exception = DuplicateVisitorException(visitor_id)

        assert "user123" in str(exception)
        assert "already exists" in str(exception)
        assert exception.visitor_id == visitor_id
        assert exception.details == f"Visitor ID: {visitor_id}"

    def test_duplicate_visit_exception(self):
        """Test DuplicateVisitException."""
        visit_id = "visit123"
        exception = DuplicateVisitException(visit_id)

        assert "visit123" in str(exception)
        assert "already exists" in str(exception)
        assert exception.visit_id == visit_id
        assert exception.details == f"Visit ID: {visit_id}"

    def test_invalid_date_range_exception(self):
        """Test InvalidDateRangeException."""
        start_date = "2025-09-20"
        end_date = "2025-09-15"  # End before start
        exception = InvalidDateRangeException(start_date, end_date)

        assert start_date in str(exception)
        assert end_date in str(exception)
        assert "Invalid date range" in str(exception)
        assert exception.start_date == start_date
        assert exception.end_date == end_date
        assert exception.details is not None
        assert f"Start: {start_date}, End: {end_date}" in exception.details

    def test_exceptions_can_be_raised_and_caught(self):
        """Test that exceptions can be properly raised and caught."""

        # Test raising and catching specific exception
        with pytest.raises(VisitorNotFoundException) as exc_info:
            raise VisitorNotFoundException("user123")

        assert exc_info.value.visitor_id == "user123"

        # Test catching as base exception type
        with pytest.raises(RepositoryException):
            raise VisitorNotFoundException("user123")

        # Test catching as domain exception
        with pytest.raises(DomainException):
            raise VisitorNotFoundException("user123")
