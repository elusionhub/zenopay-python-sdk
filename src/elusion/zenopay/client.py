"""Main client for the ZenoPay SDK."""

import logging
from typing import Optional, Type
from types import TracebackType

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.services import OrderService
from elusion.zenopay.services import WebhookService

logger = logging.getLogger(__name__)


class ZenoPayClient:
    """Main client for interacting with the ZenoPay API.

    This client provides access to all ZenoPay services including order management,
    payment processing, and webhook handling. It supports both async and sync operations.

    Examples:
        Basic usage:
        >>> client = ZenoPayClient(account_id="zp87778")

        Async usage:
        >>> async with ZenoPayClient(account_id="zp87778") as client:
        ...     order = await client.orders.create({
        ...         "buyer_email": "jackson@gmail.com",
        ...         "buyer_name": "Jackson Dastani",
        ...         "buyer_phone": "0652449389",
        ...         "amount": 1000,
        ...         "webhook_url": "https://yourwebsite.com/webhook"
        ...     })

        Sync usage:
        >>> with ZenoPayClient(account_id="zp87778") as client:
        ...     order = client.orders.create_sync({
        ...         "buyer_email": "jackson@gmail.com",
        ...         "buyer_name": "Jackson Dastani",
        ...         "buyer_phone": "0652449389",
        ...         "amount": 1000
        ...     })
    """

    def __init__(
        self,
        account_id: str,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        """Initialize the ZenoPay client.

        Args:
            account_id: Your ZenoPay account ID (required).
            api_key: API key (optional, can be set via environment variable).
            secret_key: Secret key (optional, can be set via environment variable).
            base_url: Base URL for the API (optional, defaults to production).
            timeout: Request timeout in seconds (optional).
            max_retries: Maximum number of retries for failed requests (optional).
            **kwargs: Additional configuration options.

        Examples:
            >>> # Using environment variables for API keys
            >>> client = ZenoPayClient(account_id="zp87778")

            >>> # Explicit configuration
            >>> client = ZenoPayClient(
            ...     account_id="zp87778",
            ...     api_key="your_api_key",
            ...     secret_key="your_secret_key",
            ...     timeout=30.0
            ... )
        """
        self.config = ZenoPayConfig(
            account_id=account_id,
            api_key=api_key,
            secret_key=secret_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.http_client = HTTPClient(self.config)

        # Initialize services
        self.orders = OrderService(self.http_client, self.config)
        self.webhooks = WebhookService()

        logger.info(f"ZenoPay client initialized for account: {account_id}")

    async def __aenter__(self) -> "ZenoPayClient":
        """Async context manager entry."""
        await self.http_client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Async context manager exit."""
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    def __enter__(self) -> "ZenoPayClient":
        """Sync context manager entry."""
        self.http_client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Sync context manager exit."""
        self.http_client.__exit__(exc_type, exc_val, exc_tb)

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self.http_client.close()

    def close_sync(self) -> None:
        """Close the client and cleanup resources (sync version)."""
        self.http_client.close_sync()

    def test_connection(self) -> bool:
        """Test the connection to ZenoPay API.

        Returns:
            True if connection is successful, False otherwise.

        Examples:
            >>> client = ZenoPayClient(account_id="zp87778")
            >>> if client.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            self.orders.get_status_sync("test-connection-check")
            return True
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    async def test_connection_async(self) -> bool:
        """Test the connection to ZenoPay API (async version).

        Returns:
            True if connection is successful, False otherwise.

        Examples:
            >>> async with ZenoPayClient(account_id="zp87778") as client:
            ...     if await client.test_connection_async():
            ...         print("Connection successful!")
            ...     else:
            ...         print("Connection failed!")
        """
        try:
            await self.orders.get_status("test-connection-check")
            return True
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    @property
    def account_id(self) -> str:
        """Get the account ID."""
        return self.config.account_id or ""

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self.config.base_url

    def get_config(self) -> ZenoPayConfig:
        """Get the current configuration.

        Returns:
            Current ZenoPayConfig instance.
        """
        return self.config

    def update_config(self, **kwargs: object) -> None:
        """Update client configuration.

        Args:
            **kwargs: Configuration parameters to update.

        Examples:
            >>> client = ZenoPayClient(account_id="zp87778")
            >>> client.update_config(timeout=60.0, max_retries=5)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown configuration parameter: {key}")

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ZenoPayClient(account_id='{self.account_id}', base_url='{self.base_url}')"
