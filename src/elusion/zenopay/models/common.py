"""Common models and types used across the ZenoPay SDK."""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    success: bool = Field(..., description="Whether the request was successful")
    data: T = Field(..., description="Response data")
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

    api_key: Optional[str] = Field(None, description="API key (usually null in requests)")
    secret_key: Optional[str] = Field(None, description="Secret key (usually null in requests)")
    account_id: str = Field(..., description="ZenoPay account ID")

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

    check_status: int = Field(1, description="Always 1 for status check requests")
    order_id: str = Field(..., description="Order ID to check")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "check_status": 1,
                "order_id": "66c4bb9c9abb1",
                "account_id": "zp87778",
                "api_key": "null",
                "secret_key": "null",
            }
        }
    )


# Common status constants
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
