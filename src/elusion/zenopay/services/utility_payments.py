"""Utility Payments service for the ZenoPay SDK"""

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse
from elusion.zenopay.models.utility_payments import (
    NewUtilityPayment,
    UtilityPaymentResponse,
)
from elusion.zenopay.services.base import BaseService


class UtilityPaymentsSyncMethods(BaseService):
    """Sync methods for UtilityPaymentsService"""

    def process_payment(self, payment_data: NewUtilityPayment) -> APIResponse[UtilityPaymentResponse]:
        """Process utility payment (sync).

        Args:
            payment_data: Utility payment data with service details and customer reference.

        Returns:
            Utility payment response with transaction details and status.
        """
        return self.post_sync("utility-payments", payment_data, UtilityPaymentResponse)


class UtilityPaymentsService(BaseService):
    """Service for processing utility payments (airtime, electricity, TV, internet, etc.)."""

    def __init__(self, http_client: HTTPClient, config: ZenoPayConfig):
        """Initialize UtilityPaymentsService with sync namespace."""
        super().__init__(http_client, config)
        self.sync = UtilityPaymentsSyncMethods(http_client, config)

    async def process_payment(self, payment_data: NewUtilityPayment) -> APIResponse[UtilityPaymentResponse]:
        """Process utility payment (async).

        Args:
            payment_data: Utility payment data with service details and customer reference.

        Returns:
            Utility payment response with transaction details and status.
        """
        return await self.post_async("utility-payments", payment_data, UtilityPaymentResponse)
