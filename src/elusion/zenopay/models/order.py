"""Order-related models for the ZenoPay SDK."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderBase(BaseModel):
    """Base order model with common fields."""

    order_id: str = Field(..., description="Unique order id")
    buyer_email: str = Field(..., description="Buyer's email address")
    buyer_name: str = Field(..., description="Buyer's full name")
    buyer_phone: str = Field(..., description="Buyer's phone number")
    amount: int = Field(..., gt=0, description="Order amount in smallest currency unit")
    webhook_url: Optional[str] = Field(default=None, description="URL to receive webhook notifications")

    @field_validator("buyer_email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("buyer_phone")
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
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

    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional order metadata")

    @field_validator("metadata")
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Keep metadata as dict, convert to JSON only when needed."""
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "buyer_email": "amarakofi@gmail.com",
                "buyer_name": "Amara Kofi",
                "buyer_phone": "06XXXXXXX",
                "amount": 1000,
                "webhook_url": "https://example.com/webhook",
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
                "buyer_email": "amarakofi@gmail.com",
                "buyer_name": "Amara Kofi",
                "buyer_phone": "06XXXXXXX",
                "amount": 1000,
                "payment_status": "COMPLETED",
                "reference": "1003020496",
                "webhook_url": "https://example.com/webhook",
                "metadata": {
                    "product_id": "12345",
                    "color": "blue",
                    "size": "L",
                    "custom_notes": "Please gift-wrap this item.",
                },
            }
        }
    )


class OrderResponse(BaseModel):
    """Response model for order operations."""

    status: str
    message: str
    resultcode: int
    order_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "2cd93967-0d48-46c7-a9ab-f0a0a21a11cd",
                "resultcode": "000",
                "status": "success",
                "message": "Order created successfully",
            }
        }
    )


class OrderData(BaseModel):
    order_id: str
    creation_date: str
    amount: str
    payment_status: str
    transid: Optional[str] = None
    channel: Optional[str] = None
    reference: Optional[str] = None
    msisdn: Optional[str] = None


class OrderStatusResponse(BaseModel):
    reference: str
    resultcode: str
    result: str
    message: str
    data: List[OrderData]
