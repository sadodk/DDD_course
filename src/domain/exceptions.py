"""Domain exceptions - Business and repository related exceptions."""

from typing import Optional


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class RepositoryException(DomainException):
    """Base exception for repository operations."""

    pass


class VisitorNotFoundException(RepositoryException):
    """Raised when a visitor cannot be found."""

    def __init__(self, visitor_id: str):
        super().__init__(
            f"Visitor with ID '{visitor_id}' not found", f"Visitor ID: {visitor_id}"
        )
        self.visitor_id = visitor_id


class VisitNotFoundException(RepositoryException):
    """Raised when a visit cannot be found."""

    def __init__(self, visit_id: str):
        super().__init__(
            f"Visit with ID '{visit_id}' not found", f"Visit ID: {visit_id}"
        )
        self.visit_id = visit_id


class DuplicateVisitorException(RepositoryException):
    """Raised when attempting to save a visitor that already exists."""

    def __init__(self, visitor_id: str):
        super().__init__(
            f"Visitor with ID '{visitor_id}' already exists",
            f"Visitor ID: {visitor_id}",
        )
        self.visitor_id = visitor_id


class DuplicateVisitException(RepositoryException):
    """Raised when attempting to save a visit that already exists."""

    def __init__(self, visit_id: str):
        super().__init__(
            f"Visit with ID '{visit_id}' already exists", f"Visit ID: {visit_id}"
        )
        self.visit_id = visit_id


class InvalidDateRangeException(DomainException):
    """Raised when an invalid date range is provided."""

    def __init__(self, start_date: str, end_date: str):
        super().__init__(
            f"Invalid date range: start_date '{start_date}' is after end_date '{end_date}'",
            f"Start: {start_date}, End: {end_date}",
        )
        self.start_date = start_date
        self.end_date = end_date
