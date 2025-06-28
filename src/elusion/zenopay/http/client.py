"""HTTP client for the ZenoPay SDK."""

import logging
from typing import Any, Dict, List, Optional

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

    def _clean_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Clean query parameters by removing None values and converting to strings.

        Args:
            params: Query parameters to clean.

        Returns:
            Cleaned parameters dictionary or None.
        """
        if not params:
            return None

        cleaned_params: Dict[str, str] = {}
        for key, value in params.items():
            if value is not None:
                cleaned_params[str(key)] = str(value)

        return cleaned_params if cleaned_params else None

    def _clean_data(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Clean form data by removing None values and converting to strings.

        Args:
            data: Form data to clean.

        Returns:
            Cleaned data dictionary or None.
        """
        if not data:
            return None

        cleaned_data: Dict[str, Any] = {}
        for key, value in data.items():
            if value is not None:
                cleaned_data[key] = str(value)

        return cleaned_data if cleaned_data else None

    async def request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Request URL.
            data: Form data to send (for POST/PUT requests).
            params: Query parameters to send (for GET requests).
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

        cleaned_data = self._clean_data(data)
        cleaned_params = self._clean_params(params)

        try:

            if self._client is None:
                raise ZenoPayNetworkError("Async HTTP client is not initialized.", None)

            response = await self._client.request(
                method=method,
                url=url,
                data=cleaned_data,
                params=cleaned_params,
                headers=request_headers,
                **kwargs,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException as e:
            raise ZenoPayTimeoutError(
                f"Request timeout after {self.config.timeout} seconds",
                self.config.timeout,
            ) from e
        except httpx.NetworkError as e:
            raise ZenoPayNetworkError(f"Network error: {str(e)}", e) from e
        except Exception as e:
            raise ZenoPayNetworkError(f"Unexpected error: {str(e)}", e) from e

    def request_sync(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a sync HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Request URL.
            data: Form data to send (for POST/PUT requests).
            params: Query parameters to send (for GET requests).
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

        cleaned_data = self._clean_data(data)
        cleaned_params = self._clean_params(params)

        try:

            if self._sync_client is None:
                raise ZenoPayNetworkError("Sync HTTP client is not initialized.", None)

            response = self._sync_client.request(
                method=method,
                url=url,
                data=cleaned_data,
                params=cleaned_params,
                headers=request_headers,
                **kwargs,
            )

            # Log response details for debugging

            return self._handle_response_sync(response)

        except httpx.TimeoutException as e:
            raise ZenoPayTimeoutError(
                f"Request timeout after {self.config.timeout} seconds",
                self.config.timeout,
            ) from e
        except httpx.NetworkError as e:
            raise ZenoPayNetworkError(f"Network error: {str(e)}", e) from e
        except Exception as e:
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

        response_data: Dict[str, Any] = {}

        try:
            response_data = response.json()
        except Exception:
            response_text = response.text

            if response.is_success:
                return {
                    "success": True,
                    "data": response_text,
                    "message": "Request successful",
                }
            else:
                response_data = {
                    "success": False,
                    "error": response_text or f"HTTP {response.status_code}",
                    "message": f"Request failed with status {response.status_code}",
                    "status_code": response.status_code,
                }

        if response.is_success:
            return response_data

        error_message = self._extract_error_message(response_data, response)
        error_code = response_data.get("code") or response_data.get("error_code")

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

        response_data: Dict[str, Any] = {}

        try:
            response_data = response.json()
        except Exception:
            response_text = response.text

            if response.is_success:
                return {
                    "success": True,
                    "data": response_text,
                    "message": "Request successful",
                }
            else:
                response_data = {
                    "success": False,
                    "error": response_text or f"HTTP {response.status_code}",
                    "message": f"Request failed with status {response.status_code}",
                    "status_code": response.status_code,
                }

        if response.is_success:
            return response_data

        error_message = self._extract_error_message(response_data, response)
        error_code = response_data.get("code") or response_data.get("error_code")

        raise create_api_error(
            status_code=response.status_code,
            message=error_message,
            response_data=response_data,
            error_code=error_code,
        )

    def _extract_error_message(self, response_data: Dict[str, Any], response: httpx.Response) -> str:
        """Extract detailed error message from response data.

        Args:
            response_data: Parsed response data
            response: HTTP response object

        Returns:
            Detailed error message
        """

        error_fields = ["error_description", "error", "message", "detail", "details", "error_message", "msg", "description", "reason"]

        for field in error_fields:
            if field in response_data and response_data[field]:
                error_msg: str = response_data[field]
                if isinstance(error_msg, dict):
                    return str(error_msg)
                return str(error_msg)

        if "errors" in response_data:
            errors: Dict[str, Any] = response_data["errors"]
            error_parts: List[str] = []
            for field, field_errors in errors.items():
                field_name: str = field
                if isinstance(field_errors, list):
                    error_strs = [str(e) for e in field_errors]  # type: ignore
                    error_parts.append(f"{field_name}: {', '.join(error_strs)}")
                else:
                    error_parts.append(f"{field_name}: {str(field_errors)}")
            formatted_errors = "; ".join(error_parts)
            return formatted_errors

        if "success" in response_data and response_data["success"] is False:
            print("DEBUG: Response indicates failure, checking for error details")

        if "error" in response_data and isinstance(response_data["error"], dict):
            nested_error: Dict[str, Any] = response_data["error"]  # type: ignore
            for field in error_fields:
                if field in nested_error:
                    return str(nested_error[field])

        response_text = response.text
        if response_text and len(response_text) < 1000:
            return f"HTTP {response.status_code}: {response_text}"

        fallback = f"HTTP {response.status_code} - {response.reason_phrase or 'Unknown error'}"
        return fallback

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make an async POST request.

        Args:
            url: Request URL.
            data: Form data to send.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.
        """
        return await self.request("POST", url, data=data, **kwargs)

    def post_sync(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make a sync POST request.

        Args:
            url: Request URL.
            data: Form data to send.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.
        """
        return self.request_sync("POST", url, data=data, **kwargs)

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make an async GET request.

        Args:
            url: Request URL.
            params: Query parameters to send.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.
        """
        return await self.request("GET", url, params=params, **kwargs)

    def get_sync(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make a sync GET request.

        Args:
            url: Request URL.
            params: Query parameters to send.
            **kwargs: Additional arguments for httpx.

        Returns:
            Parsed response data.
        """
        return self.request_sync("GET", url, params=params, **kwargs)
