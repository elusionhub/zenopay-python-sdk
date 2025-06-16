"""Order service for the ZenoPay SDK"""

from typing import Dict, Union

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse, StatusCheckRequest
from elusion.zenopay.models.order import (
    NewOrder,
    OrderResponse,
    OrderStatusResponse,
)
from elusion.zenopay.services.base import BaseService


class OrderSyncMethods(BaseService):
    """Sync methods for OrderService - inherits from BaseService for direct access."""

    def create(self, order_data: Union[NewOrder, Dict[str, str]]) -> APIResponse[OrderResponse]:
        """Create a new order and initiate USSD payment (sync).

        Args:
            order_data: Order creation data.

        Returns:
            Created order response with order_id and status.

        Examples:
            >>> with zenopay_client:
            ...     response = zenopay_client.orders.sync.create(order_data)
            ...     print(f"Order created: {response.data.order_id}")
        """
        # ✅ Direct access to post_sync - no parent needed
        return self.post_sync("create_order", order_data, OrderResponse)

    def get_status(self, order_id: str) -> APIResponse[OrderStatusResponse]:
        """Check the status of an existing order (sync).

        Args:
            order_id: The order ID to check status for.

        Returns:
            Order status response with payment details.
        """
        status_request = StatusCheckRequest(
            order_id=order_id,
            api_key=self.config.api_key,
            secret_key=self.config.secret_key,
            account_id=self.config.account_id or "",
            check_status=1,
        )
        # ✅ Direct access - clean and simple
        return self.post_sync("order_status", status_request, OrderStatusResponse)

    def check_payment(self, order_id: str) -> bool:
        """Check if an order has been paid (sync)."""
        try:
            status_response = self.get_status(order_id)
            return status_response.data.payment_status == "COMPLETED"
        except Exception:
            return False

    def wait_for_payment(self, order_id: str, timeout: int = 300, poll_interval: int = 10) -> APIResponse[OrderStatusResponse]:
        """Wait for an order to be paid (sync)."""
        import time

        start_time = time.time()

        while True:
            status_response = self.get_status(order_id)

            if status_response.data.payment_status == "COMPLETED":
                return status_response

            if status_response.data.payment_status == "FAILED":
                raise Exception(f"Payment failed for order {order_id}")

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Payment timeout after {timeout} seconds")

            time.sleep(poll_interval)


class OrderService(BaseService):
    """Service for managing orders and payments."""

    def __init__(self, http_client: HTTPClient, config: ZenoPayConfig):
        """Initialize OrderService with sync namespace."""
        super().__init__(http_client, config)
        self.sync = OrderSyncMethods(http_client, config)

    async def create(self, order_data: Union[NewOrder, Dict[str, str]]) -> APIResponse[OrderResponse]:
        """Create a new order and initiate USSD payment."""
        return await self._post("create_order", order_data, OrderResponse)

    async def get_status(self, order_id: str) -> APIResponse[OrderStatusResponse]:
        """Check the status of an existing order."""
        status_request = StatusCheckRequest(
            order_id=order_id,
            api_key=self.config.api_key,
            secret_key=self.config.secret_key,
            account_id=self.config.account_id or "",
            check_status=1,
        )
        return await self._post("order_status", status_request, OrderStatusResponse)

    async def check_payment(self, order_id: str) -> bool:
        """Check if an order has been paid."""
        try:
            status_response = await self.get_status(order_id)
            return status_response.data.payment_status == "COMPLETED"
        except Exception:
            return False

    async def wait_for_payment(self, order_id: str, timeout: int = 300, poll_interval: int = 10) -> APIResponse[OrderStatusResponse]:
        """Wait for an order to be paid."""
        import asyncio

        start_time = asyncio.get_event_loop().time()

        while True:
            status_response = await self.get_status(order_id)

            if status_response.data.payment_status == "COMPLETED":
                return status_response

            if status_response.data.payment_status == "FAILED":
                raise Exception(f"Payment failed for order {order_id}")

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Payment timeout after {timeout} seconds")

            await asyncio.sleep(poll_interval)
