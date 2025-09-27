# Definitions

## Entity Characteristics

Identity - Each entity has a unique identifier that defines equality
Mutability - Entity attributes can change while maintaining identity
Business Logic - Entities contain business methods, not just data
Invariants - Business rules are enforced at creation and modification

## Value Object Integration

Entities aggregate value objects (DroppedFraction, Price, Weight)
Business calculations delegate to appropriate value objects
Clean separation between entities and value objects
