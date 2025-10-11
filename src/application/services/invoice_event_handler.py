"""Event handler for sending invoices when prices are calculated."""

import logging
from domain.events.domain_event import DomainEvent
from domain.events.price_calculated_event import PriceCalculatedEvent
from application.external.invoice_api_client import InvoiceService, InvoiceRequest

logger = logging.getLogger(__name__)


class InvoiceEventHandler:
    """
    Event handler that listens to PriceCalculatedEvents and sends invoices.

    This handler implements the Subscriber pattern, reacting to domain events
    to perform infrastructure actions (sending invoices via HTTP).

    Architecture:
    - Domain layer emits events (doesn't know about invoicing)
    - This handler listens and performs the side effect
    - Keeps domain layer pure and decoupled from infrastructure
    """

    def __init__(self, invoice_service: InvoiceService):
        """
        Initialize with invoice service dependency.

        Args:
            invoice_service: Service for sending invoices
        """
        self.invoice_service = invoice_service

    def handle(self, event: DomainEvent) -> None:
        """
        Handle domain events. Only processes PriceCalculatedEvent for business customers.

        Args:
            event: Domain event to handle
        """
        # Filter: only handle PriceCalculatedEvent
        if not isinstance(event, PriceCalculatedEvent):
            return

        # Filter: only send invoices for business customers
        if not event.is_business_customer():
            logger.debug(
                f"Skipping invoice for non-business customer: {event.visitor_id}"
            )
            return

        # Validation: ensure we have an email
        if not event.customer_email:
            logger.warning(
                f"Cannot send invoice - no email for business customer: {event.visitor_id}"
            )
            return

        # Send the invoice
        logger.info(f"Sending invoice for business customer {event.visitor_id}")

        invoice_request = InvoiceRequest(
            email=event.customer_email,
            invoice_amount=event.calculated_price.amount,
            invoice_currency=str(event.calculated_price.currency),
        )

        success = self.invoice_service.send_invoice(invoice_request)

        if success:
            logger.info(f"Invoice sent successfully to {event.customer_email}")
        else:
            logger.error(f"Failed to send invoice to {event.customer_email}")
