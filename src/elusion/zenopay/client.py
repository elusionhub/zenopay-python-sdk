"""Main client for the ZenoPay SDK."""

from typing import Optional, Type
from types import TracebackType

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.services import (
    OrderService,
    WebhookService,
    DisbursementService,
    UtilityPaymentsService,
    CheckoutService,
)


class ZenoPayClient:
    """Main client for interacting with the ZenoPay API.

    This client provides access to all ZenoPay services including order management,
    payment processing, checkout sessions, and webhook handling. It supports both async and sync operations.

    Examples:
        Basic usage:
        >>> client = ZenoPayClient(api_key="your-api-key")

        Async usage:
        >>> async with ZenoPayClient(api_key="your-api-key") as client:
        ...     order = await client.orders.create({
        ...         "buyer_email": "example@example.xyz",
        ...         "buyer_name": "example name",
        ...         "buyer_phone": "06XXXXXXXX",
        ...         "amount": 1000,
        ...         "webhook_url": "https://example.xyz/webhook"
        ...     })

        Sync usage:
        >>> with ZenoPayClient(api_key="your-api-key") as client:
        ...     order = client.orders.sync.create({
        ...         "buyer_email": "example@example.xyz",
        ...         "buyer_name": "example name",
        ...         "buyer_phone": "06XXXXXXXX",
        ...         "amount": 1000
        ...     })

        Checkout usage:
        >>> checkout = await client.checkout.create_checkout({
        ...     "buyer_email": "example@example.xyz",
        ...     "buyer_name": "example name",
        ...     "buyer_phone": "06XXXXXXXX",
        ...     "amount": 1000,
        ...     "currency": "TZS",
        ...     "redirect_url": "https://example.xyz/success"
        ... })
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        """Initialize the ZenoPay client.

        Args:
            api_key: API key (optional, can be set via environment variable).
            base_url: Base URL for the API (optional, defaults to production).
            timeout: Request timeout in seconds (optional).
            max_retries: Maximum number of retries for failed requests (optional).
        """
        self.config = ZenoPayConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.http_client = HTTPClient(self.config)

        self.orders = OrderService(self.http_client, self.config)
        self.checkout = CheckoutService(self.http_client, self.config)
        self.disbursements = DisbursementService(self.http_client, self.config)
        self.utilities = UtilityPaymentsService(self.http_client, self.config)
        self.webhooks = WebhookService()

    async def __aenter__(self) -> "ZenoPayClient":
        """Enter async context manager."""
        await self.http_client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context manager."""
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    def __enter__(self) -> "ZenoPayClient":
        """Enter sync context manager."""
        self.http_client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit sync context manager."""
        self.http_client.__exit__(exc_type, exc_val, exc_tb)

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self.http_client.close()

    def close_sync(self) -> None:
        """Close the client and cleanup resources (sync version)."""
        self.http_client.close_sync()

    @property
    def api_key(self) -> str:
        """Get the current API key."""
        return self.config.api_key or ""

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self.config.base_url

    def get_config(self) -> ZenoPayConfig:
        """Get the current configuration."""
        return self.config

    def __repr__(self) -> str:
        """String representation of the client."""
        masked_key = f"{self.api_key[:8]}..." if self.api_key and len(self.api_key) > 8 else "***"
        return f"ZenoPayClient(api_key='{masked_key}', base_url='{self.base_url}')"
