# Visit Request Flow Diagram

## Simple Flow Overview

```
HTTP Request → Flask Routes → Application Service → Domain Services → Domain Entities → Repository
     ↓              ↓               ↓                      ↓              ↓              ↓
JSON Data    Parse & Validate    Orchestrate         Calculate Price   Visit Entity    Store Visit
     ↓              ↓               ↓                      ↓              ↓              ↓
     └──────────────┴───────────────┴──────────────────────┴──────────────┴──────────────┘
                                                    HTTP Response ← Price Response
```

## Detailed Flow

### 1. Request Entry Point

```
POST /calculatePrice
{
  "date": "2023-07-23",
  "dropped_fractions": [
    {"amount_dropped": 83, "fraction_type": "Green waste"}
  ],
  "person_id": "visitor123",
  "visit_id": "visit1"
}
```

### 2. Application Layer Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   routes.py     │───▶│ ApplicationContext │───▶│ PriceCalculator │
│                 │    │                 │    │                 │
│ • Parse JSON    │    │ • DI Container  │    │ • Orchestrates  │
│ • Validate      │    │ • Wire Services │    │ • Coordinates   │
│ • Return Response│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Domain Layer Flow

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Visit Entity       │    │ DroppedFraction  │    │  Price Value    │
│                     │    │  Value Objects   │    │  Object         │
│ • calculate_base_   │    │                  │    │                 │
│   price()           │    │ • FractionType   │    │ • amount        │
│ • Business Logic    │    │ • Weight         │    │ • currency      │
│ • Invariants        │    │                  │    │                 │
└─────────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                           ▲                        ▲
         │                           │                        │
┌─────────────────────┐    ┌──────────────────┐              │
│ MonthlySurcharge    │    │  VisitRepository │              │
│ Service             │    │  Interface       │              │
│                     │    │                  │              │
│ • calculate_total_  │    │ • save()         │              │
│   price_with_       │    │ • find_visits_   │              │
│   surcharge()       │    │   for_person_    │              │
│ • 5% surcharge rule │    │   in_month()     │              │
└─────────────────────┘    └──────────────────┘              │
                                     ▲                       │
                                     │                       │
                           ┌──────────────────┐              │
                           │ InMemoryVisit    │              │
                           │ Repository       │              │
                           │ (Infrastructure) │              │
                           │                  │              │
                           │ • Concrete       │              │
                           │   Implementation │              │
                           └──────────────────┘              │
                                                             │
                           ┌──────────────────┐              │
                           │ External Visitor │              │
                           │ Service          │              │
                           │                  │              │
                           │ • Get visitor    │              │
                           │   info from API  │              │
                           │ • Anti-corruption│              │
                           │   layer          │              │
                           └──────────────────┘              │
                                                             │
                                    ┌────────────────────────┘
                                    ▼
                           ┌──────────────────┐
                           │  PriceResponse   │
                           │  DTO             │
                           │                  │
                           │ • price_amount   │
                           │ • price_currency │
                           │ • person_id      │
                           │ • visit_id       │
                           └──────────────────┘
```

## Step-by-Step Process

### When a visit request comes in:

1. **Flask Route** (`routes.py`)

   - Receives HTTP POST to `/calculatePrice`
   - Parses JSON into `VisitRequest` model
   - Calls `ApplicationContext.price_calculator.calculate_price()`

2. **Price Calculator** (`price_calculator.py`)

   - Creates `Visit` entity from request data
   - Converts JSON data to domain objects (DroppedFraction, Weight, etc.)
   - Saves visit to repository

3. **Monthly Surcharge Service** (`monthly_surcharge_service.py`)

   - Calculates base price using `visit.calculate_base_price()`
   - Checks if visitor has 3+ visits this month via repository
   - Applies 5% surcharge if threshold met
   - Returns total price

4. **Visit Repository** (`in_memory_visit_repository.py`)

   - Stores the visit
   - Provides monthly visit count queries
   - Supports surcharge calculations

5. **Response**
   - Wraps result in `PriceResponse`
   - Returns JSON with price details

## Key Components

- **Application Layer**: Routes, PriceCalculator, ApplicationContext
- **Domain Layer**: Visit Entity, MonthlySurchargeService, DroppedFraction
- **Infrastructure Layer**: InMemoryVisitRepository, ExternalVisitorService

## Business Rules Applied

1. **Base Pricing**: Each waste type has a price per kg
2. **Monthly Surcharge**: 5% surcharge applies to ALL visits when visitor has 3+ visits in a month
3. **Entity Validation**: Visit must have at least one dropped fraction
