import pytest
from sharepycrud.client import SharePointClient
from sharepycrud.config import SharePointConfig
from unittest.mock import Mock, patch
from typing import Dict, List, Any
from pytest_mock import MockerFixture


@pytest.fixture
def config() -> SharePointConfig:
    """Create a test configuration"""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


@pytest.fixture
def client(config: SharePointConfig) -> SharePointClient:
    """Create a SharePointClient with mocked auth"""
    with patch("sharepycrud.client.make_graph_request") as mock_request:
        mock_request.return_value = {"access_token": "test-token"}
        return SharePointClient(config)


def test_client_initialization(
    client: SharePointClient, config: SharePointConfig
) -> None:
    """Test client initialization"""
    assert client.config == config
    assert client.access_token == "test-token"


def test_client_initialization_failure(config: SharePointConfig) -> None:
    """Test client initialization with auth failure"""
    with (
        patch("sharepycrud.client.make_graph_request", return_value=None),
        pytest.raises(ValueError, match="Failed to obtain access token"),
    ):
        SharePointClient(config)


def test_list_sites_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful site listing"""
    mock_response = {"value": [{"name": "site1"}, {"name": "site2"}]}
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    sites = client.list_sites()
    assert sites == ["site1", "site2"]


def test_list_sites_failure(client: SharePointClient, mocker: Mock) -> None:
    """Test site listing failure"""
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    sites = client.list_sites()
    assert sites is None


def test_get_site_id_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful site ID retrieval"""
    mock_response = {"id": "test-site-id"}
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    site_id = client.get_site_id(site_name="test-site")
    assert site_id == "test-site-id"


def test_get_site_id_failure(client: SharePointClient, mocker: Mock) -> None:
    """Test site ID retrieval failure"""
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    site_id = client.get_site_id(site_name="test-site")
    assert site_id is None


def test_list_drives_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful drive listing"""
    mock_response = {
        "value": [
            {"name": "drive1", "id": "drive1-id"},
            {"name": "drive2", "id": "drive2-id"},
        ]
    }
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    drives = client.list_drives("test-site-id")
    assert drives == mock_response


def test_list_drives_failure(client: SharePointClient, mocker: Mock) -> None:
    """Test drive listing failure"""
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    drives = client.list_drives("test-site-id")
    assert drives is None


def test_get_drive_id_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful drive ID retrieval"""
    mock_response = {
        "value": [
            {"name": "test-drive", "id": "test-drive-id"},
            {"name": "other-drive", "id": "other-id"},
        ]
    }
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    drive_id = client.get_drive_id("test-site-id", "test-drive")
    assert drive_id == "test-drive-id"


def test_get_drive_id_not_found(client: SharePointClient, mocker: Mock) -> None:
    """Test drive ID retrieval when drive name doesn't exist"""
    mock_response = {"value": [{"name": "other-drive", "id": "other-id"}]}
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    drive_id = client.get_drive_id("test-site-id", "test-drive")
    assert drive_id is None


def test_list_all_folders_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful folder listing"""
    # Mock for initial call
    root_response = {
        "value": [
            {
                "name": "folder1",
                "id": "folder1-id",
                "folder": {},
                "parentReference": {"path": "/drives/test-drive-id/root"},
            },
            {
                "name": "folder2",
                "id": "folder2-id",
                "folder": {},
                "parentReference": {"path": "/drives/test-drive-id/root"},
            },
        ]
    }

    # Mock for subfolder calls - return empty to prevent recursion
    empty_response: Dict[str, List[Any]] = {"value": []}

    def mock_request(url: str, *args: Any, **kwargs: Any) -> Dict[str, List[Any]]:
        if "folder1-id" in url or "folder2-id" in url:
            return empty_response
        return root_response

    mocker.patch("sharepycrud.client.make_graph_request", side_effect=mock_request)

    folders = client.list_all_folders("test-drive-id")
    expected_folders = [
        {
            "name": "folder1",
            "id": "folder1-id",
            "path": "/drives/test-drive-id/root/folder1",
        },
        {
            "name": "folder2",
            "id": "folder2-id",
            "path": "/drives/test-drive-id/root/folder2",
        },
    ]
    assert folders == expected_folders


def test_list_all_folders_failure(client: SharePointClient, mocker: Mock) -> None:
    """Test folder listing failure"""
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    folders = client.list_all_folders("test-drive-id")
    assert folders == []


def test_download_file_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful file download"""
    # Mock site and drive ID lookups
    mocker.patch.object(client, "get_site_id", return_value="test-site-id")
    mocker.patch.object(client, "get_drive_id", return_value="test-drive-id")

    # Mock file listing
    mock_list_response = {"value": [{"id": "test-file-id", "name": "test.txt"}]}
    mocker.patch(
        "sharepycrud.client.make_graph_request", return_value=mock_list_response
    )

    # Mock file download
    mock_download = Mock()
    mock_download.status_code = 200
    mock_download.content = b"test content"
    mocker.patch("requests.get", return_value=mock_download)

    content = client.download_file("test.txt", "test-site", "test-drive")
    assert content == b"test content"


def test_download_file_not_found(client: SharePointClient, mocker: Mock) -> None:
    """Test file download when file not found"""
    mocker.patch.object(client, "get_site_id", return_value="test-site-id")
    mocker.patch.object(client, "get_drive_id", return_value="test-drive-id")
    mocker.patch("sharepycrud.client.make_graph_request", return_value={"value": []})

    content = client.download_file("nonexistent.txt", "test-site", "test-drive")
    assert content is None
