"""Checkout service for the ZenoPay SDK"""

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse
from elusion.zenopay.models.checkout import (
    NewCheckout,
    CheckoutResponse,
)
from elusion.zenopay.services.base import BaseService


class CheckoutSyncMethods(BaseService):
    """Sync methods for CheckoutService - inherits from BaseService for direct access."""

    def create(self, checkout_data: NewCheckout) -> APIResponse[CheckoutResponse]:
        """Create a new checkout session (sync).

        Args:
            checkout_data: Checkout data with buyer details and payment information.

        Returns:
            Checkout response with payment link and transaction reference.
        """
        return self.post_sync("checkout", checkout_data, CheckoutResponse)


class CheckoutService(BaseService):
    """Service for creating checkout sessions and payment links."""

    def __init__(self, http_client: HTTPClient, config: ZenoPayConfig):
        """Initialize CheckoutService with sync namespace."""
        super().__init__(http_client, config)
        self.sync = CheckoutSyncMethods(http_client, config)

    async def create(self, checkout_data: NewCheckout) -> APIResponse[CheckoutResponse]:
        """Create a new checkout session (async).

        Args:
            checkout_data: Checkout data with buyer details and payment information.

        Returns:
            Checkout response with payment link and transaction reference.
        """
        return await self.post_async("checkout", checkout_data, CheckoutResponse)
