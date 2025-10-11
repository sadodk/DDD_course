"""
🎓 EDUCATIONAL TEST: Domain Events & Invoice Flow

This test demonstrates the COMPLETE flow of domain events with REAL code.
        print("   ✓ Invoice Currency:", payload["invoice_currency"])

    print("\n" + "="*80)o mocks (except HTTP calls) - just real components working together!

Run with: poetry run pytest tests/integration/test_domain_events_and_invoicing.py -v -s

The -s flag shows all print statements so you can follow along step-by-step!
"""

from unittest.mock import patch, MagicMock
from datetime import datetime

from domain.events.event_dispatcher import InMemoryEventDispatcher
from domain.events.price_calculated_event import PriceCalculatedEvent
from domain.values.price import Price, Currency
from application.services.invoice_event_handler import InvoiceEventHandler
from application.external.invoice_api_client import InvoiceService


def test_complete_event_flow_with_real_code():
    """
    🎓 EDUCATIONAL TEST: Watch the complete domain event flow in action!

    This test shows how:
    1. We create real infrastructure components (EventDispatcher, InvoiceService, InvoiceEventHandler)
    2. We wire them together (subscribe the handler to the dispatcher)
    3. We create a PriceCalculatedEvent for a business customer
    4. We dispatch the event
    5. The handler automatically reacts and sends an invoice

    Only the HTTP call is mocked - everything else is REAL CODE!
    """

    print("\n" + "=" * 80)
    print("🎓 DOMAIN EVENTS FLOW DEMONSTRATION")
    print("=" * 80)

    # STEP 1: Create the real infrastructure components
    print("\n📦 STEP 1: Setting up infrastructure...")
    print("   Creating EventDispatcher (in-memory implementation)")
    dispatcher = InMemoryEventDispatcher()

    print("   Creating InvoiceService (HTTP client)")
    invoice_service = InvoiceService(
        base_url="https://ddd-in-language.aardling.eu/api",
        auth_token="test-token",
        workshop_id="test-workshop",
    )

    print("   Creating InvoiceEventHandler (event subscriber)")
    invoice_handler = InvoiceEventHandler(invoice_service)

    print("   ✅ All components created!")

    # STEP 2: Wire them together (subscribe handler to dispatcher)
    print("\n🔌 STEP 2: Wiring components together...")
    print("   Subscribing InvoiceEventHandler to EventDispatcher")
    # We need to pass the handler.handle method as the subscriber, not the handler itself
    dispatcher.subscribe(invoice_handler.handle)
    print("   ✅ Handler is now listening for events!")

    # STEP 3: Create a domain event for a business customer
    print("\n📋 STEP 3: Creating a PriceCalculatedEvent...")
    print("   Customer Type: business")
    print("   Company: Acme Corporation")
    print("   Email: ceo@acme-corp.com")
    print("   Price: €1,250.00")

    event = PriceCalculatedEvent(
        visitor_id="visitor-abc-123",
        visit_id="visit-xyz-789",
        calculated_price=Price(amount=1250, currency=Currency.EUR),
        customer_type="business",
        customer_email="ceo@acme-corp.com",
        company_name="Acme Corporation",
    )
    print(f"   ✅ Event created at {event.occurred_at}")

    # STEP 4: Mock only the HTTP call (we don't want to hit real API in test)
    print("\n🔧 STEP 4: Mocking HTTP call (we don't want to hit real API in test)...")
    with patch("application.external.invoice_api_client.requests.post") as mock_post:
        # Configure mock to return success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "invoice_id": "inv-12345",
        }
        mock_post.return_value = mock_response
        print("   ✅ HTTP mock configured to return success")

        # STEP 5: Dispatch the event and watch the magic!
        print("\n🚀 STEP 5: Dispatching event...")
        print("   The dispatcher will notify all subscribers...")
        print("   The InvoiceEventHandler will receive the event...")
        print("   The handler will check: Is this a business customer? ✓")
        print("   The handler will check: Does the customer have email? ✓")
        print("   The handler will call InvoiceService.send_invoice()...")
        print("   The InvoiceService will make HTTP POST to external API...")

        dispatcher.dispatch(event)  # ignore

        print("   ✅ Event dispatched successfully!")

        # STEP 6: Verify the invoice was sent with correct data
        print("\n✅ STEP 6: Verifying invoice was sent...")

        # Check that HTTP POST was called
        assert mock_post.called, "❌ HTTP POST was not called!"
        print("   ✓ HTTP POST was called")

        # Get the actual call arguments
        call_args = mock_post.call_args
        url = call_args[0][0]
        payload = call_args[1]["json"]

        # Verify URL
        assert url == "https://ddd-in-language.aardling.eu/api/api/invoice"
        print(f"   ✓ Correct URL: {url}")

        # Verify payload contains all the right data
        assert payload["email"] == "ceo@acme-corp.com"
        assert payload["invoice_amount"] == 1250
        assert payload["invoice_currency"] == "EUR"

        print("   ✓ Email:", payload["email"])
        print("   ✓ Invoice Amount:", payload["invoice_amount"])
        print("   ✓ Invoice Currency:", payload["invoice_currency"])

    print("\n" + "=" * 80)
    print("🎉 SUCCESS! The complete domain event flow works perfectly!")
    print("=" * 80)
    print("\n📚 What happened:")
    print(
        "   1. ✅ Created real infrastructure (EventDispatcher, InvoiceService, Handler)"
    )
    print("   2. ✅ Wired components together (Handler subscribed to Dispatcher)")
    print("   3. ✅ Created PriceCalculatedEvent for business customer")
    print("   4. ✅ Dispatched event through the system")
    print("   5. ✅ Handler automatically received and processed the event")
    print("   6. ✅ InvoiceService sent invoice with correct data to external API")
    print("\n💡 This demonstrates the Observer Pattern and Domain Events in action!")
    print("   The PriceCalculator doesn't need to know about invoices.")
    print("   The InvoiceHandler simply listens for PriceCalculatedEvents.")
    print("   Components are decoupled and can evolve independently!")
    print("=" * 80 + "\n")
    """
    🎓 EDUCATIONAL TEST: Watch the complete domain event flow in action!

    This test shows how:
    1. We create real infrastructure components (EventDispatcher, InvoiceService, InvoiceEventHandler)
    2. We wire them together (subscribe the handler to the dispatcher)
    3. We create a PriceCalculatedEvent for a business customer
    4. We dispatch the event
    5. The handler automatically reacts and sends an invoice

    Only the HTTP call is mocked - everything else is REAL CODE!
    """

    print("\n" + "=" * 80)
    print("🎓 DOMAIN EVENTS FLOW DEMONSTRATION")
    print("=" * 80)

    # STEP 1: Create the real infrastructure components
    print("\n📦 STEP 1: Setting up infrastructure...")
    print("   Creating EventDispatcher (in-memory implementation)")
    dispatcher = InMemoryEventDispatcher()

    print("   Creating InvoiceService (HTTP client)")
    invoice_service = InvoiceService(
        base_url="https://ddd-in-language.aardling.eu",
        auth_token="demo-auth-token",
        workshop_id="python-workshop",
    )

    print("   Creating InvoiceEventHandler (event subscriber)")
    invoice_handler = InvoiceEventHandler(invoice_service)

    print("   ✅ All components created!")

    # STEP 2: Wire them together (subscribe handler to dispatcher)
    print("\n🔌 STEP 2: Wiring components together...")
    print("   Subscribing InvoiceEventHandler to EventDispatcher")
    dispatcher.subscribe(invoice_handler.handle)  # Pass the handle method as a callable
    print("   ✅ Handler is now listening for events!")

    # STEP 3: Create a domain event for a business customer
    print("\n📋 STEP 3: Creating a PriceCalculatedEvent...")
    print("   Customer Type: business")
    print("   Company: Acme Corporation")
    print("   Email: ceo@acme-corp.com")
    print("   Price: €1,250.00")

    event = PriceCalculatedEvent(
        visitor_id="visitor-abc-123",
        visit_id="visit-xyz-789",
        calculated_price=Price(amount=1250, currency=Currency.EUR),
        customer_type="business",
        customer_email="ceo@acme-corp.com",  # Note the correct field name
    )
    print(f"   ✅ Event created at {event.occurred_at}")

    # STEP 4: Mock only the HTTP call (we don't want to hit real API in test)
    print("\n🔧 STEP 4: Mocking HTTP call (we don't want to hit real API in test)...")
    with patch("requests.post") as mock_post:
        # Configure mock to return success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "invoice_id": "inv-12345",
        }
        mock_post.return_value = mock_response
        print("   ✅ HTTP mock configured to return success")

        # STEP 5: Dispatch the event and watch the magic!
        print("\n🚀 STEP 5: Dispatching event...")
        print("   The dispatcher will notify all subscribers...")
        print("   The InvoiceEventHandler will receive the event...")
        print("   The handler will check: Is this a business customer? ✓")
        print("   The handler will check: Does the customer have email? ✓")
        print("   The handler will call InvoiceService.send_invoice()...")
        print("   The InvoiceService will make HTTP POST to external API...")

        dispatcher.dispatch(event)

        print("   ✅ Event dispatched successfully!")

        # STEP 6: Verify the invoice was sent with correct data
        print("\n✅ STEP 6: Verifying invoice was sent...")

        # Check that HTTP POST was called
        assert mock_post.called, "❌ HTTP POST was not called!"
        print("   ✓ HTTP POST was called")

        # Get the actual call arguments
        call_args = mock_post.call_args
        url = call_args[0][0]
        payload = call_args[1]["json"]

        # Verify URL
        assert url == "https://ddd-in-language.aardling.eu/api/invoice"
        print(f"   ✓ Correct URL: {url}")

        # Verify payload contains all the right data
        assert payload["email"] == "ceo@acme-corp.com"
        assert payload["invoice_amount"] == 1250
        assert payload["invoice_currency"] == "EUR"

        print("   ✓ Customer Email:", payload["email"])
        print("   ✓ Amount:", payload["invoice_amount"])
        print("   ✓ Currency:", payload["invoice_currency"])

    print("\n" + "=" * 80)
    print("🎉 SUCCESS! The complete domain event flow works perfectly!")
    print("=" * 80)
    print("\n📚 What happened:")
    print(
        "   1. ✅ Created real infrastructure (EventDispatcher, InvoiceService, Handler)"
    )
    print("   2. ✅ Wired components together (Handler subscribed to Dispatcher)")
    print("   3. ✅ Created PriceCalculatedEvent for business customer")
    print("   4. ✅ Dispatched event through the system")
    print("   5. ✅ Handler automatically received and processed the event")
    print("   6. ✅ InvoiceService sent invoice with correct data to external API")
    print("\n💡 This demonstrates the Observer Pattern and Domain Events in action!")
    print("   The PriceCalculator doesn't need to know about invoices.")
    print("   The InvoiceHandler simply listens for PriceCalculatedEvents.")
    print("   Components are decoupled and can evolve independently!")
    print("=" * 80 + "\n")
