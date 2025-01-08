import pytest
from sharepycrud.client import SharePointClient
from sharepycrud.config import SharePointConfig
from unittest.mock import Mock, patch
from typing import Dict, List, Any
from .type_fixture import typed_fixture


@typed_fixture
def config() -> SharePointConfig:
    """Create a test configuration"""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


@typed_fixture
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


def test_get_site_id_no_access_token(client: SharePointClient) -> None:
    """Test get_site_id when access_token is missing"""
    # Remove access_token
    client.access_token = None

    site_id = client.get_site_id(site_name="test-site")
    assert site_id is None


def test_list_drive_ids_success(client: SharePointClient, mocker: Mock) -> None:
    mock_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"id": "drive1-id", "name": "drive1"},
            {"id": "drive2-id", "name": "drive2"},
        ]
    }
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    drive_ids = client.list_drive_ids("test-site-id")
    assert drive_ids == [("drive1-id", "drive1"), ("drive2-id", "drive2")]


def test_list_drive_ids_failure(client: SharePointClient, mocker: Mock) -> None:
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    drive_ids = client.list_drive_ids("test-site-id")
    assert drive_ids == []


def test_list_drives_success(client: SharePointClient, mocker: Mock) -> None:
    """Test successful drive listing"""
    mock_response: Dict[str, List[Dict[str, Any]]] = {
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


def test_list_drives_no_value(client: SharePointClient, mocker: Mock) -> None:
    """Test list_drives when 'value' key is missing"""
    mock_response: Dict[str, Any] = {}  # 'value' key is missing
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    drives = client.list_drives("test-site-id")
    assert drives is None


def test_list_drives_no_access_token(client: SharePointClient) -> None:
    """Test list_drives when access_token is missing"""
    # Remove access_token
    client.access_token = None

    drives = client.list_drives("test-site-id")
    assert drives is None


def test_list_drives_no_items_in_root_folder(
    client: SharePointClient, mocker: Mock
) -> None:
    """Test list_drives when root folder has no items"""
    # Mock drives response
    mock_drives_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"name": "drive1", "id": "drive1-id"},
        ]
    }
    mocker.patch(
        "sharepycrud.client.make_graph_request",
        side_effect=[
            mock_drives_response,  # First call: Drives response
            {},  # Second call: Root contents missing "value"
        ],
    )

    with patch("builtins.print") as mock_print:
        drives = client.list_drives("test-site-id")
        assert drives == mock_drives_response

        # Assert "No items in root folder" was printed
        mock_print.assert_any_call("No items in root folder")


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


def test_download_file_no_drive_id(client: SharePointClient, mocker: Mock) -> None:
    """Test download_file when drive_id is None"""
    mocker.patch.object(client, "get_site_id", return_value="test-site-id")
    mocker.patch.object(client, "get_drive_id", return_value=None)

    content = client.download_file("test.txt", "test-site", "test-drive")
    assert content is None


def test_download_file_http_error(client: SharePointClient, mocker: Mock) -> None:
    """Test download_file when HTTP GET returns non-200 status code"""
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
    mock_download.status_code = 404  # Not found
    mock_download.content = b""
    mocker.patch("requests.get", return_value=mock_download)

    content = client.download_file("test.txt", "test-site", "test-drive")
    assert content is None


def test_get_folder_content_success(client: SharePointClient, mocker: Mock) -> None:
    mock_response = {
        "value": [
            {
                "id": "item1-id",
                "name": "item1",
                "folder": {},
                "parentReference": {"path": "/drives/drive-id/root/folder1"},
                "webUrl": "http://example.com/item1",
                "size": 1234,
            },
            {
                "id": "item2-id",
                "name": "item2",
                "file": {},
                "parentReference": {"path": "/drives/drive-id/root/folder1"},
                "webUrl": "http://example.com/item2",
                "size": 5678,
            },
        ]
    }
    mocker.patch("sharepycrud.client.make_graph_request", return_value=mock_response)

    contents = client.get_folder_content("test-drive-id", "folder-id")
    expected_contents = [
        {
            "id": "item1-id",
            "name": "item1",
            "type": "folder",
            "webUrl": "http://example.com/item1",
            "size": 1234,
        },
        {
            "id": "item2-id",
            "name": "item2",
            "type": "file",
            "webUrl": "http://example.com/item2",
            "size": 5678,
        },
    ]
    assert contents == expected_contents


def test_get_folder_content_failure(client: SharePointClient, mocker: Mock) -> None:
    mocker.patch("sharepycrud.client.make_graph_request", return_value=None)

    contents = client.get_folder_content("test-drive-id", "folder-id")
    assert contents is None


# Edge case exception handling tests
def test_list_sites_no_access_token(client: SharePointClient) -> None:
    """Test list_sites when access_token is None"""
    client.access_token = None
    sites = client.list_sites()
    assert sites is None
