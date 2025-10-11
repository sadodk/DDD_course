# Domain-Driven Design in Python Workshop

A comprehensive implementation of Domain-Driven Design principles in Python, featuring a waste management pricing system with domain events for automatic invoice generation.

## 🎯 Overview

This project demonstrates clean architecture using Domain-Driven Design patterns:

- **Domain Layer**: Pure business logic with entities, value objects, and business rules
- **Application Layer**: Orchestration services with domain events integration
- **Infrastructure Layer**: Repositories, external API clients, and data persistence
- **Anti-Corruption Layers**: Protection from external service changes

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry 1.8.0+ (https://python-poetry.org)

### Installation & Running

```bash
# Install dependencies
poetry install

# Run the application
poetry run flask --app src/application/main.py run --debug

# Run tests
poetry run pytest

# Code quality checks
poetry run ruff check .
poetry run ruff format .
poetry run mypy src tests
```

## 📁 Project Structure

```
src/
├── 🏛️ domain/                    ← Pure Business Logic
│   ├── entities/                 • Visit, Visitor, Business aggregates
│   ├── values/                   • Price, DroppedFraction value objects
│   ├── business_rules/           • Pricing rules and validation logic
│   ├── services/                 • Domain services (PricingService)
│   ├── repositories/             • Repository interfaces
│   └── events/                   • Domain events infrastructure
│
├── 🎯 application/               ← Application Layer
│   ├── services/                 • PriceCalculator, InvoiceEventHandler
│   ├── adapters/                 • Anti-Corruption Layers
│   ├── external/                 • External API clients
│   ├── dependency_injection.py   • DI Container
│   ├── routes.py                 • HTTP endpoints
│   └── main.py                   • Flask app bootstrap
│
├── 🔧 infrastructure/            ← Infrastructure Layer
│   └── repositories/             • InMemory implementations
│
└── 🧪 tests/                     ← Test Suite
    ├── domain/                   • Domain logic tests
    ├── application/              • Application service tests
    ├── infrastructure/           • Repository tests
    └── integration/              • End-to-end tests
```

## 🏗️ Architecture Deep Dive

### Domain Layer - Pure Business Logic

#### Entities & Aggregates

- **Visit**: Aggregate root containing waste disposal visit data
- **Visitor**: Entity representing customers (individual/business)
- **Business**: Aggregate for business customer groupings

#### Value Objects

- **Price**: Immutable monetary values with currency
- **DroppedFraction**: Waste disposal data with business calculations
- **Weight**: Type-safe weight measurements

#### Business Rules Engine

```python
# Before: Hardcoded rates
def price(self, city, customer_type):
    # 40+ lines of hardcoded rate tables...

# After: Business rule objects
def price(self, city, customer_type):
    context = PricingContext(customer_type=customer_type, city=city)
    engine = PricingRuleEngine()
    return engine.calculate_price(self, context)
```

**Available Pricing Rules**:

- `PinevillePricingRule`: Special rates for Pineville
- `OakCityPricingRule`: Oak City specific pricing
- `BusinessCustomerDiscountRule`: Business customer discounts
- `DefaultPricingRule`: Fallback pricing

### Application Layer - Orchestration

#### Application Services

```python
class PriceCalculator:
    """Orchestrates price calculation workflow"""

    def calculate_price(self, visit_data: Dict[str, Any]) -> PriceResponse:
        # 1. Fetch visitor data
        # 2. Create domain entities
        # 3. Calculate price using domain services
        # 4. Emit domain events
        # 5. Return response
```

#### Folder Organization by Purpose

| Folder      | Purpose                      | Pattern                 |
| ----------- | ---------------------------- | ----------------------- |
| `services/` | Orchestration & Coordination | Application Service     |
| `adapters/` | Translation Layer            | Anti-Corruption Layer   |
| `external/` | Outbound Communication       | External Service Client |

### Domain Events System

#### Event-Driven Invoice Generation

```
HTTP Request → PriceCalculator → Domain Events → InvoiceEventHandler → External API
```

**Flow**:

1. **Price Calculated** → Emit `PriceCalculatedEvent`
2. **Event Dispatcher** → Notify all subscribers
3. **Invoice Handler** → Check if business customer
4. **Invoice Service** → Send HTTP POST to external API

#### Components

**Domain Events**:

```python
@dataclass(frozen=True)
class PriceCalculatedEvent:
    visitor_id: str
    visit_id: str
    calculated_price: Price
    customer_type: str
    customer_email: Optional[str]
    occurred_at: datetime

    def is_business_customer(self) -> bool:
        return self.customer_type == "business"
```

**Event Dispatcher** (Observer Pattern):

```python
class InMemoryEventDispatcher:
    def subscribe(self, subscriber: EventSubscriber):
        self._subscribers.append(subscriber)

    def dispatch(self, event: DomainEvent):
        for subscriber in self._subscribers:
            subscriber.handle(event)
```

**Invoice Event Handler**:

```python
class InvoiceEventHandler:
    def handle(self, event: DomainEvent):
        if isinstance(event, PriceCalculatedEvent):
            if event.is_business_customer() and event.customer_email:
                self.invoice_service.send_invoice(...)
```

## 🎓 Domain-Driven Design Patterns

### 1. **Entities**

- **Identity**: Unique identifiers define equality
- **Mutability**: Attributes can change while maintaining identity
- **Business Logic**: Contains domain methods, not just data
- **Invariants**: Business rules enforced at creation/modification

### 2. **Value Objects**

- **Immutability**: Cannot be changed after creation
- **Equality by Value**: Two objects with same values are equal
- **Self-Validation**: Enforce constraints in constructor
- **Side-Effect Free**: Methods don't modify state

### 3. **Aggregates**

- **Consistency Boundary**: Maintain business invariants
- **Root Entity**: Single entry point for modifications
- **Transaction Boundary**: Changes committed as unit

### 4. **Domain Services**

- **Stateless**: No internal state
- **Domain Logic**: Business operations that don't fit entities
- **Coordination**: Orchestrate between multiple domain objects

### 5. **Repository Pattern**

- **Abstraction**: Hide data access details
- **Domain Interface**: Defined in domain layer
- **Infrastructure Implementation**: Concrete implementations
- **Collection-Like**: Query domain objects naturally

### 6. **Anti-Corruption Layer**

- **Translation**: Convert external DTOs to domain entities
- **Protection**: Shield domain from external changes
- **Adaptation**: Handle external service differences

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ HTTP Request (routes.py)                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Application Service (PriceCalculator)                       │
│ • Orchestrates workflow                                     │
│ • No business logic                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Anti-Corruption Layer (VisitorAdapter)                     │
│ • Translates external DTOs                                 │
│ • Protects domain                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Domain Layer (Entities, Services, Rules)                   │
│ • Pure business logic                                       │
│ • No external dependencies                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Domain Events (PriceCalculatedEvent)                       │
│ • Decouple side effects                                     │
│ • Enable cross-cutting concerns                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure (Repositories, External APIs)               │
│ • Data persistence                                          │
│ • External integrations                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Testing Strategy

### Test Organization

- **Unit Tests**: Domain logic in isolation
- **Integration Tests**: Component interaction
- **End-to-End Tests**: Complete workflow validation

### Educational Test Example

```python
def test_complete_event_flow_with_real_code():
    """🎓 Shows real domain events flow with explanatory output"""

    # Real components (no mocks except HTTP)
    dispatcher = InMemoryEventDispatcher()
    invoice_service = InvoiceService(...)
    invoice_handler = InvoiceEventHandler(invoice_service)

    # Wire components
    dispatcher.subscribe(invoice_handler.handle)

    # Create and dispatch event
    event = PriceCalculatedEvent(...)
    dispatcher.dispatch(event)

    # Verify invoice sent automatically
    assert invoice_sent_successfully
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test with detailed output
poetry run pytest tests/integration/test_domain_events_and_invoicing.py -v -s

# Run with coverage
poetry run pytest --cov=src
```

## 🔧 Configuration & Dependencies

### Dependency Injection

```python
class ApplicationContext:
    def __init__(self):
        # Repositories
        self.visit_repository = InMemoryVisitRepository()
        self.visitor_repository = InMemoryVisitorRepository()

        # Domain Services
        self.pricing_service = PricingService(...)

        # Event Infrastructure
        self.event_dispatcher = InMemoryEventDispatcher()
        self.invoice_service = InvoiceService(...)
        self.invoice_handler = InvoiceEventHandler(...)

        # Wire event handlers
        self.event_dispatcher.subscribe(self.invoice_handler.handle)
```

### External Integrations

- **Visitor API**: Fetch customer information
- **Invoice API**: Send invoices to business customers
- **Error Handling**: Graceful degradation and logging

## 📚 Key Learnings

### 1. **Separation of Concerns**

- Domain logic isolated from infrastructure
- Application services coordinate without business logic
- External concerns handled at boundaries

### 2. **Dependency Inversion**

- Domain defines interfaces
- Infrastructure implements details
- Dependencies point inward

### 3. **Event-Driven Architecture**

- Domain events enable loose coupling
- Cross-cutting concerns via event handlers
- Scalable and maintainable design

### 4. **Testability**

- Pure domain logic easy to test
- Infrastructure can be mocked
- Clear component boundaries

## 🎯 Business Rules Implemented

### Pricing Rules

1. **Pineville Special Rates**: Custom pricing for Pineville customers
2. **Oak City Exemptions**: Specific exemptions for Oak City
3. **Business Discounts**: Automatic discounts for business customers
4. **Default Fallback**: Standard pricing when no special rules apply

### Invoice Rules

1. **Business Only**: Only business customers receive invoices
2. **Email Required**: Must have valid email address
3. **Automatic Sending**: Triggered by price calculation events
4. **Error Isolation**: Failed invoice doesn't break price calculation

## 🔄 Extension Points

### Adding New Business Rules

```python
class NewCityPricingRule(PricingRule):
    def can_apply(self, context: PricingContext) -> bool:
        return context.city == "NewCity"

    def calculate_price(self, dropped_fraction: DroppedFraction, context: PricingContext) -> Price:
        # Custom pricing logic
        pass
```

### Adding New Event Handlers

```python
class AnalyticsEventHandler:
    def handle(self, event: DomainEvent):
        if isinstance(event, PriceCalculatedEvent):
            # Track pricing analytics
            pass
```

### Adding New External Services

```python
class EmailService:
    def send_notification(self, customer_email: str, message: str):
        # Send email notifications
        pass
```

## 🎓 Workshop Learning Objectives

1. **Domain Modeling**: Express business concepts in code
2. **Clean Architecture**: Separate concerns and dependencies
3. **Design Patterns**: Repository, Strategy, Observer patterns
4. **Event-Driven Design**: Loose coupling via domain events
5. **Testing Strategies**: Unit, integration, and end-to-end testing
6. **Refactoring**: Transform procedural code to domain-driven design

## 📖 References

- **Domain-Driven Design** by Eric Evans
- **Clean Architecture** by Robert Martin
- **Implementing Domain-Driven Design** by Vaughn Vernon
- **Python Type Hints** and **Dataclasses** documentation

---

**🎉 Happy Coding!** This project demonstrates how Domain-Driven Design principles create maintainable, testable, and business-focused software architecture.
