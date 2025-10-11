# Domain Events & Invoice Flow - Visual Explanation

## 🎯 What Problem Does This Solve?

**Problem**: Business customers need invoices after payment, but we don't want the price calculation code to know about invoicing.

**Solution**: Use Domain Events to decouple price calculation from invoice sending.

---

## 🔄 The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. HTTP Request: Calculate Price for Business Customer         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. PriceCalculator (Application Service)                       │
│     - Fetches visitor info                                      │
│     - Calculates price: €150.50                                 │
│     - Creates PriceCalculatedEvent                              │
│     - Calls: event_dispatcher.dispatch(event)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ dispatch
┌─────────────────────────────────────────────────────────────────┐
│  3. EventDispatcher (Observer Pattern)                          │
│     - Receives event                                            │
│     - Notifies ALL subscribers                                  │
│     - subscribers.forEach(subscriber => subscriber(event))      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ notify
┌─────────────────────────────────────────────────────────────────┐
│  4. InvoiceEventHandler (Subscriber)                            │
│     - Receives PriceCalculatedEvent                             │
│     - Checks: event.is_business_customer() ? ✓                  │
│     - Checks: event.customer_email exists ? ✓                   │
│     - Calls: invoice_service.send_invoice(...)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ send
┌─────────────────────────────────────────────────────────────────┐
│  5. InvoiceService (Infrastructure)                             │
│     POST https://ddd-in-language.aardling.eu/api/invoice        │
│     {                                                            │
│       "email": "business@example.com",                          │
│       "invoice_amount": 150.50,                                 │
│       "invoice_currency": "EUR"                                 │
│     }                                                            │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. ✅ Invoice Delivered!                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Responsibilities

### 1. PriceCalculatedEvent (Domain Layer)

```python
@dataclass(frozen=True)
class PriceCalculatedEvent(DomainEvent):
    visitor_id: str
    visit_id: str
    calculated_price: Price
    customer_type: str
    customer_email: Optional[str]
    customer_city: Optional[str]
    occurred_at: datetime
```

**Responsibility**: Capture what happened in the domain  
**Why immutable**: Events are facts - they can't be changed  
**Why in domain layer**: It represents a business event, not infrastructure

---

### 2. EventDispatcher (Domain Layer)

```python
class InMemoryEventDispatcher(EventDispatcher):
    def __init__(self):
        self._subscribers: List[EventSubscriber] = []

    def subscribe(self, subscriber: EventSubscriber):
        self._subscribers.append(subscriber)

    def dispatch(self, event: DomainEvent):
        for subscriber in self._subscribers:
            subscriber(event)
```

**Responsibility**: Notify all subscribers when events occur  
**Pattern**: Observer Pattern / Pub-Sub  
**Why in domain layer**: It's a domain concept (events are domain events)

---

### 3. InvoiceEventHandler (Application Layer)

```python
class InvoiceEventHandler:
    def __init__(self, invoice_service: InvoiceService):
        self.invoice_service = invoice_service

    def handle(self, event: DomainEvent):
        # Filter: only process PriceCalculatedEvent
        if not isinstance(event, PriceCalculatedEvent):
            return

        # Filter: only business customers
        if not event.is_business_customer():
            return

        # Validate: must have email
        if not event.customer_email:
            return

        # Action: send invoice
        self.invoice_service.send_invoice(...)
```

**Responsibility**: React to domain events and trigger infrastructure actions  
**Pattern**: Event Subscriber  
**Why in application layer**: It coordinates between domain and infrastructure

---

### 4. InvoiceService (Application/External Layer)

```python
class InvoiceService:
    def send_invoice(self, invoice_request: InvoiceRequest):
        response = requests.post(
            f"{self.base_url}/api/invoice",
            json={...},
            headers={...}
        )
        return response.status_code == 200
```

**Responsibility**: Send HTTP POST to external invoice API  
**Pattern**: External Service Client  
**Why in external layer**: It's pure infrastructure (HTTP calls)

---

## 🎭 Observer Pattern Explained

The Observer Pattern allows **one-to-many** dependency:

- **One** event can trigger **many** handlers
- Handlers don't know about each other
- Easy to add new handlers without changing existing code

```
        ┌──────────────────┐
        │  EventDispatcher │
        │   (Observable)   │
        └────────┬─────────┘
                 │
         ┌───────┼───────┐
         │       │       │
         ↓       ↓       ↓
    ┌────────┐ ┌────────┐ ┌────────┐
    │Invoice │ │Analytics│ │Logging │
    │Handler │ │Handler  │ │Handler │
    └────────┘ └────────┘ └────────┘
    (Observer) (Observer)  (Observer)
```

**Key Benefits**:

1. **Decoupling**: PriceCalculator doesn't know about handlers
2. **Extensibility**: Add new handlers without modifying code
3. **Single Responsibility**: Each handler does one thing

---

## 📊 Sequence Diagram

```
User          Routes    PriceCalculator  EventDispatcher  InvoiceHandler  InvoiceService  API
 │               │            │                 │               │              │           │
 │─POST /price─>│            │                 │               │              │           │
 │               │            │                 │               │              │           │
 │               │─calculate─>│                 │               │              │           │
 │               │            │                 │               │              │           │
 │               │            │───dispatch(evt)─>│              │              │           │
 │               │            │                 │               │              │           │
 │               │            │                 │─notify(evt)──>│              │           │
 │               │            │                 │               │              │           │
 │               │            │                 │               │─send_invoice─>│          │
 │               │            │                 │               │              │           │
 │               │            │                 │               │              │─POST─────>│
 │               │            │                 │               │              │           │
 │               │            │                 │               │              │<─200 OK──│
 │               │            │                 │               │              │           │
 │               │<───price───│                 │               │              │           │
 │               │            │                 │               │              │           │
 │<─200 + price─│            │                 │               │              │           │
 │               │            │                 │               │              │           │
```

---

## 🧪 How to Test This

### Unit Test: InvoiceEventHandler in Isolation

```python
def test_invoice_handler_filters_correctly():
    # Mock the service
    mock_service = Mock()
    handler = InvoiceEventHandler(mock_service)

    # Create event for individual (not business)
    event = PriceCalculatedEvent(
        customer_type="individual",  # Not business!
        ...
    )

    # Handle event
    handler.handle(event)

    # Assert: service was NOT called
    mock_service.send_invoice.assert_not_called()
```

### Integration Test: Complete Flow

```python
def test_complete_flow():
    # Setup all real components (except HTTP)
    mock_service = Mock()
    handler = InvoiceEventHandler(mock_service)
    dispatcher = InMemoryEventDispatcher()
    dispatcher.subscribe(handler.handle)

    # Create and dispatch event
    event = PriceCalculatedEvent(
        customer_type="business",
        customer_email="test@example.com",
        ...
    )
    dispatcher.dispatch(event)

    # Assert: invoice was sent
    mock_service.send_invoice.assert_called_once()
```

---

## 🎨 Design Benefits

### 1. **Open/Closed Principle**

✅ Open for extension (add new handlers)  
✅ Closed for modification (don't change PriceCalculator)

```python
# Adding analytics is EASY - no changes to existing code!
analytics_handler = AnalyticsEventHandler()
event_dispatcher.subscribe(analytics_handler.handle)
```

### 2. **Single Responsibility Principle**

- `PriceCalculator`: Calculate prices
- `InvoiceEventHandler`: Send invoices
- `EventDispatcher`: Notify subscribers

### 3. **Dependency Inversion Principle**

- PriceCalculator depends on `EventDispatcher` (abstraction)
- InvoiceEventHandler depends on `InvoiceService` (abstraction)
- Both depend on abstractions, not concrete implementations

---

## 🚀 Future Extensions

Want to add analytics? Easy!

```python
class AnalyticsEventHandler:
    def handle(self, event: DomainEvent):
        if isinstance(event, PriceCalculatedEvent):
            # Track metrics
            analytics.track(event.visitor_id, event.calculated_price)

# Wire it up
dispatcher.subscribe(analytics_handler.handle)
```

Want to add logging? Easy!

```python
class LoggingEventHandler:
    def handle(self, event: DomainEvent):
        logger.info(f"Event occurred: {event}")

# Wire it up
dispatcher.subscribe(logging_handler.handle)
```

**No changes needed to**:

- PriceCalculator ✓
- InvoiceEventHandler ✓
- EventDispatcher ✓

---

## 🎓 Key Takeaways

1. **Domain Events** represent things that happened in the domain
2. **EventDispatcher** implements the Observer Pattern
3. **Event Handlers** react to events (application layer)
4. **Decoupling** allows easy extension without modification
5. **Testing** is easier because components are isolated

---

## 📚 Further Reading

- **Event-Driven Architecture**: Martin Fowler
- **Domain Events**: Eric Evans (DDD Blue Book)
- **Observer Pattern**: Gang of Four Design Patterns
- **Command Query Responsibility Segregation (CQRS)**: Greg Young

---

**Run the test to see it in action**:

```bash
poetry run pytest tests/integration/test_domain_events_and_invoicing.py -v -s
```

The `-s` flag shows print statements so you can see the flow explained! 🎯
