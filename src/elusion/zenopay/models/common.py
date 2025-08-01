"""Common models and types used across the ZenoPay SDK."""

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    success: bool = Field(..., description="Whether the request was successful")
    results: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if applicable")


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")


class ValidationError(BaseModel):
    """Validation error response."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="General error message")
    errors: List[ErrorDetail]


class ZenoPayAPIRequest(BaseModel):
    """Base model for ZenoPay API requests."""

    def to_form_data(self) -> dict[str, str]:
        """Convert to form data format as expected by ZenoPay API."""
        data = self.model_dump(exclude_unset=True, by_alias=True)

        form_data: dict[str, str] = {}
        for key, value in data.items():
            if value is not None:
                form_data[key] = str(value)

        return form_data


class StatusCheckRequest(ZenoPayAPIRequest):
    """Request model for checking order status."""

    order_id: str = Field(..., description="Order ID to check")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "66c4bb9c9abb1",
            }
        }
    )


class UtilityCodes(str, Enum):
    """Uility codes"""

    CASHIN = "CASHIN"

    def __str__(self) -> str:
        """String representation of the utility codes."""
        return self.value


class Currency(str, Enum):
    """Supported currency codes."""

    USD = "USD"  # US Dollar
    TZS = "TZS"  # Tanzanian Shilling
    GBP = "GBP"  # British Pound
    EUR = "EUR"  # Euro
    NGN = "NGN"  # Nigerian Naira
    KES = "KES"  # Kenyan Shilling
    UGX = "UGX"  # Ugandan Shilling
    ZAR = "ZAR"  # South African Rand
    INR = "INR"  # Indian Rupee
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    SAR = "SAR"  # Saudi Riyal
    AED = "AED"  # Emirati Dirham
    CNY = "CNY"  # Chinese Yuan
    JPY = "JPY"  # Japanese Yen

    def __str__(self) -> str:
        """String representation of the currency code."""
        return self.value


PAYMENT_STATUSES = {
    "PENDING": "PENDING",
    "COMPLETED": "COMPLETED",
    "FAILED": "FAILED",
    "CANCELLED": "CANCELLED",
}

MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 255
MAX_PHONE_LENGTH = 20
MAX_WEBHOOK_URL_LENGTH = 500
MAX_METADATA_LENGTH = 1000
