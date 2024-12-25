import pytest
from sharepycrud.auth import SharePointAuth
from unittest.mock import Mock
import requests


@pytest.fixture
def auth_client() -> SharePointAuth:
    """Create a SharePointAuth instance with test credentials"""
    return SharePointAuth(
        tenant_id="test-tenant", client_id="test-client", client_secret="test-secret"
    )


def test_auth_initialization(auth_client: SharePointAuth) -> None:
    """Test SharePointAuth initialization"""
    assert auth_client.tenant_id == "test-tenant"
    assert auth_client.client_id == "test-client"
    assert auth_client.client_secret == "test-secret"
    assert (
        auth_client.base_url
        == "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token"
    )


def test_get_access_token_success(auth_client: SharePointAuth, mocker: Mock) -> None:
    """Test successful access token retrieval"""
    # Mock the requests.post response
    mock_response = Mock()
    mock_response.json.return_value = {"access_token": "test-token"}
    mocker.patch("requests.post", return_value=mock_response)

    token = auth_client.get_access_token()

    assert token == "test-token"
    requests.post.assert_called_once_with(  # type: ignore
        auth_client.base_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test-client",
            "client_secret": "test-secret",
            "scope": "https://graph.microsoft.com/.default",
        },
    )


def test_get_access_token_failure(auth_client: SharePointAuth, mocker: Mock) -> None:
    """Test access token retrieval failure"""
    # Mock the requests.post response with invalid token
    mock_response = Mock()
    mock_response.json.return_value = {"error": "invalid_client"}
    mocker.patch("requests.post", return_value=mock_response)

    with pytest.raises(ValueError, match="Failed to get valid access token"):
        auth_client.get_access_token()
