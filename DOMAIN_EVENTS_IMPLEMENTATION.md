# Domain Events Implementation - Invoice Sending

## Overview

We've successfully implemented a domain events system that automatically sends invoices to business customers after their price is calculated. This uses the **Observer Pattern** to decouple the price calculation logic from invoice sending.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          HTTP Request (Calculate Price)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  PriceCalculator (Application Service)                       │
│  1. Calculates price                                         │
│  2. Emits PriceCalculatedEvent                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ dispatches event
┌─────────────────────────────────────────────────────────────┐
│  EventDispatcher                                             │
│  - Notifies all subscribers                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ notifies
┌─────────────────────────────────────────────────────────────┐
│  InvoiceEventHandler                                         │
│  - Checks if business customer                              │
│  - Sends invoice via HTTP POST                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  InvoiceService                                              │
│  - POST to https://ddd-in-language.aardling.eu/api/invoice  │
└─────────────────────────────────────────────────────────────┘
```

## Components Created

### 1. Domain Events Infrastructure

#### `domain/events/domain_event.py`

- **Base class** for all domain events
- Immutable (frozen=True)
- Automatically tracks when the event occurred

#### `domain/events/event_dispatcher.py`

- **EventDispatcher interface** - defines how to subscribe and dispatch events
- **InMemoryEventDispatcher** - synchronous implementation
- Subscribers are notified when events are dispatched

### 2. Price Calculated Event

#### `domain/events/price_calculated_event.py`

- **PriceCalculatedEvent** - emitted when a price is calculated
- Contains:
  - visitor_id, visit_id
  - calculated_price (Price value object)
  - customer_type ("business" or "individual")
  - customer_email
  - customer_city
  - occurred_at timestamp

### 3. Invoice Infrastructure

#### `application/invoice_service.py`

- **InvoiceService** - sends HTTP POST to invoice API
- **InvoiceRequest** - DTO for invoice data
- Handles:
  - Authentication headers
  - Error handling
  - Logging

#### `application/invoice_event_handler.py`

- **InvoiceEventHandler** - subscribes to domain events
- Logic:
  1. Filter: only processes `PriceCalculatedEvent`
  2. Filter: only for business customers
  3. Validation: ensures email exists
  4. Action: sends invoice via InvoiceService

### 4. Integration

#### `application/dependency_injection.py`

Updated to wire up:

- EventDispatcher (InMemoryEventDispatcher)
- InvoiceService (with API credentials)
- InvoiceEventHandler (subscribes to events)
- PriceCalculator (receives EventDispatcher)

#### `application/services/price_calculation_service.py`

Updated to:

- Accept EventDispatcher in constructor
- Create `PriceCalculatedEvent` after calculation
- Dispatch event to all subscribers

## Key Benefits of This Architecture

### 1. **Decoupling**

- PriceCalculator doesn't know about invoicing
- Adding new reactions to price calculation is easy (just add new subscribers)
- Domain logic stays pure

### 2. **Single Responsibility**

- PriceCalculator: calculates prices
- InvoiceEventHandler: sends invoices
- InvoiceService: HTTP communication

### 3. **Open/Closed Principle**

- Can add new event handlers without modifying existing code
- Example: Add analytics tracking by creating `AnalyticsEventHandler`

### 4. **Testability**

- Can test price calculation without HTTP calls
- Can test invoice sending in isolation
- Can mock EventDispatcher for unit tests

## How It Works - Flow

1. **HTTP Request arrives** at `/calculatePrice` endpoint
2. **Routes** calls `app.price_calculator.calculate_price()`
3. **PriceCalculator**:
   - Fetches visitor info
   - Calculates price using domain services
   - Creates `PriceCalculatedEvent`
   - Dispatches event
4. **EventDispatcher** notifies all subscribers
5. **InvoiceEventHandler**:
   - Receives event
   - Checks if business customer with email
   - Calls `invoice_service.send_invoice()`
6. **InvoiceService**:
   - Sends HTTP POST to invoice API
   - Logs result

## API Endpoint Used

```http
POST https://ddd-in-language.aardling.eu/api/invoice
Content-Type: application/json
x-auth-token: fZg124e-cuHb
x-workshop-id: DDD in Your Language - 2025 Sept-Oct

{
  "email": "business@example.com",
  "invoice_amount": 150.50,
  "invoice_currency": "EUR"
}
```

## Testing

To test the implementation:

1. **Start the application**:

   ```bash
   poetry run flask --app src/application/main.py run --debug --port 8080
   ```

2. **Send a test request** with a business customer:

   ```bash
   curl -X POST http://localhost:8080/calculatePrice \
     -H "Content-Type: application/json" \
     -d '{
       "person_id": "business-customer-id",
       "visit_id": "visit-123",
       "date": "2025-10-11T10:00:00Z",
       "dropped_fractions": [
         {
           "fraction_type": "construction_waste",
           "amount_dropped": 500
         }
       ]
     }'
   ```

3. **Check logs** - you should see:
   - "Sending invoice to [email] for [amount] [currency]"
   - "Invoice sent successfully"

## Future Enhancements

1. **Async Event Processing**

   - Replace InMemoryEventDispatcher with message queue (RabbitMQ, Kafka)
   - Process events asynchronously

2. **Event Sourcing**

   - Store all events in an event store
   - Replay events to rebuild state

3. **Additional Handlers**

   - Analytics tracking
   - Email notifications to customers
   - Audit logging
   - Metrics collection

4. **Retry Logic**

   - Add retry mechanism for failed invoice sends
   - Dead letter queue for permanently failed events

5. **Event Versioning**
   - Support multiple versions of events
   - Handle schema evolution

## Pattern Summary

This implementation demonstrates several DDD patterns:

- **Domain Events**: Capture significant domain occurrences
- **Observer Pattern**: Decouple event producers from consumers
- **Dependency Injection**: Wire up components cleanly
- **Anti-Corruption Layer**: Protect domain from external APIs
- **Application Services**: Orchestrate domain logic without containing it

---

**Status**: ✅ Complete and ready for testing
