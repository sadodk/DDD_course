┌─────────────────────────────────────────────────────────────┐
│ HTTP Layer (routes.py) │
│ No direct domain dependency │
└────────────────────────────┬────────────────────────────────┘
│
↓
┌─────────────────────────────────────────────────────────────┐
│ Application Layer (price_calculator.py) │
│ - Orchestrates domain services and repositories │
│ - Creates domain entities from external data │
│ - Uses: Visit, Visitor, PricingService, Repositories │
└────────────────────────────┬────────────────────────────────┘
│
↓
┌─────────────────────────────────────────────────────────────┐
│ Domain Layer (domain/\*) │
│ - Pure business logic │
│ - Entities, Value Objects, Business Rules │
│ - Domain Services, Repository Interfaces │
└─────────────────────────────────────────────────────────────┘
↑
│
┌────────────────────────────┴────────────────────────────────┐
│ Anti-Corruption Layer (external_visitor_adapter.py) │
│ - Translates external DTOs to domain entities │
│ - Protects domain from external service changes │
│ - Uses: Visitor, Business, domain types │
└─────────────────────────────────────────────────────────────┘
