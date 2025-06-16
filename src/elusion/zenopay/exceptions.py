"""Custom exceptions for the ZenoPay SDK."""

from typing import Any, Dict, Optional


class ZenoPayError(Exception):
    """Base exception for all ZenoPay SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ZenoPayError.

        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
            response_data: Response data from the API if available.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class ZenoPayAPIError(ZenoPayError):
    """Exception raised for API errors from the ZenoPay service."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        """Initialize ZenoPayAPIError.

        Args:
            message: Error message from the API.
            status_code: HTTP status code.
            response_data: Full response data from the API.
            error_code: Specific error code from the API.
        """
        super().__init__(message, status_code, response_data)
        self.error_code = error_code


class ZenoPayAuthenticationError(ZenoPayAPIError):
    """Exception raised for authentication errors (401)."""

    def __init__(
        self,
        message: str = "Invalid API key or secret key",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 401, response_data, "AUTHENTICATION_ERROR")


class ZenoPayAuthorizationError(ZenoPayAPIError):
    """Exception raised for authorization errors (403)."""

    def __init__(
        self,
        message: str = "Insufficient permissions for this operation",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 403, response_data, "AUTHORIZATION_ERROR")


class ZenoPayNotFoundError(ZenoPayAPIError):
    """Exception raised when a resource is not found (404)."""

    def __init__(
        self,
        message: str = "The requested resource was not found",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 404, response_data, "NOT_FOUND_ERROR")


class ZenoPayValidationError(ZenoPayAPIError):
    """Exception raised for validation errors (400, 422)."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        response_data: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ZenoPayValidationError.

        Args:
            message: Error message.
            status_code: HTTP status code (400 or 422).
            response_data: Response data from the API.
            validation_errors: Detailed validation errors by field.
        """
        super().__init__(message, status_code, response_data, "VALIDATION_ERROR")
        self.validation_errors = validation_errors or {}


class ZenoPayRateLimitError(ZenoPayAPIError):
    """Exception raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        response_data: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        """Initialize ZenoPayRateLimitError.

        Args:
            message: Error message.
            response_data: Response data from the API.
            retry_after: Number of seconds to wait before retrying.
        """
        super().__init__(message, 429, response_data, "RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class ZenoPayServerError(ZenoPayAPIError):
    """Exception raised for server errors (5xx)."""

    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = 500,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data, "SERVER_ERROR")


class ZenoPayNetworkError(ZenoPayError):
    """Exception raised for network-related errors."""

    def __init__(
        self,
        message: str = "Network error occurred",
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize ZenoPayNetworkError.

        Args:
            message: Error message.
            original_error: The original exception that caused this error.
        """
        super().__init__(message)
        self.original_error = original_error


class ZenoPayTimeoutError(ZenoPayNetworkError):
    """Exception raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timeout",
        timeout_duration: Optional[float] = None,
    ) -> None:
        """Initialize ZenoPayTimeoutError.

        Args:
            message: Error message.
            timeout_duration: The timeout duration that was exceeded.
        """
        super().__init__(message)
        self.timeout_duration = timeout_duration


class ZenoPayWebhookError(ZenoPayError):
    """Exception raised for webhook-related errors."""

    def __init__(
        self,
        message: str = "Webhook processing error",
        webhook_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ZenoPayWebhookError.

        Args:
            message: Error message.
            webhook_data: The webhook data that caused the error.
        """
        super().__init__(message)
        self.webhook_data = webhook_data or {}


def create_api_error(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
) -> ZenoPayAPIError:
    """Factory function to create appropriate API error based on status code.

    Args:
        status_code: HTTP status code.
        message: Error message.
        response_data: Response data from the API.
        error_code: Specific error code from the API.

    Returns:
        Appropriate ZenoPayAPIError subclass instance.
    """
    if status_code == 401:
        return ZenoPayAuthenticationError(message, response_data)
    elif status_code == 403:
        return ZenoPayAuthorizationError(message, response_data)
    elif status_code == 404:
        return ZenoPayNotFoundError(message, response_data)
    elif status_code in (400, 422):
        validation_errors = None
        if response_data and "errors" in response_data:
            validation_errors = response_data["errors"]
        return ZenoPayValidationError(message, status_code, response_data, validation_errors)
    elif status_code == 429:
        retry_after = None
        if response_data and "retry_after" in response_data:
            retry_after = response_data["retry_after"]
        return ZenoPayRateLimitError(message, response_data, retry_after)
    elif status_code >= 500:
        return ZenoPayServerError(message, status_code, response_data)
    else:
        return ZenoPayAPIError(message, status_code, response_data, error_code)
