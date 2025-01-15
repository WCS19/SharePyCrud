from unittest.mock import patch, MagicMock
import pytest
import requests
from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Any, Dict, cast, Optional
import logging


@pytest.fixture
def mock_config() -> SharePointConfig:
    """Fixture for a mock SharePointConfig."""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


@pytest.fixture
def base_client(mock_config: SharePointConfig) -> BaseClient:
    """Fixture for BaseClient with a mocked access token."""
    with patch.object(
        BaseClient, "_get_access_token", return_value="mock_access_token"
    ):
        return BaseClient(mock_config)


def test_init_no_access_token(caplog: Any) -> None:
    """
    Test that BaseClient.__init__ raises a ValueError if no access token is obtained.
    This covers the lines that log an error and raise ValueError.
    """
    config: SharePointConfig = SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="https://test.sharepoint.com",
    )

    # Patch _get_access_token to return None, triggering the failure path
    with patch.object(BaseClient, "_get_access_token", return_value=None):
        with pytest.raises(ValueError, match="Failed to obtain access token"):
            BaseClient(config)

    assert "Failed to obtain access token during initialization" in caplog.text


def test_get_access_token_success(mock_config: SharePointConfig, caplog: Any) -> None:
    """
    Test that _get_access_token returns a valid token.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")

    # 1) Patch _get_access_token for __init__ so it won't fail immediately
    with patch.object(
        BaseClient, "_get_access_token", return_value="constructor_mock_token"
    ):
        client: BaseClient = BaseClient(mock_config)

    # 2) Now use the *real* _get_access_token to test success scenario
    with patch("requests.post") as mock_post:
        mock_response: MagicMock = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "test_access_token"}
        mock_post.return_value = mock_response

        token: Optional[str] = client._get_access_token()
        assert token == "test_access_token"
    assert "Successfully obtained access token" in caplog.text


def test_get_access_token_missing_token(
    mock_config: SharePointConfig, caplog: Any
) -> None:
    """
    Test that _get_access_token raises a ValueError if the response is JSON but missing 'access_token'.
    """
    # 1) Patch _get_access_token for __init__ so it won't fail
    with patch.object(
        BaseClient, "_get_access_token", return_value="constructor_mock_token"
    ):
        client: BaseClient = BaseClient(mock_config)

    # 2) Now patch requests.post to return a token-less JSON response
    with patch("requests.post") as mock_post:
        mock_response: MagicMock = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"not_access_token": "some_value"}
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to obtain access token"):
            client._get_access_token()

    assert "No access token in response" in caplog.text


def test_get_access_token_http_error(
    mock_config: SharePointConfig, caplog: Any
) -> None:
    """
    Test that _get_access_token raises a ValueError if an HTTPError occurs.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")

    # 1) Patch _get_access_token for __init__ so it won't fail
    with patch.object(
        BaseClient, "_get_access_token", return_value="constructor_mock_token"
    ):
        client: BaseClient = BaseClient(mock_config)

    # Mock an HTTPError
    with patch("requests.post") as mock_post:
        mock_response: MagicMock = MagicMock()
        http_error: requests.exceptions.HTTPError = requests.exceptions.HTTPError(
            "Mock HTTP error"
        )
        http_error.response = MagicMock()
        http_error.response.status_code = 400
        http_error.response.reason = "Bad Request"
        http_error.response.text = "Error details"
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to obtain access token"):
            client._get_access_token()

    assert "HTTP error getting access token: 400 - Bad Request" in caplog.text
    assert "Response content: Error details" in caplog.text


def test_get_access_token_request_exception(
    mock_config: SharePointConfig, caplog: Any
) -> None:
    """
    Test that _get_access_token raises a ValueError if a generic requests.exceptions.RequestException occurs.
    """
    # 1) Patch _get_access_token for __init__ so it won't fail
    with patch.object(
        BaseClient, "_get_access_token", return_value="constructor_mock_token"
    ):
        client: BaseClient = BaseClient(mock_config)

    # 2) Simulate a generic RequestException (e.g., network failure)
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Network failure")

        with pytest.raises(ValueError, match="Failed to obtain access token"):
            client._get_access_token()

    assert "Failed to get access token: Network failure" in caplog.text


def test_make_graph_request_success(base_client: BaseClient) -> None:
    """Test that make_graph_request returns the correct response."""
    with patch("requests.request") as mock_request:
        mock_request.return_value = MagicMock(
            status_code=200,
            headers={"Content-Type": "application/json"},
            json=lambda: {"key": "value"},
        )
        response: Dict[str, Any] = base_client.make_graph_request(
            "https://mock-url.com"
        )
        assert response == {"key": "value"}


def test_make_graph_request_error(base_client: BaseClient) -> None:
    """Test that make_graph_request handles HTTP errors."""
    with patch("requests.request") as mock_request:
        mock_response: MagicMock = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Mock HTTP error"
        )
        mock_response.status_code = 500
        mock_response.text = "Error occurred"
        mock_response.reason = "Internal Server Error"
        mock_response.headers = {"Content-Type": "application/json"}

        mock_request.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError, match="Mock HTTP error"):
            base_client.make_graph_request("https://mock-url.com")


def test_make_graph_request_no_access_token(
    mock_config: SharePointConfig, caplog: Any
) -> None:
    """
    Test that make_graph_request raises ValueError if the access token is missing/invalid.
    We bypass the constructor check by returning a mock token, then set access_token = None.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")

    # 1) Patch _get_access_token for __init__ so it won't fail
    with patch.object(
        BaseClient, "_get_access_token", return_value="constructor_mock_token"
    ):
        client_no_token = BaseClient(mock_config)

    # 2) Now manually remove the token to simulate "no access token"
    client_no_token.access_token = None
    with pytest.raises(ValueError, match="Access token is missing or invalid"):
        client_no_token.make_graph_request("https://example.com")

    assert "Access token is missing or invalid" in caplog.text


def test_make_graph_request_with_custom_headers(base_client: BaseClient) -> None:
    """
    Test that make_graph_request correctly merges custom headers with default headers.
    """
    with patch("requests.request") as mock_request:
        mock_response: MagicMock = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "ok"}
        mock_request.return_value = mock_response

        custom_headers: Dict[str, str] = {"X-Custom-Header": "12345"}
        response: Dict[str, Any] = base_client.make_graph_request(
            url="https://example.com/api",
            method="POST",
            headers=custom_headers,
        )

        # Verify the response
        assert response == {"result": "ok"}

        # Check the method, headers, and URL in the mock call
        call_args: tuple[str, str] = mock_request.call_args.args  # Positional arguments
        call_kwargs: Dict[str, Any] = mock_request.call_args.kwargs  # Keyword arguments

        # Check HTTP method (first positional argument)
        assert call_args[0] == "POST"
        # Check URL (second positional argument)
        assert call_args[1] == "https://example.com/api"
        # Check headers (in kwargs)
        sent_headers: Dict[str, str] = call_kwargs["headers"]
        assert sent_headers["Authorization"] == "Bearer mock_access_token"
        assert sent_headers["X-Custom-Header"] == "12345"


def test_make_graph_request_returns_empty_dict_for_non_json(
    base_client: BaseClient,
) -> None:
    """
    Test that make_graph_request returns an empty dict for a non-JSON response.
    """
    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "text/plain"}  # Not JSON
        mock_request.return_value = mock_response

        result: Dict[str, Any] = base_client.make_graph_request(
            "https://example.com/api"
        )
        assert result == {}, "Expected an empty dict for non-JSON response"


def test_make_graph_request_http_error_with_response(
    base_client: BaseClient, caplog: Any
) -> None:
    """
    Test that make_graph_request handles HTTP errors and logs the error details.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")

    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        http_error = requests.exceptions.HTTPError("Mock HTTP error")
        http_error.response = MagicMock()
        http_error.response.status_code = 500
        http_error.response.reason = "Server Error"
        http_error.response.text = "Internal Server Error"

        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError, match="Mock HTTP error"):
            base_client.make_graph_request("https://example.com/api")

    assert "HTTP error in request: 500 - Server Error" in caplog.text
    assert "Response content: Internal Server Error" in caplog.text
    assert "Failed URL: https://example.com/api" in caplog.text


def test_make_graph_request_request_exception(
    base_client: BaseClient, caplog: Any
) -> None:
    """
    Test that make_graph_request raises a requests.exceptions.RequestException if a generic requests exception occurs.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")

    with patch(
        "requests.request",
        side_effect=requests.exceptions.RequestException("Network Error"),
    ):
        with pytest.raises(requests.exceptions.RequestException, match="Network Error"):
            base_client.make_graph_request("https://example.com/api")

    assert "Request failed: Network Error" in caplog.text
    assert "Failed URL: https://example.com/api" in caplog.text


def test_format_graph_url(base_client: BaseClient) -> None:
    """Test that format_graph_url correctly formats URLs."""
    url: str = base_client.format_graph_url("sites", "site-id", "lists")
    assert url == "https://graph.microsoft.com/v1.0/sites/site-id/lists"


def test_format_graph_url_no_args(base_client: BaseClient, caplog: Any) -> None:
    """
    Test that format_graph_url correctly formats URLs with no additional arguments.
    """
    caplog.set_level(logging.DEBUG)

    base_path = "sites"
    url: str = base_client.format_graph_url(base_path)
    assert url == "https://graph.microsoft.com/v1.0/sites"
    assert f"Formatted Graph API URL: {url}" in caplog.text


def test_format_graph_url_exception(base_client: BaseClient, caplog: Any) -> None:
    """
    Test that format_graph_url raises an exception if there's an error formatting the URL.
    """
    caplog.set_level(logging.DEBUG)

    with patch(
        "sharepycrud.baseClient.quote", side_effect=Exception("Mock Encoding Error")
    ):
        base_path = "sites"
        args = ("invalid_path",)  # Note: args is a tuple when passed with *args

        with pytest.raises(Exception, match="Mock Encoding Error"):
            base_client.format_graph_url(base_path, *args)

    assert "Error formatting Graph API URL: Mock Encoding Error" in caplog.text
    assert f"base_path: {base_path}, args: {args}" in caplog.text


def test_parse_folder_path(base_client: BaseClient) -> None:
    """Test that parse_folder_path correctly parses folder paths."""
    result: list[str] = base_client.parse_folder_path("/Folder1/Folder2/Folder3/")
    assert result == ["Folder1", "Folder2", "Folder3"]


def test_parse_folder_path_valid(base_client: BaseClient, caplog: Any) -> None:
    """
    Test parse_folder_path for a valid folder path to ensure parsing works.
    """
    caplog.set_level(logging.DEBUG)

    folder_path = "/Folder1/FolderNest1/FolderNest2/"
    components: list[str] = base_client.parse_folder_path(folder_path)
    assert components == ["Folder1", "FolderNest1", "FolderNest2"]
    assert f"Parsed folder path '{folder_path}' into: {components}" in caplog.text


def test_parse_folder_path_exception(base_client: BaseClient, caplog: Any) -> None:
    """
    Test that parse_folder_path raises an exception if the input is None.
    """
    caplog.set_level(logging.DEBUG)

    # Pass in None so calling .strip("/") raises an AttributeError
    folder_path = None

    with pytest.raises(
        AttributeError, match="'NoneType' object has no attribute 'strip'"
    ):
        base_client.parse_folder_path(folder_path)

    assert (
        "Error parsing folder path: 'NoneType' object has no attribute 'strip'"
        in caplog.text
    )
    assert f"Input folder_path: {folder_path}" in caplog.text
