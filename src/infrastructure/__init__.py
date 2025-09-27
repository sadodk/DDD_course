"""Infrastructure layer package.

The infrastructure layer contains concrete implementations of domain interfaces,
external service adapters, and technical concerns like persistence, messaging, etc.

This layer depends on the domain layer but the domain layer does not depend on this layer.
"""

from .repositories import InMemoryVisitorRepository, InMemoryVisitRepository

__all__ = ["InMemoryVisitorRepository", "InMemoryVisitRepository"]
