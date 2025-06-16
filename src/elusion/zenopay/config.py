"""Configuration and constants for the ZenoPay SDK."""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default configuration
DEFAULT_BASE_URL = "https://api.zeno.africa"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# Environment variable names
ENV_API_KEY = "ZENOPAY_API_KEY"
ENV_SECRET_KEY = "ZENOPAY_SECRET_KEY"
ENV_ACCOUNT_ID = "ZENOPAY_ACCOUNT_ID"
ENV_BASE_URL = "ZENOPAY_BASE_URL"
ENV_TIMEOUT = "ZENOPAY_TIMEOUT"

# HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": "zenopay-python-sdk",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}

# API endpoints
ENDPOINTS = {
    "create_order": "",
    "order_status": "/order-status",
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
        secret_key: Optional[str] = None,
        account_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize configuration.

        Args:
            api_key: ZenoPay API key. If not provided, will try to get from environment.
            secret_key: ZenoPay secret key. If not provided, will try to get from environment.
            account_id: ZenoPay account ID. If not provided, will try to get from environment.
            base_url: Base URL for the ZenoPay API.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            retry_delay: Delay between retries in seconds.
            headers: Additional headers to include in requests.
        """
        self.api_key = api_key or os.getenv(ENV_API_KEY)
        self.secret_key = secret_key or os.getenv(ENV_SECRET_KEY)
        self.account_id = account_id or os.getenv(ENV_ACCOUNT_ID)

        if not self.account_id:
            raise ValueError(f"Account ID is required. Set {ENV_ACCOUNT_ID} environment variable " "or pass account_id parameter.")

        self.base_url = base_url or os.getenv(ENV_BASE_URL, DEFAULT_BASE_URL)

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

        # Merge default headers with custom headers
        self.headers = DEFAULT_HEADERS.copy()
        if headers:
            self.headers.update(headers)

    def get_endpoint_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint.

        Args:
            endpoint: Endpoint key from ENDPOINTS dict.

        Returns:
            Full URL for the endpoint.
        """
        if endpoint not in ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        endpoint_path = ENDPOINTS[endpoint]
        if endpoint_path:
            return f"{self.base_url.rstrip('/')}{endpoint_path}"
        else:
            # For create_order, the base URL is the endpoint
            return self.base_url
