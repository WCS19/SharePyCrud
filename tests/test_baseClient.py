import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig


@pytest.fixture
def mock_config() -> SharePointConfig:
    """Fixture for a mock SharePointConfig."""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="test.sharepoint.com",
    )


@pytest.fixture
def base_client(mock_config: SharePointConfig) -> BaseClient:
    """
    Create a BaseClient instance.
    We'll patch _get_access_token to avoid real network calls in the fixture.
    """
    with patch.object(
        BaseClient, "_get_access_token", return_value="mock_access_token"
    ):
        client = BaseClient(mock_config)
    return client


## Test _get_access_token
@patch("requests.post")
def test_get_access_token_success(
    mock_post: MagicMock, mock_config: SharePointConfig
) -> None:
    """
    Test that _get_access_token successfully returns a token on 200 status.
    """
    # Mock a successful token response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_post.return_value = mock_response

    # We directly call _get_access_token by instantiating the client
    client = BaseClient(mock_config)  # triggers _get_access_token in __init__
    assert client.access_token == "fake_token"
    mock_post.assert_called_once_with(
        "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "scope": "https://graph.microsoft.com/.default",
        },
    )


@patch("requests.post")
def test_get_access_token_failure(
    mock_post: MagicMock, mock_config: SharePointConfig
) -> None:
    """
    Test that _get_access_token returns None if the request fails.
    """
    # Mock a failing response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException(
        "Network error"
    )
    mock_post.return_value = mock_response

    # Attempting to instantiate BaseClient should raise ValueError in __init__
    # because _get_access_token returns None on failure
    with pytest.raises(ValueError) as exc_info:
        _ = BaseClient(mock_config)

    assert "Failed to obtain access token" in str(exc_info.value)


## Test make_graph_request
@patch("requests.request")
def test_make_graph_request_success(
    mock_request: MagicMock, base_client: BaseClient
) -> None:
    """
    Test that make_graph_request returns a dictionary on success.
    """
    # Mock a successful JSON response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"key": "value"}
    mock_request.return_value = mock_response

    url = "https://graph.microsoft.com/v1.0/some/endpoint"
    response: Dict[str, Any] = base_client.make_graph_request(
        url, method="POST", data={"param": "test"}
    )
    assert response == {"key": "value"}

    # Ensure the correct request call was made
    mock_request.assert_called_once_with(
        "POST",
        url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Accept": "application/json",
        },
        json={"param": "test"},
    )


@patch("requests.request")
def test_make_graph_request_raises_for_4xx(
    mock_request: MagicMock, base_client: BaseClient
) -> None:
    """
    Test that make_graph_request raises for HTTP error status.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "400 Client Error"
    )
    mock_request.return_value = mock_response

    url = "https://graph.microsoft.com/v1.0/some/endpoint"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        base_client.make_graph_request(url)

    assert "400 Client Error" in str(exc_info.value)


@patch("requests.request")
def test_make_graph_request_invalid_json(
    mock_request: MagicMock, base_client: BaseClient
) -> None:
    """
    Test that make_graph_request raises ValueError if JSON parsing fails.
    """
    # Mock a response that raises ValueError when json() is called
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_request.return_value = mock_response

    url = "https://graph.microsoft.com/v1.0/bad/json"
    # Expect the method to raise ValueError if JSON is invalid
    with pytest.raises(ValueError) as exc_info:
        _ = base_client.make_graph_request(url)

    assert "Invalid JSON" in str(exc_info.value)


@patch.object(BaseClient, "_get_access_token", return_value="mock_access_token")
def test_make_graph_request_missing_token(
    mock_get_access_token: MagicMock, mock_config: SharePointConfig
) -> None:
    """
    Test that make_graph_request raises ValueError when the access token is missing.
    """
    # Create the BaseClient with a mocked access token
    base_client = BaseClient(mock_config)
    base_client.access_token = None  # Simulate missing access token

    url = "https://graph.microsoft.com/v1.0/some/endpoint"
    with pytest.raises(ValueError, match="Access token is missing or invalid"):
        base_client.make_graph_request(url)


@patch("requests.post")
def test_make_graph_request_token_request(
    mock_post: MagicMock, base_client: BaseClient
) -> None:
    """
    Test that make_graph_request sets Content-Type for token requests.
    """
    # Mock a successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"access_token": "new_token"}
    mock_post.return_value = mock_response

    url = "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token"
    data = {"grant_type": "client_credentials"}
    response = base_client.make_graph_request(url, method="POST", data=data)

    assert response == {"access_token": "new_token"}
    mock_post.assert_called_once_with(
        url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=data,
    )


@patch("requests.request")
def test_make_graph_request_post_method(
    mock_request: MagicMock, base_client: BaseClient
) -> None:
    """
    Test make_graph_request handles POST requests correctly.
    """
    # Mock a successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"key": "value"}
    mock_request.return_value = mock_response

    url = "https://graph.microsoft.com/v1.0/some/endpoint"
    data = {"param": "test"}
    response = base_client.make_graph_request(url, method="POST", data=data)

    assert response == {"key": "value"}
    mock_request.assert_called_once_with(
        "POST",
        url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Accept": "application/json",
        },
        json=data,
    )


def test_format_graph_url(base_client: BaseClient) -> None:
    """
    Test format_graph_url with varying arguments.
    """
    assert (
        base_client.format_graph_url("drives")
        == "https://graph.microsoft.com/v1.0/drives"
    )
    assert (
        base_client.format_graph_url("drives", "12345", "items")
        == "https://graph.microsoft.com/v1.0/drives/12345/items"
    )


def test_parse_folder_path(base_client: BaseClient) -> None:
    """
    Test parse_folder_path with different folder path patterns.
    """
    assert base_client.parse_folder_path("Folder1/FolderNest1/FolderNest2") == [
        "Folder1",
        "FolderNest1",
        "FolderNest2",
    ]
    assert base_client.parse_folder_path("/Folder1/FolderNest1/") == [
        "Folder1",
        "FolderNest1",
    ]
    assert base_client.parse_folder_path("") == [""]
