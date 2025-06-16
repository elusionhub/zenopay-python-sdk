"""Webhook-related models for the ZenoPay SDK."""

import json
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WebhookPayload(BaseModel):
    """Model for webhook payload from ZenoPay."""

    order_id: str = Field(..., description="Order ID")
    payment_status: str = Field(..., description="Payment status")
    reference: Optional[str] = Field(None, description="Payment reference number")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Order metadata")

    @field_validator("payment_status")
    def validate_payment_status(cls, v: str) -> str:
        """Validate payment status."""
        valid_statuses = ["PENDING", "COMPLETED", "FAILED", "CANCELLED"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid payment status: {v}")
        return v

    @field_validator("metadata")
    def parse_metadata(cls, v: Union[str, Dict[str, Any], None]) -> Optional[Dict[str, Any]]:
        """Parse metadata from JSON string if necessary."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.payment_status == "COMPLETED"

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.payment_status == "FAILED"

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from the metadata."""
        if self.metadata:
            return self.metadata.get(key, default)
        return default

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "677e43274d7cb",
                "payment_status": "COMPLETED",
                "reference": "1003020496",
                "metadata": {
                    "product_id": "12345",
                    "color": "blue",
                    "size": "L",
                    "custom_notes": "Please gift-wrap this item.",
                },
            }
        }
    )


class WebhookEvent(BaseModel):
    """Model for complete webhook event information."""

    payload: WebhookPayload = Field(..., description="Webhook payload data")
    raw_data: str = Field(..., description="Raw webhook data received")
    timestamp: Optional[str] = Field(None, description="Event timestamp")
    signature: Optional[str] = Field(None, description="Webhook signature for verification")

    @classmethod
    def from_raw_data(cls, raw_data: str) -> "WebhookEvent":
        """Create WebhookEvent from raw webhook data.

        Args:
            raw_data: Raw JSON string from webhook.

        Returns:
            WebhookEvent instance.

        Raises:
            ValueError: If the raw data cannot be parsed.
        """
        try:
            payload_data = json.loads(raw_data)
            payload = WebhookPayload.model_validate(payload_data)

            return cls(payload=payload, raw_data=raw_data, timestamp=None, signature=None)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid webhook data: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy processing."""
        return {
            "order_id": self.payload.order_id,
            "payment_status": self.payload.payment_status,
            "reference": self.payload.reference,
            "metadata": self.payload.metadata,
            "raw_data": self.raw_data,
            "timestamp": self.timestamp,
        }


class WebhookResponse(BaseModel):
    """Model for webhook response."""

    status: str = Field("success", description="Response status")
    message: str = Field("Webhook received", description="Response message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Webhook received and processed",
            }
        }
    )
