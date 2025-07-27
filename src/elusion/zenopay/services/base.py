"""Base service class for all ZenoPay SDK services."""

from typing import Any, Dict, Type, TypeVar, Union, Optional

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

        return request_data

    def _prepare_query_params(self, params: Optional[Union[BaseModel, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Prepare and validate query parameters for GET requests.

        Args:
            params: Parameters to prepare for the request.

        Returns:
            Prepared query parameters dictionary.

        Raises:
            ZenoPayValidationError: If validation fails.
        """
        if params is None:
            query_params = {}
        elif isinstance(params, BaseModel):
            query_params = params.model_dump(exclude_unset=True, by_alias=True)
        else:
            query_params = params.copy()

        return query_params

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
            parsed_data = model_class.model_validate(response_data)
            success = True
            message = response_data.get("message", None)
            error = None

            return APIResponse[model_class](
                success=success,
                results=parsed_data,
                message=message,
                error=error,
            )

        except ValidationError as e:
            # print(f"{response_data}")
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

        response_data = await self.http_client.post(url, json=prepared_data)
        return self._parse_response(response_data, model_class)

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

        response_data = self.http_client.post_sync(url, json=prepared_data)
        return self._parse_response(response_data, model_class)

    async def get_async(
        self,
        endpoint: str,
        model_class: Type[T],
        params: Optional[Union[BaseModel, Dict[str, Any]]] = None,
    ) -> APIResponse[T]:
        """Make an async GET request.

        Args:
            endpoint: API endpoint name.
            model_class: Model class to parse response into.
            params: Optional query parameters to send with the request.

        Returns:
            Parsed API response.
        """
        url = self._build_url(endpoint)
        query_params = self._prepare_query_params(params)

        response_data = await self.http_client.get(url, params=query_params)
        return self._parse_response(response_data, model_class)

    def get_sync(
        self,
        endpoint: str,
        model_class: Type[T],
        params: Optional[Union[BaseModel, Dict[str, Any]]] = None,
    ) -> APIResponse[T]:
        """Make a sync GET request.

        Args:
            endpoint: API endpoint name.
            model_class: Model class to parse response into.
            params: Optional query parameters to send with the request.

        Returns:
            Parsed API response.
        """
        url = self._build_url(endpoint)
        query_params = self._prepare_query_params(params)

        response_data = self.http_client.get_sync(url, params=query_params)
        return self._parse_response(response_data, model_class)
