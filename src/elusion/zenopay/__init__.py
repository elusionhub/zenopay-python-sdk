"""ZenoPay SDK for Python.

A modern Python SDK for the ZenoPay payment API with support for USSD payments,
checkout sessions, order management, and webhook handling.
"""

__version__ = "0.4.1"
__author__ = "Elution Hub"
__email__ = "elusion.lab@gmail.com"

from elusion.zenopay.client import ZenoPayClient as ZenoPay
from elusion.zenopay.exceptions import (
    ZenoPayError,
    ZenoPayAPIError,
    ZenoPayAuthenticationError,
    ZenoPayValidationError,
    ZenoPayNetworkError,
)
from elusion.zenopay.models import (
    Order,
    NewOrder,
    OrderStatus,
    WebhookEvent,
    WebhookPayload,
    Currency,
)
from elusion.zenopay.models.checkout import (
    NewCheckout,
    CheckoutResponse,
)

__all__ = [
    # Main client
    "ZenoPay",
    # Exceptions
    "ZenoPayError",
    "ZenoPayAPIError",
    "ZenoPayAuthenticationError",
    "ZenoPayValidationError",
    "ZenoPayNetworkError",
    # Models
    "Order",
    "NewOrder",
    "OrderStatus",
    "WebhookEvent",
    "WebhookPayload",
    "Currency",
    # Checkout models
    "NewCheckout",
    "CheckoutResponse",
]
