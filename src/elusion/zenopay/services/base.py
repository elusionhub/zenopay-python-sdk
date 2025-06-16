"""Base service class for all ZenoPay SDK services."""

from typing import Any, Dict, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError

from elusion.zenopay.config import ZenoPayConfig
from elusion.zenopay.exceptions import ZenoPayValidationError
from elusion.zenopay.http import HTTPClient
from elusion.zenopay.models.common import APIResponse

T = TypeVar("T", bound=BaseModel)


class BaseService:
    """Base class for all API services."""

    def __init__(self, http_client: HTTPClient, config: ZenoPayConfig) -> None:
        """Initialize the service.

        Args:
            http_client: HTTP client instance.
            config: ZenoPay configuration.
        """
        self.http_client = http_client
        self.config = config

    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for an API endpoint.

        Args:
            endpoint: The endpoint name from config.ENDPOINTS.

        Returns:
            Full URL for the endpoint.
        """
        return self.config.get_endpoint_url(endpoint)

    def _prepare_request_data(self, data: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare and validate data for API requests.

        Args:
            data: Data to prepare for the request.

        Returns:
            Prepared data dictionary for form submission.

        Raises:
            ZenoPayValidationError: If validation fails.
        """
        if isinstance(data, BaseModel):
            request_data = data.model_dump(exclude_unset=True, by_alias=True)
        else:
            request_data = data.copy()

        request_data.update(
            {
                "account_id": self.config.account_id,
                "api_key": self.config.api_key or "null",
                "secret_key": self.config.secret_key or "null",
            }
        )

        return request_data

    def _parse_response(
        self,
        response_data: Dict[str, Any],
        model_class: Type[T],
    ) -> APIResponse[T]:
        """Parse API response into typed models.

        Args:
            response_data: Raw response data from API.
            model_class: Pydantic model class to parse data into.

        Returns:
            Parsed response with typed data.

        Raises:
            ZenoPayValidationError: If response parsing fails.
        """
        try:
            if "success" in response_data:
                success = response_data.get("success", True)
                data = response_data.get("data", response_data)
                message = response_data.get("message")
                error = response_data.get("error")

                if success and data:
                    parsed_data = model_class.model_validate(data)
                else:
                    # Error response
                    raise ZenoPayValidationError(error or "Unknown API error")
            else:
                # Direct data response
                parsed_data = model_class.model_validate(response_data)
                success = True
                message = None
                error = None

            return APIResponse[model_class](
                success=success,
                data=parsed_data,
                message=message,
                error=error,
            )

        except ValidationError as e:
            raise ZenoPayValidationError(
                f"Failed to parse response: {str(e)}",
                validation_errors={"errors": e.errors()},
            ) from e

    async def post_async(
        self,
        endpoint: str,
        data: Union[BaseModel, Dict[str, Any]],
        model_class: Type[T],
    ) -> APIResponse[T]:
        """Make an async POST request.

        Args:
            endpoint: API endpoint name.
            data: Data to send in the request.
            model_class: Model class to parse response into.

        Returns:
            Parsed API response.
        """
        url = self._build_url(endpoint)
        prepared_data = self._prepare_request_data(data)

        response_data = await self.http_client.post(url, data=prepared_data)
        return self._parse_response(response_data, model_class)

    async def _post(
        self,
        endpoint: str,
        data: Union[BaseModel, Dict[str, Any]],
        model_class: Type[T],
    ) -> APIResponse[T]:
        """Make a POST request (legacy method name).

        Args:
            endpoint: API endpoint name.
            data: Data to send in the request.
            model_class: Model class to parse response into.

        Returns:
            Parsed API response.
        """
        return await self.post_async(endpoint, data, model_class)

    def post_sync(
        self,
        endpoint: str,
        data: Union[BaseModel, Dict[str, Any]],
        model_class: Type[T],
    ) -> APIResponse[T]:
        """Make a sync POST request.

        Args:
            endpoint: API endpoint name.
            data: Data to send in the request.
            model_class: Model class to parse response into.

        Returns:
            Parsed API response.
        """
        url = self._build_url(endpoint)
        prepared_data = self._prepare_request_data(data)

        response_data = self.http_client.post_sync(url, data=prepared_data)
        return self._parse_response(response_data, model_class)
