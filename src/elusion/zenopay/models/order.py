"""Order-related models for the ZenoPay SDK."""

from datetime import datetime
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderBase(BaseModel):
    """Base order model with common fields."""

    buyer_email: str = Field(..., description="Buyer's email address")
    buyer_name: str = Field(..., description="Buyer's full name")
    buyer_phone: str = Field(..., description="Buyer's phone number")
    amount: int = Field(..., gt=0, description="Order amount in smallest currency unit")
    webhook_url: Optional[str] = Field(None, description="URL to receive webhook notifications")

    @field_validator("buyer_email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("buyer_phone")
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove any non-digit characters except +
        cleaned = "".join(c for c in v if c.isdigit() or c == "+")
        if len(cleaned) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return cleaned

    @field_validator("webhook_url")
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook URL format."""
        if v is not None:
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                raise ValueError("Webhook URL must start with http:// or https://")
        return v


class NewOrder(OrderBase):
    """Model for creating a new order."""

    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional order metadata")

    @field_validator("metadata")
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Keep metadata as dict, convert to JSON only when needed."""
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "buyer_email": "jackson@gmail.com",
                "buyer_name": "Jackson Dastani",
                "buyer_phone": "0652449389",
                "amount": 1000,
                "webhook_url": "https://yourwebsite.com/webhook",
                "metadata": {
                    "product_id": "12345",
                    "color": "blue",
                    "size": "L",
                    "custom_notes": "Please gift-wrap this item.",
                },
            }
        }
    )


class OrderStatus(BaseModel):
    """Model for checking order status."""

    order_id: str = Field(..., description="Order ID to check status for")

    model_config = ConfigDict(json_schema_extra={"example": {"order_id": "66c4bb9c9abb1"}})


class Order(BaseModel):
    """Complete order model with all fields."""

    # Order details
    buyer_email: str = Field(..., description="Buyer's email address")
    buyer_name: str = Field(..., description="Buyer's full name")
    buyer_phone: str = Field(..., description="Buyer's phone number")
    amount: int = Field(..., description="Order amount")

    # Payment details
    payment_status: str = Field("PENDING", description="Current payment status")
    reference: Optional[str] = Field(None, description="Payment reference number")

    # Additional information
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Order metadata")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Order creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="Payment completion time")

    @field_validator("payment_status")
    def validate_payment_status(cls, v: str) -> str:
        """Validate payment status."""
        valid_statuses = ["PENDING", "COMPLETED", "FAILED", "CANCELLED"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("metadata")
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return v

    @property
    def is_paid(self) -> bool:
        """Check if the order has been paid."""
        return self.payment_status == "COMPLETED"

    @property
    def is_pending(self) -> bool:
        """Check if the order is still pending."""
        return self.payment_status == "PENDING"

    @property
    def has_failed(self) -> bool:
        """Check if the payment has failed."""
        return self.payment_status == "FAILED"

    @property
    def is_cancelled(self) -> bool:
        """Check if the order has been cancelled."""
        return self.payment_status == "CANCELLED"

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from the metadata."""
        if self.metadata:
            return self.metadata.get(key, default)
        return default

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "66c4bb9c9abb1",
                "buyer_email": "jackson@gmail.com",
                "buyer_name": "Jackson Dastani",
                "buyer_phone": "0652449389",
                "amount": 1000,
                "payment_status": "COMPLETED",
                "reference": "1003020496",
                "webhook_url": "https://yourwebsite.com/webhook",
                "metadata": {
                    "product_id": "12345",
                    "color": "blue",
                    "size": "L",
                    "custom_notes": "Please gift-wrap this item.",
                },
                "created_at": "2025-06-15T10:00:00Z",
                "updated_at": "2025-06-15T10:05:00Z",
                "completed_at": "2025-06-15T10:05:00Z",
            }
        }
    )


class OrderResponse(BaseModel):
    """Response model for order operations."""

    status: str = Field("success", description="Status of the operation (success or error)")
    message: str = Field(
        "Order created successfully",
        description="Message describing the operation result",
    )
    order_id: str = Field(..., description="ID of the created or updated order")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Order created successfully",
                "order_id": "66c4bb9c9abb1",
            }
        }
    )


class OrderStatusResponse(BaseModel):
    status: str = Field("success", description="Status of the operation (success or error)")
    order_id: str = Field(..., description="ID of the order")
    message: str = Field(
        "Order status retrieved successfully",
        description="Message describing the operation result",
    )
    payment_status: str = Field("PENDING", description="Current payment status of the order")


class OrderListParams(BaseModel):
    """Parameters for listing orders."""

    status: Optional[str] = Field(None, description="Filter by payment status")
    buyer_email: Optional[str] = Field(None, description="Filter by buyer email")
    date_from: Optional[Union[datetime, str]] = Field(None, description="Filter orders from this date")
    date_to: Optional[Union[datetime, str]] = Field(None, description="Filter orders to this date")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Number of orders to return")

    @field_validator("status")
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status filter."""
        if v is not None:
            valid_statuses = ["PENDING", "COMPLETED", "FAILED", "CANCELLED"]
            if v not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("date_from", mode="before")
    def parse_date_from(cls, v: Union[str, datetime, None]) -> Union[datetime, None]:
        """Parse string dates to datetime objects for date_from."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                try:
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {v}")
        return v

    @field_validator("date_to", mode="before")
    def parse_date_to(cls, v: Union[str, datetime, None]) -> Union[datetime, None]:
        """Parse string dates to datetime objects for date_to."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                try:
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {v}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "COMPLETED",
                "buyer_email": "jackson@gmail.com",
                "date_from": "2025-06-01",
                "date_to": "2025-06-15",
                "limit": 50,
            }
        }
    )
