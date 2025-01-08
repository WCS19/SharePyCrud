import pytest
from sharepycrud.utils import format_graph_url, make_graph_request
from unittest.mock import Mock, patch
import requests
from typing import cast
from pytest_mock import MockerFixture
from sharepycrud.utils import setup_client


def test_setup_client_valid_env_vars(mocker: MockerFixture) -> None:
    """Test setup_client with valid environment variables"""
    # Mock SharePointConfig.from_env to return a valid configuration
    mock_config = Mock()
    mock_config.validate.return_value = (True, [])
    mocker.patch(
        "sharepycrud.utils.SharePointConfig.from_env", return_value=mock_config
    )
    mock_client = Mock()
    mocker.patch("sharepycrud.client.SharePointClient", return_value=mock_client)

    client = setup_client()
    assert client is not None
    assert client == mock_client


def test_setup_client_missing_env_vars(mocker: MockerFixture) -> None:
    """Test setup_client when environment variables are missing"""
    # Mock SharePointConfig.from_env to simulate missing environment variables
    mock_config = Mock()
    mock_config.validate.return_value = (False, ["client_id", "client_secret"])
    mocker.patch(
        "sharepycrud.utils.SharePointConfig.from_env", return_value=mock_config
    )

    # Capture printed output
    with patch("builtins.print") as mock_print:
        client = setup_client()
        assert client is None

        # Debug captured print calls
        print(
            f"Captured print calls: {[call.args for call in mock_print.call_args_list]}"
        )


def test_setup_client_type_checking(mocker: MockerFixture) -> None:
    """Test setup_client with TYPE_CHECKING enabled"""
    with patch("sharepycrud.utils.TYPE_CHECKING", True):
        # Ensure that the import inside TYPE_CHECKING works without issues
        import sharepycrud.client


def test_format_graph_url_debug() -> None:
    """Debug test to print URL formation"""
    url = format_graph_url("sites")
    assert url == "https://graph.microsoft.com/v1.0/sites"


def test_format_graph_url_basic() -> None:
    """Test basic URL formatting"""
    url = format_graph_url("sites")
    assert url == "https://graph.microsoft.com/v1.0/sites"


def test_format_graph_url_with_args() -> None:
    """Test URL formatting with arguments"""
    url = format_graph_url("sites", "site-id", "drives")
    assert url == "https://graph.microsoft.com/v1.0/sites/site-id/drives"


def test_format_graph_url_with_special_chars() -> None:
    """Test URL formatting with special characters"""
    url = format_graph_url("sites", "test site", "my/drive")
    assert url == "https://graph.microsoft.com/v1.0/sites/test%20site/my%2Fdrive"


def test_make_graph_request_success(mocker: MockerFixture) -> None:
    """Test successful graph request"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": "test"}
    mock_request = mocker.patch("requests.request", return_value=mock_response)

    result = make_graph_request("https://test.com", "fake-token")

    assert result == {"value": "test"}
    mock_request.assert_called_once_with(
        "GET",
        "https://test.com",
        headers={"Authorization": "Bearer fake-token", "Accept": "application/json"},
        json=None,
    )


def test_make_graph_request_failure(mocker: MockerFixture) -> None:
    """Test failed graph request"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "Unauthorized"}
    mocker.patch("requests.request", return_value=mock_response)

    result = make_graph_request("https://test.com", "fake-token")

    assert result == {}


def test_make_graph_request_token_endpoint(mocker: MockerFixture) -> None:
    """Test request to token endpoint"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test-token"}
    mock_post = mocker.patch("requests.post", return_value=mock_response)

    result = make_graph_request(
        "https://login.microsoftonline.com/tenant/oauth2/v2.0/token",
        "fake-token",
        method="POST",
        data={"grant_type": "client_credentials"},
    )

    assert result == {"access_token": "test-token"}
    mock_post.assert_called_once_with(
        "https://login.microsoftonline.com/tenant/oauth2/v2.0/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
    )
