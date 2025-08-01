"""Tests for ZenoPay WebhookService."""

from typing import Any, Dict, List
import pytest
from unittest.mock import Mock, patch

from elusion.zenopay.services import WebhookService
from elusion.zenopay.models.webhook import WebhookEvent, WebhookResponse
from elusion.zenopay.exceptions import ZenoPayWebhookError

from tests.fixtures.mock_data import webhook_json_fixtures, mock_handlers


class TestWebhookService:
    """Test WebhookService functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.service = WebhookService()
        mock_handlers.reset()

    def test_parse_webhook_valid_completed(self):
        """Test parsing valid completed webhook."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())

        assert isinstance(event, WebhookEvent)
        assert event.payload.order_id == "ZP-20250616-123456-test-01"
        assert event.payload.payment_status == "COMPLETED"
        assert event.payload.reference == "REF123456789"
        assert event.payload.metadata is not None
        assert event.payload.metadata["product_id"] == "12345"

    def test_parse_webhook_valid_failed(self):
        """Test parsing valid failed webhook."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_failed_json())

        assert event.payload.order_id == "ZP-20250616-123456-test-02"
        assert event.payload.payment_status == "FAILED"
        assert event.payload.reference == "REF123456790"

    def test_parse_webhook_valid_pending(self):
        """Test parsing valid pending webhook."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_pending_json())

        assert event.payload.payment_status == "PENDING"
        assert event.payload.order_id == "ZP-20250616-123456-test-03"

    def test_parse_webhook_valid_cancelled(self):
        """Test parsing valid cancelled webhook."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_cancelled_json())

        assert event.payload.payment_status == "CANCELLED"
        assert event.payload.order_id == "ZP-20250616-123456-test-04"

    def test_parse_webhook_minimal_data(self):
        """Test parsing minimal valid webhook data."""
        event = self.service.parse_webhook(webhook_json_fixtures.minimal_json())

        assert event.payload.order_id == "ZP-minimal-test"
        assert event.payload.payment_status == "COMPLETED"
        assert event.payload.reference == "REF-MIN"

    def test_parse_webhook_invalid_json(self):
        """Test parsing invalid JSON raises error."""
        with pytest.raises(ZenoPayWebhookError):
            self.service.parse_webhook(webhook_json_fixtures.invalid_json())

    def test_parse_webhook_empty_json(self):
        """Test parsing empty JSON raises error."""
        with pytest.raises(ZenoPayWebhookError):
            self.service.parse_webhook(webhook_json_fixtures.empty_json())

    def test_parse_webhook_missing_order_id(self):
        """Test parsing webhook missing order_id raises error."""
        with pytest.raises(ZenoPayWebhookError):
            self.service.parse_webhook(webhook_json_fixtures.missing_order_id_json())

    def test_parse_webhook_missing_payment_status(self):
        """Test parsing webhook missing payment_status raises error."""
        with pytest.raises(ZenoPayWebhookError):
            self.service.parse_webhook(webhook_json_fixtures.missing_payment_status_json())

    def test_register_handler(self):
        """Test handler registration."""
        handler = Mock()
        self.service.register_handler("COMPLETED", handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())
        response = self.service.handle_webhook(event)

        handler.assert_called_once_with(event)
        assert response.status == "success"

    def test_on_payment_completed(self):
        """Test payment completed handler registration."""
        self.service.on_payment_completed(mock_handlers.payment_completed_handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())
        self.service.handle_webhook(event)

        assert "completed" in mock_handlers.calls
        assert len(mock_handlers.events) == 1
        assert mock_handlers.events[0].payload.payment_status == "COMPLETED"

    def test_on_payment_failed(self):
        """Test payment failed handler registration."""
        self.service.on_payment_failed(mock_handlers.payment_failed_handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_failed_json())
        self.service.handle_webhook(event)

        assert "failed" in mock_handlers.calls
        assert mock_handlers.events[0].payload.payment_status == "FAILED"

    def test_on_payment_pending(self):
        """Test payment pending handler registration."""
        self.service.on_payment_pending(mock_handlers.payment_pending_handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_pending_json())
        self.service.handle_webhook(event)

        assert "pending" in mock_handlers.calls
        assert mock_handlers.events[0].payload.payment_status == "PENDING"

    def test_on_payment_cancelled(self):
        """Test payment cancelled handler registration."""
        self.service.on_payment_cancelled(mock_handlers.payment_cancelled_handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_cancelled_json())
        self.service.handle_webhook(event)

        assert "cancelled" in mock_handlers.calls
        assert mock_handlers.events[0].payload.payment_status == "CANCELLED"

    def test_handle_webhook_no_handler(self):
        """Test handling webhook with no registered handler."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())
        response = self.service.handle_webhook(event)

        assert response.status == "success"
        assert "ZP-20250616-123456-test-01" in response.message

    def test_handle_webhook_handler_exception(self):
        """Test handling webhook when handler raises exception."""
        self.service.on_payment_completed(mock_handlers.error_handler)

        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())
        response = self.service.handle_webhook(event)

        assert response.status == "error"
        assert "Error processing webhook" in response.message

    def test_process_webhook_request_success(self):
        """Test complete webhook request processing."""
        self.service.on_payment_completed(mock_handlers.payment_completed_handler)

        response = self.service.process_webhook_request(webhook_json_fixtures.valid_completed_json())

        assert response.status == "success"
        assert "ZP-20250616-123456-test-01" in response.message
        assert "completed" in mock_handlers.calls

    def test_process_webhook_request_invalid_data(self):
        """Test webhook request processing with invalid data."""
        response = self.service.process_webhook_request(webhook_json_fixtures.invalid_json())

        assert response.status == "error"
        assert "Invalid webhook data" in response.message

    def test_process_webhook_request_with_signature(self):
        """Test webhook processing with signature."""
        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json(), signature="test-signature")

        assert event.signature == "test-signature"

    def test_create_test_webhook(self):
        """Test creating test webhook event."""
        test_event = self.service.create_test_webhook("test-order-123", "COMPLETED")

        assert test_event.payload.order_id == "test-order-123"
        assert test_event.payload.payment_status == "COMPLETED"
        assert test_event.payload.reference is not None
        assert test_event.payload.reference.startswith("TEST-")
        assert test_event.payload.metadata is not None
        assert test_event.payload.metadata["test"] is True

    def test_create_test_webhook_default_status(self):
        """Test creating test webhook with default status."""
        test_event = self.service.create_test_webhook("test-order-456")

        assert test_event.payload.payment_status == "COMPLETED"

    def test_multiple_handlers_replacement(self):
        """Test that registering multiple handlers replaces previous ones."""
        handler1 = Mock()
        handler2 = Mock()

        self.service.register_handler("COMPLETED", handler1)
        self.service.register_handler("COMPLETED", handler2)  # Should replace handler1

        event = self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())
        self.service.handle_webhook(event)

        handler1.assert_not_called()
        handler2.assert_called_once_with(event)

    @patch("elusion.zenopay.services.webhooks.logger")
    def test_logging_webhook_parsing(self, mock_logger: Mock):
        """Test that webhook parsing is logged."""
        self.service.parse_webhook(webhook_json_fixtures.valid_completed_json())

        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "ZP-20250616-123456-test-01" in call_args
        assert "COMPLETED" in call_args

    @patch("elusion.zenopay.services.webhooks.logger")
    def test_logging_webhook_processing(self, mock_logger: Mock):
        """Test that successful webhook processing is logged."""
        self.service.process_webhook_request(webhook_json_fixtures.valid_completed_json())

        mock_logger.info.assert_called()


class TestWebhookModels:
    """Test webhook model functionality."""

    def test_webhook_event_from_raw_data(self):
        """Test WebhookEvent creation from raw data."""
        event = WebhookEvent.from_raw_data(webhook_json_fixtures.valid_completed_json())

        assert event.payload.order_id == "ZP-20250616-123456-test-01"
        assert event.payload.payment_status == "COMPLETED"

    def test_webhook_event_properties(self):
        """Test WebhookEvent payload properties."""
        completed_event = WebhookEvent.from_raw_data(webhook_json_fixtures.valid_completed_json())
        failed_event = WebhookEvent.from_raw_data(webhook_json_fixtures.valid_failed_json())

        assert completed_event.payload.is_completed
        assert not completed_event.payload.is_failed

        assert failed_event.payload.is_failed
        assert not failed_event.payload.is_completed

    def test_webhook_event_metadata_access(self):
        """Test accessing webhook metadata."""
        event = WebhookEvent.from_raw_data(webhook_json_fixtures.valid_completed_json())

        product_id = event.payload.get_metadata_value("product_id")
        assert product_id == "12345"

        missing_value = event.payload.get_metadata_value("missing_key", "default")
        assert missing_value == "default"

    def test_webhook_response_creation(self):
        """Test WebhookResponse creation."""
        response = WebhookResponse(status="success", message="Test message")

        assert response.status == "success"
        assert response.message == "Test message"

    def test_webhook_response_default_values(self):
        """Test WebhookResponse default values."""
        response = WebhookResponse(status="success", message="Webhook received")

        assert response.status == "success"
        assert response.message == "Webhook received"


class TestWebhookIntegration:
    """Test webhook integration scenarios."""

    def test_webhook_service_with_zenopay_client(self):
        """Test webhook service integration with ZenoPay client."""
        from elusion.zenopay import ZenoPay

        client = ZenoPay(api_key="test_api_key")

        # Test that webhook service is available
        assert hasattr(client, "webhooks")
        assert isinstance(client.webhooks, WebhookService)

    def test_end_to_end_webhook_flow(self):
        """Test complete webhook flow."""
        service = WebhookService()
        results: List[Dict[str, Any]] = []

        def completion_handler(event: WebhookEvent):
            results.append(
                {
                    "order_id": event.payload.order_id,
                    "status": event.payload.payment_status,
                    "reference": event.payload.reference,
                }
            )

        service.on_payment_completed(completion_handler)

        response = service.process_webhook_request(webhook_json_fixtures.valid_completed_json())

        assert response.status == "success"
        assert len(results) == 1
        assert results[0]["order_id"] == "ZP-20250616-123456-test-01"
        assert results[0]["status"] == "COMPLETED"
        assert results[0]["reference"] == "REF123456789"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
