"""HTTP client for the ZenoPay SDK."""

import logging
from typing import Any, Dict, Optional

import httpx

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.exceptions import (
    ZenoPayNetworkError,
    ZenoPayTimeoutError,
    create_api_error,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for making requests to the ZenoPay API."""

    def __init__(self, config: ZenoPayConfig) -> None:
        """Initialize the HTTP client.

        Args:
            config: ZenoPay configuration instance.
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __enter__(self) -> "HTTPClient":
        """Sync context manager entry."""
        self._ensure_sync_client()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sync context manager exit."""
        self.close_sync()

    async def _ensure_client(self) -> None:
        """Ensure async client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=self.config.headers.copy(),
            )

    def _ensure_sync_client(self) -> None:
        """Ensure sync client is initialized."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                timeout=self.config.timeout,
                headers=self.config.headers.copy(),
            )

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def close_sync(self) -> None:
        """Close the sync HTTP client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Request URL.
            data: Form data to send.
            headers: Additional headers.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.

        Raises:
            ZenoPayAPIError: For API errors.
            ZenoPayNetworkError: For network errors.
            ZenoPayTimeoutError: For timeout errors.
        """
        await self._ensure_client()

        request_headers = self.config.headers.copy()
        if headers:
            request_headers.update(headers)

        if data:
            cleaned_data = {}
            for key, value in data.items():
                if value is not None:
                    cleaned_data[key] = str(value)
            data = cleaned_data

        try:
            logger.debug(f"Making {method} request to {url}")

            if self._client is None:
                raise ZenoPayNetworkError("Async HTTP client is not initialized.", None)

            response = await self._client.request(
                method=method,
                url=url,
                data=data,
                headers=request_headers,
                **kwargs,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise ZenoPayTimeoutError(
                f"Request timeout after {self.config.timeout} seconds",
                self.config.timeout,
            ) from e
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise ZenoPayNetworkError(f"Network error: {str(e)}", e) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ZenoPayNetworkError(f"Unexpected error: {str(e)}", e) from e

    def request_sync(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a sync HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Request URL.
            data: Form data to send.
            headers: Additional headers.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.

        Raises:
            ZenoPayAPIError: For API errors.
            ZenoPayNetworkError: For network errors.
            ZenoPayTimeoutError: For timeout errors.
        """
        self._ensure_sync_client()

        request_headers = self.config.headers.copy()
        if headers:
            request_headers.update(headers)

        if data:
            cleaned_data = {}
            for key, value in data.items():
                if value is not None:
                    cleaned_data[key] = str(value)
            data = cleaned_data

        try:
            logger.debug(f"Making {method} request to {url}")

            if self._sync_client is None:
                raise ZenoPayNetworkError("Sync HTTP client is not initialized.", None)

            response = self._sync_client.request(
                method=method,
                url=url,
                data=data,
                headers=request_headers,
                **kwargs,
            )

            return self._handle_response_sync(response)

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise ZenoPayTimeoutError(
                f"Request timeout after {self.config.timeout} seconds",
                self.config.timeout,
            ) from e
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise ZenoPayNetworkError(f"Network error: {str(e)}", e) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ZenoPayNetworkError(f"Unexpected error: {str(e)}", e) from e

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response for async requests.

        Args:
            response: HTTP response object.

        Returns:
            Parsed response data.

        Raises:
            ZenoPayAPIError: For API errors.
        """
        logger.debug(f"Response status: {response.status_code}")

        try:
            # Try to parse as JSON first
            response_data = response.json()
        except Exception:
            # If JSON parsing fails, treat as text response
            response_text = response.text
            logger.debug(f"Non-JSON response: {response_text}")

            # For successful responses that aren't JSON, create a basic structure
            if response.is_success:
                return {
                    "success": True,
                    "data": response_text,
                    "message": "Request successful",
                }
            else:
                response_data: Dict[str, Any] = {
                    "success": False,
                    "error": response_text or f"HTTP {response.status_code}",
                    "message": f"Request failed with status {response.status_code}",
                }

        if response.is_success:
            return response_data

        # Handle API errors
        error_message = response_data.get("error", f"HTTP {response.status_code}")
        error_code = response_data.get("code")

        logger.error(f"API error: {response.status_code} - {error_message}")

        raise create_api_error(
            status_code=response.status_code,
            message=error_message,
            response_data=response_data,
            error_code=error_code,
        )

    def _handle_response_sync(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response for sync requests.

        Args:
            response: HTTP response object.

        Returns:
            Parsed response data.

        Raises:
            ZenoPayAPIError: For API errors.
        """
        logger.debug(f"Response status: {response.status_code}")

        try:
            # Try to parse as JSON first
            response_data = response.json()
        except Exception:
            # If JSON parsing fails, treat as text response
            response_text = response.text
            logger.debug(f"Non-JSON response: {response_text}")

            # For successful responses that aren't JSON, create a basic structure
            if response.is_success:
                return {
                    "success": True,
                    "data": response_text,
                    "message": "Request successful",
                }
            else:
                response_data: Dict[str, Any] = {
                    "success": False,
                    "error": response_text or f"HTTP {response.status_code}",
                    "message": f"Request failed with status {response.status_code}",
                }

        if response.is_success:
            return response_data

        error_message = response_data.get("error", f"HTTP {response.status_code}")
        error_code = response_data.get("code")

        logger.error(f"API error: {response.status_code} - {error_message}")

        raise create_api_error(
            status_code=response.status_code,
            message=error_message,
            response_data=response_data,
            error_code=error_code,
        )

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", url, data=data, **kwargs)

    def post_sync(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make a sync POST request."""
        return self.request_sync("POST", url, data=data, **kwargs)
