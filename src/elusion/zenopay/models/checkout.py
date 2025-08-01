from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from elusion.zenopay.models import Currency


class NewCheckout(BaseModel):
    """Model for creating a new checkout."""

    buyer_email: str = Field(..., description="Buyer's email address")
    buyer_name: str = Field(..., description="Buyer's full name")
    buyer_phone: str = Field(..., description="Buyer's phone number")
    amount: int = Field(..., gt=0, description="Order amount in smallest currency unit")
    currency: Currency = Field(..., description="Currency code for the checkout")
    redirect_url: str = Field(..., description="URL to redirect when payment is done", max_length=500)

    @field_validator("redirect_url")
    @classmethod
    def validate_redirect_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate redirect URL format."""
        if v is not None and v.strip():
            v = v.strip()
            if not (v.startswith("http://") or v.startswith("https://")):
                raise ValueError("Redirect URL must start with http:// or https://")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "buyer_email": "amarakofi@gmail.com",
                "buyer_name": "Amara Kofi",
                "buyer_phone": "06XXXXXXX",
                "amount": 1000,
                "currency": "TZS",
                "redirect_url": "https://example.com/redirect",
            }
        }
    )


class CheckoutResponse(BaseModel):
    """Response model for checkout creation."""

    payment_link: str = Field(..., description="URL for the payment page")
    tx_ref: str = Field(..., description="Transaction reference ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_link": "https://checkout.flutterwave.com/v3/hosted/pay/flwlnk-01k1e5mjmb01crqpthc2a5d2mv",
                "tx_ref": "TX-66c4bb9c9abb1_12345",
            }
        }
    )
