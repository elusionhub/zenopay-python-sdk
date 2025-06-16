"""Webhook service for the ZenoPay SDK."""

import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from elusion.zenopay.exceptions import ZenoPayWebhookError
from elusion.zenopay.models.webhook import WebhookEvent, WebhookResponse

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for handling ZenoPay webhooks."""

    def __init__(self) -> None:
        """Initialize the webhook service."""
        self._handlers: Dict[str, Callable[[WebhookEvent], Any]] = {}

    def parse_webhook(self, raw_data: str, signature: Optional[str] = None) -> WebhookEvent:
        """Parse raw webhook data into a WebhookEvent.

        Args:
            raw_data: Raw JSON string from the webhook request.
            signature: Optional webhook signature for verification.

        Returns:
            Parsed WebhookEvent.

        Raises:
            ZenoPayWebhookError: If the webhook data is invalid.

        Examples:
            >>> webhook_service = WebhookService()
            >>> raw_data = '''{"order_id":"677e43274d7cb","payment_status":"COMPLETED","reference":"1003020496"}'''
            >>> event = webhook_service.parse_webhook(raw_data)
            >>> print(f"Order {event.payload.order_id} is {event.payload.payment_status}")
        """
        try:
            event = WebhookEvent.from_raw_data(raw_data)
            event.signature = signature
            event.timestamp = datetime.now().isoformat()

            logger.info(f"Parsed webhook for order {event.payload.order_id}: {event.payload.payment_status}")
            return event

        except Exception as e:
            logger.error(f"Failed to parse webhook: {e}")
            raise ZenoPayWebhookError(f"Invalid webhook data: {e}", {"raw_data": raw_data})

    def register_handler(self, event_type: str, handler: Callable[[WebhookEvent], Any]) -> None:
        """Register a handler for specific webhook events.

        Args:
            event_type: Type of event to handle (e.g., "COMPLETED", "FAILED").
            handler: Function to call when this event type is received.

        Examples:
            >>> def payment_completed_handler(event: WebhookEvent):
            ...     print(f"Payment completed for order {event.payload.order_id}")
            ...     # Update database, send emails, etc.
            >>>
            >>> webhook_service.register_handler("COMPLETED", payment_completed_handler)
        """
        self._handlers[event_type] = handler

    def handle_webhook(self, event: WebhookEvent) -> WebhookResponse:
        """Handle a parsed webhook event.

        Args:
            event: Parsed webhook event.

        Returns:
            Webhook response to send back to ZenoPay.

        Examples:
            >>> event = webhook_service.parse_webhook(raw_data)
            >>> response = webhook_service.handle_webhook(event)
            >>> print(response.message)  # "Webhook received and processed"
        """
        try:
            event_type = event.payload.payment_status

            if event_type in self._handlers:
                self._handlers[event_type](event)
            else:
                logger.warning(f"No handler registered for event type: {event_type}")

            self._log_webhook_event(event)

            return WebhookResponse(
                status="success",
                message=f"Webhook received and processed for order {event.payload.order_id}",
            )

        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return WebhookResponse(status="error", message=f"Error processing webhook: {str(e)}")

    def process_webhook_request(self, raw_data: str, signature: Optional[str] = None) -> WebhookResponse:
        """Process a complete webhook request from raw data to response.

        Args:
            raw_data: Raw JSON string from the webhook request.
            signature: Optional webhook signature.

        Returns:
            Webhook response to send back to ZenoPay.

        Examples:
            >>> # In your Flask/FastAPI endpoint:
            >>> @app.route('/webhook', methods=['POST'])
            >>> def handle_zenopay_webhook():
            ...     raw_data = request.data.decode('utf-8')
            ...     response = webhook_service.process_webhook_request(raw_data)
            ...     return {"status": response.status, "message": response.message}
        """
        try:
            event = self.parse_webhook(raw_data, signature)

            response = self.handle_webhook(event)

            logger.info(f"Successfully processed webhook for order {event.payload.order_id}")
            return response

        except ZenoPayWebhookError as e:
            logger.error(f"Webhook error: {e}")
            return WebhookResponse(status="error", message=str(e))
        except Exception as e:
            logger.error(f"Unexpected error processing webhook: {e}")
            return WebhookResponse(status="error", message="Internal error processing webhook")

    def _log_webhook_event(self, event: WebhookEvent) -> None:
        """Log webhook event for debugging and audit purposes.

        Args:
            event: The webhook event to log.
        """
        log_data: Dict[str, Any] = {
            "timestamp": event.timestamp,
            "order_id": event.payload.order_id,
            "payment_status": event.payload.payment_status,
            "reference": event.payload.reference,
        }

        logger.info(f"Webhook event logged: {json.dumps(log_data)}")

    def create_test_webhook(self, order_id: str, payment_status: str = "COMPLETED") -> WebhookEvent:
        """Create a test webhook event for development/testing.

        Args:
            order_id: Order ID for the test webhook.
            payment_status: Payment status for the test webhook.

        Returns:
            Test webhook event.

        Examples:
            >>> # For testing your webhook handlers
            >>> test_event = webhook_service.create_test_webhook("test-123", "COMPLETED")
            >>> response = webhook_service.handle_webhook(test_event)
        """
        test_payload: Dict[str, Any] = {
            "order_id": order_id,
            "payment_status": payment_status,
            "reference": "TEST-" + str(int(datetime.now().timestamp())),
            "metadata": {"test": True, "created_at": datetime.now().isoformat()},
        }

        raw_data = json.dumps(test_payload)
        return self.parse_webhook(raw_data)

    def on_payment_completed(self, handler: Callable[[WebhookEvent], Any]) -> None:
        """Register handler for payment completed events."""
        self.register_handler("COMPLETED", handler)

    def on_payment_failed(self, handler: Callable[[WebhookEvent], Any]) -> None:
        """Register handler for payment failed events."""
        self.register_handler("FAILED", handler)

    def on_payment_pending(self, handler: Callable[[WebhookEvent], Any]) -> None:
        """Register handler for payment pending events."""
        self.register_handler("PENDING", handler)

    def on_payment_cancelled(self, handler: Callable[[WebhookEvent], Any]) -> None:
        """Register handler for payment cancelled events."""
        self.register_handler("CANCELLED", handler)
