"""Disbursement service for the ZenoPay SDK"""

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse
from elusion.zenopay.models.disbursement import (
    NewDisbursement,
    DisbursementSuccessResponse,
)
from elusion.zenopay.services.base import BaseService


class DisbursementSyncMethods(BaseService):
    """Sync methods for DisbursementService - inherits from BaseService for direct access."""

    def disburse(self, disbursement_data: NewDisbursement) -> APIResponse[DisbursementSuccessResponse]:
        """Send money to mobile wallet (sync).

        Args:
            disbursement_data: Disbursement data with recipient details.

        Returns:
            Disbursement response with transaction details and fees.
        """
        return self.post_sync("disbursement", disbursement_data, DisbursementSuccessResponse)


class DisbursementService(BaseService):
    """Service for sending money to mobile wallets."""

    def __init__(self, http_client: HTTPClient, config: ZenoPayConfig):
        """Initialize DisbursementService with sync namespace."""
        super().__init__(http_client, config)
        self.sync = DisbursementSyncMethods(http_client, config)

    async def disburse(self, disbursement_data: NewDisbursement) -> APIResponse[DisbursementSuccessResponse]:
        """Send money to mobile wallet (async).

        Args:
            disbursement_data: Disbursement data with recipient details.

        Returns:
            Disbursement response with transaction details and fees.
        """
        return await self.post_async("disbursement", disbursement_data, DisbursementSuccessResponse)
