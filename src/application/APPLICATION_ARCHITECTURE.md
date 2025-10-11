# Application Layer Architecture

This folder is organized by **purpose** to create a clear mental model of responsibilities and dependencies.

## 📁 Folder Structure

```
application/
├── 📁 adapters/                     ← Anti-Corruption Layers
│   └── visitor_adapter.py           • Translates external DTOs → Domain entities
│                                    • Protects domain from external changes
│
├── 📁 external/                     ← External API Clients
│   ├── visitor_api_client.py        • HTTP client for visitor API
│   └── invoice_api_client.py        • HTTP client for invoice API
│
├── 📁 services/                     ← Application Services (Orchestration)
│   ├── price_calculation_service.py • Coordinates pricing workflow
│   └── invoice_event_handler.py     • Reacts to domain events
│
├── 🔧 dependency_injection.py       ← Dependency Injection Container
│                                    • Wires up all components
│
├── 🌐 routes.py                     ← HTTP Endpoints (Flask)
│                                    • Entry point for web requests
│
└── 🚀 main.py                       ← Flask Application Bootstrap
```

## 🎯 Mental Model: Responsibility Segregation

### **adapters/** - "Translation Layer"

**Purpose**: Protect the domain from external systems  
**Pattern**: Anti-Corruption Layer  
**Example**: `visitor_adapter.py`

- Converts external `VisitorInfo` DTO → domain `Visitor` entity
- Groups business visitors by address
- Caches external data

### **external/** - "Outbound Communication"

**Purpose**: Make HTTP calls to external APIs  
**Pattern**: External Service Integration  
**Examples**:

- `visitor_api_client.py` - Fetches visitor data
- `invoice_api_client.py` - Sends invoices

### **services/** - "Orchestration & Coordination"

**Purpose**: Coordinate domain logic without containing it  
**Pattern**: Application Service  
**Examples**:

- `price_calculation_service.py` - Orchestrates price calculation workflow
- `invoice_event_handler.py` - Subscribes to events and triggers actions

### **dependency_injection.py** - "Wiring Hub"

**Purpose**: Create and wire all dependencies  
**Pattern**: Dependency Injection Container  
**Wires up**:

- Repositories
- Domain services
- Application services
- Event handlers
- External clients

### **routes.py** - "HTTP Interface"

**Purpose**: HTTP endpoint definitions  
**Pattern**: Controller/Routes  
**Responsibilities**:

- Parse HTTP requests
- Call application services
- Return HTTP responses

### **main.py** - "Bootstrap"

**Purpose**: Flask app initialization  
**Pattern**: Application Entry Point

---

## 🔄 Data Flow

```
HTTP Request
    ↓
routes.py (parses request)
    ↓
services/price_calculation_service.py (orchestrates)
    ├→ external/visitor_api_client.py (fetch data)
    ├→ adapters/visitor_adapter.py (translate to domain)
    ├→ Domain Services (business logic)
    └→ Event Dispatcher (emit events)
         ↓
    services/invoice_event_handler.py (reacts to event)
         ↓
    external/invoice_api_client.py (send invoice)
```

---

## 📋 File-by-File Breakdown

### adapters/visitor_adapter.py

**Role**: Anti-Corruption Layer  
**Domain Usage**:

- `domain.entities.visitor.Visitor` - Domain entity
- `domain.entities.business.Business` - Aggregate root
- `domain.types.*` - Domain types

**Purpose**: Protects domain from external service changes

---

### external/visitor_api_client.py

**Role**: External HTTP Client  
**Domain Usage**: ❌ None (pure infrastructure)

**Purpose**: Fetches visitor data from external API

---

### external/invoice_api_client.py

**Role**: External HTTP Client  
**Domain Usage**: ❌ None (pure infrastructure)

**Purpose**: Sends invoices via HTTP POST

---

### services/price_calculation_service.py

**Role**: Application Service (Orchestrator)  
**Domain Usage**:

- `domain.entities.visit.Visit` - Aggregate root
- `domain.entities.visitor.Visitor` - Entity
- `domain.services.pricing_service.PricingService` - Domain service
- `domain.repositories.*` - Repository interfaces
- `domain.values.*` - Value objects
- `domain.events.price_calculated_event.PriceCalculatedEvent` - Domain event

**Purpose**: Orchestrates price calculation workflow and emits events

---

### services/invoice_event_handler.py

**Role**: Event Subscriber  
**Domain Usage**:

- `domain.events.domain_event.DomainEvent` - Event base class
- `domain.events.price_calculated_event.PriceCalculatedEvent` - Specific event

**Purpose**: Listens to price events and sends invoices for business customers

---

### dependency_injection.py

**Role**: Dependency Injection Container  
**Domain Usage**:

- `domain.business_rules.*` - Business rules
- `domain.services.pricing_service.PricingService` - Domain service
- `domain.events.event_dispatcher.InMemoryEventDispatcher` - Event infrastructure

**Purpose**: Wires up all components and their dependencies

---

### routes.py

**Role**: HTTP Controller  
**Domain Usage**: ⚠️ Indirect only (through application services)

**Purpose**: HTTP endpoint definitions

---

### main.py

**Role**: Application Bootstrap  
**Domain Usage**: ❌ None

**Purpose**: Flask app initialization

---

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**

Each folder has a clear, single responsibility:

- `adapters/` = translation
- `external/` = HTTP clients
- `services/` = orchestration

### 2. **Dependency Direction**

```
routes.py
   ↓
services/ (application logic)
   ↓
domain/ (business logic)
   ↑
adapters/ (translation)
   ↑
external/ (HTTP clients)
```

### 3. **Testability**

- `external/` can be mocked
- `services/` can be tested without HTTP
- Domain logic is pure and testable

### 4. **Domain Protection**

- `routes.py` doesn't import domain directly
- `external/` clients are pure infrastructure
- `adapters/` protect domain from external changes

---

## 🎓 Pattern Summary

| Folder                    | Pattern                 | Purpose                     |
| ------------------------- | ----------------------- | --------------------------- |
| `adapters/`               | Anti-Corruption Layer   | Translate external → domain |
| `external/`               | External Service Client | Make HTTP calls             |
| `services/`               | Application Service     | Orchestrate workflows       |
| `dependency_injection.py` | DI Container            | Wire dependencies           |
| `routes.py`               | Controller              | Handle HTTP                 |
| `main.py`                 | Bootstrap               | Start app                   |

---

**Key Insight**: The folder structure makes the **flow of data and responsibility** immediately clear. You can understand the system's architecture just by looking at the folder names! 🎯
