"""Service for sending invoices to business customers."""

import requests
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class InvoiceRequest:
    """Data required to send an invoice."""

    email: str
    invoice_amount: float
    invoice_currency: str


class InvoiceService:
    """
    Service for sending invoices via HTTP POST.

    This is an infrastructure service that handles communication
    with the external invoice API.
    """

    def __init__(self, base_url: str, auth_token: str, workshop_id: str):
        """
        Initialize the invoice service.

        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            workshop_id: Workshop identifier
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.workshop_id = workshop_id

    def send_invoice(self, invoice_request: InvoiceRequest) -> bool:
        """
        Send an invoice to the specified email.

        Args:
            invoice_request: Invoice data to send

        Returns:
            True if invoice was sent successfully, False otherwise
        """
        url = f"{self.base_url}/api/invoice"
        headers = {
            "content-type": "application/json",
            "x-auth-token": self.auth_token,
            "x-workshop-id": self.workshop_id,
        }

        payload = {
            "email": invoice_request.email,
            "invoice_amount": invoice_request.invoice_amount,
            "invoice_currency": invoice_request.invoice_currency,
        }

        try:
            logger.info(
                f"Sending invoice to {invoice_request.email} for {invoice_request.invoice_amount} {invoice_request.invoice_currency}"
            )
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"Invoice sent successfully: {response.json()}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to send invoice: {e}")
            return False
