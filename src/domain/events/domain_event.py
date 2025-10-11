"""Base domain event class."""

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class DomainEvent(Protocol):
    """
    Protocol for domain events.

    Domain events represent something significant that happened in the domain.
    """

    @property
    def occurred_at(self) -> datetime:
        """When the event occurred."""
        ...
