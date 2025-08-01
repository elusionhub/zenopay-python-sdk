"""Configuration and constants for the ZenoPay SDK."""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "https://zenoapi.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# Environment variable names
ENV_API_KEY = "ZENOPAY_API_KEY"
ENV_BASE_URL = "ZENOPAY_BASE_URL"
ENV_TIMEOUT = "ZENOPAY_TIMEOUT"

# HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": "zenopay-python-sdk",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# API endpoints
ENDPOINTS = {
    "create_order": "/api/payments/mobile_money_tanzania",
    "checkout": "/api/payments/checkout/",
    "order_status": "/api/payments/order-status",
    "disbursement": "/api/payments/walletcashin/process/",
    "utility-payments": "/api/payments/utilitypayment/process/",
}

# Payment statuses
PAYMENT_STATUSES = {
    "PENDING": "PENDING",
    "COMPLETED": "COMPLETED",
    "FAILED": "FAILED",
    "CANCELLED": "CANCELLED",
}


class ZenoPayConfig:
    """Configuration class for the ZenoPay SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize configuration.

        Args:
            api_key: ZenoPay API key. If not provided, will try to get from environment.
            base_url: Base URL for the ZenoPay API.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            retry_delay: Delay between retries in seconds.
            headers: Additional headers to include in requests.
        """
        self.api_key = os.getenv(ENV_API_KEY) or api_key

        if not self.api_key:
            raise ValueError(f"API key is required. Set {ENV_API_KEY} environment variable " "or pass api_key parameter.")

        self.base_url = os.getenv(ENV_BASE_URL) or base_url or DEFAULT_BASE_URL

        # Parse timeout from environment if provided
        env_timeout = os.getenv(ENV_TIMEOUT)
        if env_timeout:
            try:
                env_timeout_float = float(env_timeout)
            except ValueError:
                env_timeout_float = DEFAULT_TIMEOUT
        else:
            env_timeout_float = DEFAULT_TIMEOUT

        self.timeout = timeout or env_timeout_float
        self.max_retries = max_retries or DEFAULT_MAX_RETRIES
        self.retry_delay = retry_delay or DEFAULT_RETRY_DELAY

        self.headers = DEFAULT_HEADERS.copy()

        if self.api_key:
            self.headers["x-api-key"] = self.api_key

        # Add any additional custom headers
        if headers:
            self.headers.update(headers)

    def get_endpoint_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint.

        Args:
            endpoint: Endpoint key from ENDPOINTS dict.

        Returns:
            Full URL for the endpoint.

        Raises:
            ValueError: If endpoint is not found in ENDPOINTS.
        """
        if endpoint not in ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint}. Available endpoints: {list(ENDPOINTS.keys())}")

        endpoint_path = ENDPOINTS[endpoint]
        if endpoint_path:
            return f"{self.base_url.rstrip('/')}{endpoint_path}"
        else:
            return self.base_url

    def __repr__(self) -> str:
        """String representation of the config."""
        # Mask API key for security
        masked_api_key = f"{self.api_key[:8]}..." if self.api_key and len(self.api_key) > 8 else self.api_key
        return f"ZenoPayConfig(api_key='{masked_api_key}', base_url='{self.base_url}')"
