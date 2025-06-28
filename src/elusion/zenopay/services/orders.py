"""Order service for the ZenoPay SDK"""

from typing import Any, Dict, Union

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse
from elusion.zenopay.models.order import (
    NewOrder,
    OrderResponse,
    OrderStatusResponse,
)
from elusion.zenopay.services.base import BaseService


class OrderSyncMethods(BaseService):
    """Sync methods for OrderService - inherits from BaseService for direct access."""

    def create(self, order_data: NewOrder) -> APIResponse[OrderResponse]:
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
        return self.post_sync("create_order", order_data, OrderResponse)

    def check_status(self, order_id: str) -> APIResponse[OrderStatusResponse]:
        """Check the status of an existing order using GET request (sync).

        Args:
            order_id: The order ID to check status for.

        Returns:
            Order status response with payment details.
        """
        params: Dict[str, Any] = {
            "order_id": order_id,
        }
        return self.get_sync("order_status", OrderStatusResponse, params=params)

    def check_payment(self, order_id: str) -> bool:
        """Check if an order has been paid (sync)."""
        try:
            status_response = self.check_status(order_id)
            return status_response.results.data[0].payment_status == "COMPLETED"
        except Exception:
            return False

    def wait_for_payment(self, order_id: str, timeout: int = 300, poll_interval: int = 10) -> APIResponse[OrderStatusResponse]:
        """Wait for an order to be paid (sync)."""
        import time

        start_time = time.time()

        while True:
            status_response = self.check_status(order_id)

            if status_response.results.data[0].payment_status == "COMPLETED":
                return status_response

            if status_response.results.data[0].payment_status == "FAILED":
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
        """Create a new order and initiate USSD payment (async).

        Args:
            order_data: Order creation data.

        Returns:
            Created order response with order_id and status.
        """
        return await self.post_async("create_order", order_data, OrderResponse)

    async def check_status(self, order_id: str) -> APIResponse[OrderStatusResponse]:
        """Check the status of an existing order using GET request (async).

        Args:
            order_id: The order ID to check status for.

        Returns:
            Order status response with payment details.
        """
        params: Dict[str, Any] = {
            "order_id": order_id,
        }
        return await self.get_async("order_status", OrderStatusResponse, params=params)

    async def check_payment(self, order_id: str) -> bool:
        """Check if an order has been paid (async)."""
        try:
            status_response = await self.check_status(order_id)
            return status_response.results.data[0].payment_status == "COMPLETED"
        except Exception:
            return False

    async def wait_for_payment(self, order_id: str, timeout: int = 300, poll_interval: int = 10) -> APIResponse[OrderStatusResponse]:
        """Wait for an order to be paid (async)."""
        import asyncio

        start_time = asyncio.get_event_loop().time()

        while True:
            status_response = await self.check_status(order_id)

            if status_response.results.data[0].payment_status == "COMPLETED":
                return status_response

            if status_response.results.data[0].payment_status == "FAILED":
                raise Exception(f"Payment failed for order {order_id}")

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Payment timeout after {timeout} seconds")

            await asyncio.sleep(poll_interval)
