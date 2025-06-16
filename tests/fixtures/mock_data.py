"""Mock data and fixtures for ZenoPay SDK tests."""

import json
from datetime import datetime
from typing import Dict, Any, List

from elusion.zenopay.models import WebhookEvent


class WebhookFixtures:
    """Webhook test data fixtures."""

    @staticmethod
    def valid_completed_webhook() -> Dict[str, Any]:
        """Valid completed payment webhook data."""
        return {
            "order_id": "ZP-20250616-123456-test-01",
            "payment_status": "COMPLETED",
            "reference": "REF123456789",
            "metadata": {
                "product_id": "12345",
                "color": "blue",
                "size": "L",
                "amount": 1000,
            },
        }

    @staticmethod
    def valid_failed_webhook() -> Dict[str, Any]:
        """Valid failed payment webhook data."""
        return {
            "order_id": "ZP-20250616-123456-test-02",
            "payment_status": "FAILED",
            "reference": "REF123456790",
            "metadata": {"product_id": "12346", "error_code": "INSUFFICIENT_FUNDS"},
        }

    @staticmethod
    def valid_pending_webhook() -> Dict[str, Any]:
        """Valid pending payment webhook data."""
        return {
            "order_id": "ZP-20250616-123456-test-03",
            "payment_status": "PENDING",
            "reference": "REF123456791",
            "metadata": {
                "product_id": "12347",
                "initiated_at": datetime.now().isoformat(),
            },
        }

    @staticmethod
    def valid_cancelled_webhook() -> Dict[str, Any]:
        """Valid cancelled payment webhook data."""
        return {
            "order_id": "ZP-20250616-123456-test-04",
            "payment_status": "CANCELLED",
            "reference": "REF123456792",
            "metadata": {"product_id": "12348", "cancelled_by": "user"},
        }

    @staticmethod
    def minimal_webhook() -> Dict[str, Any]:
        """Minimal valid webhook data."""
        return {
            "order_id": "ZP-minimal-test",
            "payment_status": "COMPLETED",
            "reference": "REF-MIN",
        }

    @staticmethod
    def webhook_without_metadata() -> Dict[str, Any]:
        """Webhook without metadata."""
        return {
            "order_id": "ZP-no-metadata-test",
            "payment_status": "COMPLETED",
            "reference": "REF-NO-META",
        }

    @staticmethod
    def invalid_webhook_missing_order_id() -> Dict[str, Any]:
        """Invalid webhook missing order_id."""
        return {"payment_status": "COMPLETED", "reference": "REF123456789"}

    @staticmethod
    def invalid_webhook_missing_payment_status() -> Dict[str, Any]:
        """Invalid webhook missing payment_status."""
        return {"order_id": "ZP-missing-status-test", "reference": "REF123456789"}

    @staticmethod
    def invalid_webhook_bad_status() -> Dict[str, Any]:
        """Invalid webhook with bad payment status."""
        return {
            "order_id": "ZP-bad-status-test",
            "payment_status": "INVALID_STATUS",
            "reference": "REF123456789",
        }


class WebhookJsonFixtures:
    """JSON string fixtures for webhook tests."""

    @staticmethod
    def valid_completed_json() -> str:
        """Valid completed webhook as JSON string."""
        return json.dumps(WebhookFixtures.valid_completed_webhook())

    @staticmethod
    def valid_failed_json() -> str:
        """Valid failed webhook as JSON string."""
        return json.dumps(WebhookFixtures.valid_failed_webhook())

    @staticmethod
    def valid_pending_json() -> str:
        """Valid pending webhook as JSON string."""
        return json.dumps(WebhookFixtures.valid_pending_webhook())

    @staticmethod
    def valid_cancelled_json() -> str:
        """Valid cancelled webhook as JSON string."""
        return json.dumps(WebhookFixtures.valid_cancelled_webhook())

    @staticmethod
    def minimal_json() -> str:
        """Minimal webhook as JSON string."""
        return json.dumps(WebhookFixtures.minimal_webhook())

    @staticmethod
    def invalid_json() -> str:
        """Invalid JSON string."""
        return '{"invalid": json string}'

    @staticmethod
    def empty_json() -> str:
        """Empty JSON object."""
        return "{}"

    @staticmethod
    def missing_order_id_json() -> str:
        """Invalid webhook missing order_id as JSON."""
        return json.dumps(WebhookFixtures.invalid_webhook_missing_order_id())

    @staticmethod
    def missing_payment_status_json() -> str:
        """Invalid webhook missing payment_status as JSON."""
        return json.dumps(WebhookFixtures.invalid_webhook_missing_payment_status())


class OrderFixtures:
    """Order test data fixtures."""

    @staticmethod
    def valid_order_data() -> Dict[str, Any]:
        """Valid order creation data."""
        return {
            "buyer_email": "test@example.com",
            "buyer_name": "Test User",
            "buyer_phone": "0700000000",
            "amount": 1000,
            "webhook_url": "https://test.com/webhook",
            "metadata": {"product_id": "12345", "campaign": "test_campaign"},
        }

    @staticmethod
    def minimal_order_data() -> Dict[str, Any]:
        """Minimal valid order data."""
        return {
            "buyer_email": "minimal@example.com",
            "buyer_name": "Minimal User",
            "buyer_phone": "0700000001",
            "amount": 500,
        }

    @staticmethod
    def order_response_data() -> Dict[str, Any]:
        """Mock order response data."""
        return {
            "status": "success",
            "message": "Order created successfully",
            "order_id": "ZP-20250616-123456-test-01",
        }

    @staticmethod
    def order_status_response_data() -> Dict[str, Any]:
        """Mock order status response data."""
        return {
            "status": "success",
            "order_id": "ZP-20250616-123456-test-01",
            "message": "Order status retrieved successfully",
            "payment_status": "PENDING",
        }


class MockHandlers:
    """Mock handler functions for testing."""

    def __init__(self):
        self.calls: List[str] = []
        self.events: List[WebhookEvent] = []

    def payment_completed_handler(self, event: WebhookEvent):
        """Mock completed payment handler."""
        self.calls.append("completed")
        self.events.append(event)

    def payment_failed_handler(self, event: WebhookEvent):
        """Mock failed payment handler."""
        self.calls.append("failed")
        self.events.append(event)

    def payment_pending_handler(self, event: WebhookEvent):
        """Mock pending payment handler."""
        self.calls.append("pending")
        self.events.append(event)

    def payment_cancelled_handler(self, event: WebhookEvent):
        """Mock cancelled payment handler."""
        self.calls.append("cancelled")
        self.events.append(event)

    def error_handler(self, event: WebhookEvent):
        """Handler that raises an error."""
        raise Exception("Handler error for testing")

    def reset(self):
        """Reset call tracking."""
        self.calls.clear()
        self.events.clear()


webhook_fixtures = WebhookFixtures()
webhook_json_fixtures = WebhookJsonFixtures()
order_fixtures = OrderFixtures()
mock_handlers = MockHandlers()
