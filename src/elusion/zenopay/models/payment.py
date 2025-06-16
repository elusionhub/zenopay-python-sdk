"""Payment models for the ZenoPay SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentStatus(str, Enum):
    """Enumeration of payment statuses."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    @classmethod
    def from_string(cls, status: str) -> "PaymentStatus":
        """Create PaymentStatus from string.

        Args:
            status: Status string.

        Returns:
            PaymentStatus enum value.

        Raises:
            ValueError: If status is invalid.
        """
        try:
            return cls(status.upper())
        except ValueError:
            raise ValueError(f"Invalid payment status: {status}")

    @property
    def is_final(self) -> bool:
        """Check if this is a final status (completed, failed, or cancelled)."""
        return self in (self.COMPLETED, self.FAILED, self.CANCELLED)

    @property
    def is_successful(self) -> bool:
        """Check if this represents a successful payment."""
        return self == self.COMPLETED

    def __str__(self) -> str:
        """String representation of the status."""
        return self.value


class PaymentMethod(str, Enum):
    """Enumeration of payment methods."""

    USSD = "USSD"
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"

    def __str__(self) -> str:
        """String representation of the payment method."""
        return self.value


class PaymentProvider(str, Enum):
    """Enumeration of payment providers."""

    VODACOM = "VODACOM"
    AIRTEL = "AIRTEL"
    TIGO = "TIGO"
    HALOPESA = "HALOPESA"
    OTHER = "OTHER"

    def __str__(self) -> str:
        """String representation of the payment provider."""
        return self.value


class PaymentBase(BaseModel):
    """Base payment model with common fields."""

    amount: int = Field(..., gt=0, description="Payment amount in smallest currency unit")
    currency: str = Field("TZS", description="Payment currency code")
    reference: Optional[str] = Field(None, description="Payment reference number")
    status: PaymentStatus = Field(PaymentStatus.PENDING, description="Payment status")

    @field_validator("currency")
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        valid_currencies = ["TZS", "USD", "EUR", "KES", "UGX"]
        if v.upper() not in valid_currencies:
            raise ValueError(f"Invalid currency. Must be one of: {', '.join(valid_currencies)}")
        return v.upper()

    @field_validator("status", mode="before")
    def validate_status(cls, v: str) -> PaymentStatus:
        """Validate and convert payment status."""
        return PaymentStatus.from_string(v)


class Payment(PaymentBase):
    """Complete payment model with all fields."""

    # Order relationship
    order_id: str = Field(..., description="Associated order ID")

    # Payment details
    method: Optional[PaymentMethod] = Field(None, description="Payment method used")
    provider: Optional[PaymentProvider] = Field(None, description="Payment provider")
    provider_reference: Optional[str] = Field(None, description="Provider's reference number")

    # Customer details
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    customer_email: Optional[str] = Field(None, description="Customer email address")

    # Transaction details
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")

    # Fees and charges
    fee_amount: Optional[int] = Field(None, description="Transaction fee amount")
    net_amount: Optional[int] = Field(None, description="Net amount after fees")

    # Timestamps
    initiated_at: Optional[datetime] = Field(None, description="Payment initiation time")
    completed_at: Optional[datetime] = Field(None, description="Payment completion time")
    failed_at: Optional[datetime] = Field(None, description="Payment failure time")
    expires_at: Optional[datetime] = Field(None, description="Payment expiration time")

    # Error information
    error_code: Optional[str] = Field(None, description="Error code if payment failed")
    error_message: Optional[str] = Field(None, description="Error message if payment failed")

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED

    @property
    def is_cancelled(self) -> bool:
        """Check if payment was cancelled."""
        return self.status == PaymentStatus.CANCELLED

    @property
    def is_final(self) -> bool:
        """Check if payment is in a final state."""
        return self.status.is_final

    @property
    def formatted_amount(self) -> str:
        """Get formatted amount string."""
        if self.currency == "TZS":
            return f"{self.amount:,} {self.currency}"
        else:
            amount_decimal = self.amount / 100
            return f"{amount_decimal:.2f} {self.currency}"

    @property
    def formatted_net_amount(self) -> str:
        """Get formatted net amount string."""
        if self.net_amount is None:
            return self.formatted_amount

        if self.currency == "TZS":
            return f"{self.net_amount:,} {self.currency}"
        else:
            net_decimal = self.net_amount / 100
            return f"{net_decimal:.2f} {self.currency}"

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from the metadata."""
        if self.metadata:
            return self.metadata.get(key, default)
        return default

    def calculate_fee_percentage(self) -> Optional[float]:
        """Calculate fee as percentage of total amount."""
        if self.fee_amount is None or self.amount <= 0:
            return None
        return (self.fee_amount / self.amount) * 100

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "pay_677e43274d7cb",
                "order_id": "ord_677e43274d7cb",
                "amount": 1000,
                "currency": "TZS",
                "status": "COMPLETED",
                "reference": "1003020496",
                "method": "USSD",
                "provider": "VODACOM",
                "provider_reference": "MP240615001",
                "customer_phone": "0652449389",
                "customer_email": "jackson@gmail.com",
                "description": "Payment for Order #12345",
                "fee_amount": 50,
                "net_amount": 950,
                "initiated_at": "2025-06-15T10:00:00Z",
                "completed_at": "2025-06-15T10:05:00Z",
                "created_at": "2025-06-15T10:00:00Z",
                "updated_at": "2025-06-15T10:05:00Z",
                "metadata": {"product_id": "12345", "campaign": "summer_sale"},
            }
        }
    )


class PaymentCreate(PaymentBase):
    """Model for creating a new payment."""

    order_id: str = Field(..., description="Associated order ID")
    method: Optional[PaymentMethod] = Field(None, description="Preferred payment method")
    provider: Optional[PaymentProvider] = Field(None, description="Preferred payment provider")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")

    @field_validator("customer_phone")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is not None:
            # Remove any non-digit characters except +
            cleaned = "".join(c for c in v if c.isdigit() or c == "+")
            if len(cleaned) < 10:
                raise ValueError("Phone number must be at least 10 digits")
            return cleaned
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_677e43274d7cb",
                "amount": 1000,
                "currency": "TZS",
                "method": "USSD",
                "provider": "VODACOM",
                "customer_phone": "0652449389",
                "description": "Payment for Order #12345",
                "metadata": {"product_id": "12345", "campaign": "summer_sale"},
            }
        }
    )


class PaymentSearch(BaseModel):
    """Model for searching payments."""

    order_id: Optional[str] = Field(None, description="Filter by order ID")
    status: Optional[PaymentStatus] = Field(None, description="Filter by payment status")
    method: Optional[PaymentMethod] = Field(None, description="Filter by payment method")
    provider: Optional[PaymentProvider] = Field(None, description="Filter by payment provider")
    reference: Optional[str] = Field(None, description="Filter by payment reference")
    customer_phone: Optional[str] = Field(None, description="Filter by customer phone")
    date_from: Optional[Union[datetime, str]] = Field(None, description="Filter from date")
    date_to: Optional[Union[datetime, str]] = Field(None, description="Filter to date")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Number of results to return")

    @field_validator("date_from", mode="before")
    def parse_date_from(cls, v: Union[str, datetime, None]) -> Union[datetime, None]:
        """Parse string dates to datetime objects."""
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
        """Parse string dates to datetime objects."""
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
                "method": "USSD",
                "date_from": "2025-06-01",
                "date_to": "2025-06-15",
                "limit": 50,
            }
        }
    )
