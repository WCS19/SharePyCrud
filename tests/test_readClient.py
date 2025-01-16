import pytest
from unittest.mock import MagicMock, patch
from sharepycrud.readClient import ReadClient
from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Any, List, Dict, Optional
import requests
import logging
import sys


@pytest.fixture
def mock_base_client() -> BaseClient:
    """Mocked BaseClient instance."""
    base_client = MagicMock(spec=BaseClient)
    base_client.access_token = "mock_access_token"
    base_client.config = SharePointConfig(
        tenant_id="mock-tenant-id",
        client_id="mock-client-id",
        client_secret="mock-client-secret",
        sharepoint_url="https://mock.sharepoint.com",
    )
    return base_client


@pytest.fixture
def read_client(mock_base_client: BaseClient) -> ReadClient:
    """ReadClient initialized with a mocked BaseClient."""
    return ReadClient(mock_base_client)


def test_make_graph_request(read_client: ReadClient) -> None:
    """Test delegating make_graph_request to BaseClient."""
    with patch.object(
        read_client.client, "make_graph_request", return_value={"key": "value"}
    ) as mock_method:
        result = read_client.make_graph_request(
            "https://mock-url.com", "POST", {"data": "test"}
        )
        mock_method.assert_called_once_with(
            "https://mock-url.com", "POST", {"data": "test"}
        )
        assert result == {"key": "value"}


def test_format_graph_url(read_client: ReadClient) -> None:
    """Test delegating format_graph_url to BaseClient."""
    with patch.object(
        read_client.client, "format_graph_url", return_value="https://mocked-url.com"
    ) as mock_method:
        result = read_client.format_graph_url("sites", "mock-site")
        mock_method.assert_called_once_with("sites", "mock-site")
        assert result == "https://mocked-url.com"


def test_parse_folder_path(read_client: ReadClient) -> None:
    """Test delegating parse_folder_path to BaseClient."""
    with patch.object(
        read_client.client, "parse_folder_path", return_value=["Folder1", "Folder2"]
    ) as mock_method:
        result = read_client.parse_folder_path("/Folder1/Folder2/")
        mock_method.assert_called_once_with("/Folder1/Folder2/")
        assert result == ["Folder1", "Folder2"]


def test_list_sites_success(read_client: ReadClient) -> None:
    """Test listing sites successfully."""
    mock_response = {"value": [{"name": "Site1"}, {"name": "Site2"}]}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_sites()
        assert result == ["Site1", "Site2"]


def test_list_sites_no_sites_found(read_client: ReadClient, caplog: Any) -> None:
    """
    Test listing sites when no sites are found (empty response).
    """
    caplog.set_level("INFO", logger="sharepycrud.readClient")

    with patch.object(
        read_client.client, "make_graph_request", return_value={"value": []}
    ):
        result = read_client.list_sites()
        assert result == []
        assert "Found 0 sites" in caplog.text


def test_list_sites_no_token(read_client: ReadClient) -> None:
    """Test listing sites when access token is missing."""
    read_client.client.access_token = None
    result = read_client.list_sites()
    assert result is None


def test_list_sites_response_none(read_client: ReadClient) -> None:
    """Test listing sites when response is None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_sites()
        assert result is None


def test_get_site_id_success(read_client: ReadClient, caplog: Any) -> None:
    """Test getting a site ID successfully."""
    caplog.set_level("INFO", logger="sharepycrud.readClient")
    mock_response = {"id": "mock-site-id"}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_site_id("mock-site-name")

    assert result == "mock-site-id"
    assert "Found site: mock-site-name" in caplog.text
    assert "Site ID: mock-site-id" in caplog.text


def test_get_site_id_no_access_token(read_client: ReadClient) -> None:
    """Test that get_site_id returns None when there is no access token."""
    read_client.client.access_token = None
    result = read_client.get_site_id(site_name="TestSite")
    assert result is None


def test_get_site_id_no_site_name(read_client: ReadClient, caplog: Any) -> None:
    """Test that get_site_id logs an error and returns None when site_name is empty."""
    caplog.set_level("ERROR", logger="sharepycrud.readClient")
    result = read_client.get_site_id(site_name="")
    assert result is None
    assert "Site name is required" in caplog.text


def test_get_site_id_not_found(read_client: ReadClient) -> None:
    """Test that get_site_id returns None when the site ID is not found."""
    mock_response = {"id": None}  # Site ID is not present

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_site_id(site_name="TestSite")

    assert result is None


def test_get_site_id_no_response(read_client: ReadClient) -> None:
    """Test that get_site_id returns None when make_graph_request returns None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.get_site_id(site_name="TestSite")

    assert result is None


def test_list_drives_and_root_contents_success(
    read_client: ReadClient, caplog: Any
) -> None:
    """Test listing drives and root contents successfully."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Dict[str, str]]] = {
        "value": [{"name": "Drive1", "id": "drive-id-1"}]
    }
    mock_root_contents: Dict[str, List[Dict[str, Any]]] = {
        "value": [
            {"name": "Folder1", "folder": {}},
            {"name": "File1", "file": {}},
        ]
    }

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_response, mock_root_contents],
    ):
        result = read_client.list_drives_and_root_contents("site123")
        assert result == mock_response
        assert "Found 1 drives" in caplog.text
        assert "Processing drive: Drive1" in caplog.text
        assert "Drive 'Drive1' contains 1 folders and 1 files" in caplog.text


def test_list_drives_and_root_contents_no_access_token(read_client: ReadClient) -> None:
    """Test that list_drives_and_root_contents returns None when there is no access token."""
    read_client.client.access_token = None
    result = read_client.list_drives_and_root_contents(site_id="mock-site-id")
    assert result is None


def test_list_drives_and_root_contents_empty_response(
    read_client: ReadClient, caplog: Any
) -> None:
    """Test listing drives and root contents when no drives are present."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Any]] = {"value": []}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_drives_and_root_contents(site_id="mock-site-id")
        assert result == {"value": []}
        assert "Found 0 drives" in caplog.text


def test_list_drives_and_root_contents_no_contents(
    read_client: ReadClient, caplog: Any
) -> None:
    """Test listing drives and root contents when root folders are empty."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_drive_response: Dict[str, List[Dict[str, str]]] = {
        "value": [{"name": "Drive1", "id": "drive1"}]
    }
    mock_empty_contents: Dict[str, List[Any]] = {"value": []}

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_drive_response, mock_empty_contents],
    ):
        result = read_client.list_drives_and_root_contents("site123")
        assert result == mock_drive_response
        assert "Found 1 drives" in caplog.text
        assert "Processing drive: Drive1" in caplog.text
        assert "Drive 'Drive1' contains 0 folders and 0 files" in caplog.text


def test_list_drives_and_root_contents_with_items(
    read_client: ReadClient, caplog: Any
) -> None:
    """Test listing drives and root contents with items."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"id": "drive1", "name": "Drive1"},
        ]
    }
    mock_root_contents: Dict[str, List[Dict[str, Any]]] = {
        "value": [
            {"name": "Folder1", "folder": {}},
            {"name": "File1", "file": {}},
        ]
    }

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_response, mock_root_contents],
    ):
        result = read_client.list_drives_and_root_contents("site123")
        assert result == mock_response
        assert "Found 1 drives" in caplog.text
        assert "Processing drive: Drive1" in caplog.text
        assert "Drive 'Drive1' contains 1 folders and 1 files" in caplog.text


def test_list_drives_and_root_contents_no_items_in_root_folder(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test listing drives and root contents where root folder contains no items.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_drive_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"id": "drive1", "name": "Drive1"},
        ]
    }
    mock_empty_root_response: Dict[str, Any] = {"value": []}  # Empty root contents

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_drive_response, mock_empty_root_response],
    ):
        result = read_client.list_drives_and_root_contents("site123")
        assert result == mock_drive_response
        assert "Found 1 drives" in caplog.text
        assert "Processing drive: Drive1" in caplog.text
        assert "Drive 'Drive1' contains 0 folders and 0 files" in caplog.text


def test_list_drives_and_root_contents_no_response(read_client: ReadClient) -> None:
    """Test listing drives and root contents when make_graph_request returns None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_drives_and_root_contents("site123")
        assert result is None


def test_list_drive_names_success(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful listing of drive names."""
    mock_base_client.make_graph_request.return_value = {
        "value": [
            {"name": "Documents"},
            {"name": "Shared Documents"},
            {"name": "Site Assets"},
        ]
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    drive_names = read_client.list_drive_names("site123")

    assert drive_names == ["Documents", "Shared Documents", "Site Assets"]
    assert "Found 3 drives" in caplog.text
    assert (
        "Drive names: ['Documents', 'Shared Documents', 'Site Assets']" in caplog.text
    )


def test_list_drive_names_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    drive_names = read_client.list_drive_names("site123")

    assert drive_names is None


def test_list_drive_names_no_response(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.make_graph_request.return_value = None

    drive_names = read_client.list_drive_names("site123")

    assert drive_names is None


def test_list_drive_names_empty_list(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when no drives are found."""
    mock_base_client.make_graph_request.return_value = {"value": []}

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    drive_names = read_client.list_drive_names("site123")

    assert drive_names == []
    assert "Found 0 drives" in caplog.text
    assert "Drive names: []" in caplog.text


def test_list_drive_names_missing_names(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when some drives don't have names."""
    mock_base_client.make_graph_request.return_value = {
        "value": [{"name": "Documents"}, {}, {"name": "Site Assets"}]  # Missing name
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    drive_names = read_client.list_drive_names("site123")

    assert drive_names == ["Documents", None, "Site Assets"]
    assert "Found 3 drives" in caplog.text
    assert "Drive names: ['Documents', None, 'Site Assets']" in caplog.text


def test_get_drive_id_success(read_client: ReadClient, caplog: Any) -> None:
    """Test getting a drive ID successfully."""
    caplog.set_level("INFO", logger="sharepycrud.readClient")
    mock_response = {"value": [{"name": "Drive1", "id": "mock-drive-id"}]}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_drive_id("mock-site-id", "Drive1")

    assert result == "mock-drive-id"
    assert "Found drive: Drive1, ID: mock-drive-id" in caplog.text


def test_get_drive_id_no_access_token(read_client: ReadClient) -> None:
    """Test that get_drive_id returns None when there is no access token."""
    read_client.client.access_token = None
    result = read_client.get_drive_id(site_id="mock-site-id", drive_name="Drive1")
    assert result is None


def test_get_drive_id_no_response(read_client: ReadClient) -> None:
    """Test that get_drive_id returns None when make_graph_request returns None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.get_drive_id(site_id="mock-site-id", drive_name="Drive1")
        assert result is None


def test_get_drive_id_not_found(read_client: ReadClient, caplog: Any) -> None:
    """Test that getting a drive ID returns None when drive is not found."""
    caplog.set_level("INFO", logger="sharepycrud.readClient")
    mock_response: Dict[str, List[Dict[str, str]]] = {"value": []}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_drive_id("mock-site-id", "NonexistentDrive")

    assert result is None
    assert "Drive not found: NonexistentDrive" in caplog.text


def test_list_drive_ids_with_drives(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_drive_ids when drives are present.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    # Mock the make_graph_request to return drives
    mock_response = {
        "value": [
            {"id": "drive1", "name": "Drive 1"},
            {"id": "drive2", "name": "Drive 2"},
        ]
    }
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_drive_ids("site123")
        assert result == [("drive1", "Drive 1"), ("drive2", "Drive 2")]
        assert "Found 2 drives" in caplog.text


def test_list_drive_ids_no_drives(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_drive_ids when no drives are found.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    # Mock the make_graph_request to return an empty list of drives
    mock_response: Dict[str, List[Any]] = {"value": []}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_drive_ids("site123")
        assert result == []
        assert "Found 0 drives" in caplog.text


def test_list_drive_ids_no_access_token(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_drive_ids when access token is missing.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    # Remove access token to simulate missing token
    read_client.client.access_token = None
    result = read_client.list_drive_ids("site123")
    assert result == []
    assert "Found" not in caplog.text


def test_list_all_folders_with_folders(read_client: ReadClient, caplog: Any) -> None:
    """Test list_all_folders with nested folder structure."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    root_response: Dict[str, List[Dict[str, Any]]] = {
        "value": [
            {
                "name": "Folder1",
                "id": "folder1",
                "parentReference": {"path": "/drives/drive1"},
                "folder": {},
            }
        ]
    }

    folder1_response: Dict[str, List[Dict[str, Any]]] = {
        "value": [
            {
                "name": "SubFolder1",
                "id": "subfolder1",
                "parentReference": {"path": "/drives/drive1/Folder1"},
                "folder": {},
            }
        ]
    }

    subfolder1_response: Dict[str, List[Dict[str, Any]]] = {"value": []}
    call_count = 0

    # Define a mock function to simulate make_graph_request to prevent recursion
    def mock_make_graph_request(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return root_response
        elif call_count == 2:
            return folder1_response
        else:
            return subfolder1_response

    call_count = 0
    with patch.object(
        read_client.client, "make_graph_request", side_effect=mock_make_graph_request
    ):
        result = read_client.list_all_folders("drive1")

    expected: List[Dict[str, Any]] = [
        {"name": "Folder1", "id": "folder1", "path": "/drives/drive1/Folder1"},
        {
            "name": "SubFolder1",
            "id": "subfolder1",
            "path": "/drives/drive1/Folder1/SubFolder1",
        },
    ]

    assert result == expected
    assert "Processing folder: Folder1 at level 0" in caplog.text
    assert "Processing folder: SubFolder1 at level 1" in caplog.text
    assert "Found 1 subfolders in Folder1" in caplog.text


def test_list_all_folders_empty(read_client: ReadClient) -> None:
    """Test list_all_folders when no folders exist."""
    mock_response: Dict[str, List[Any]] = {"value": []}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_all_folders("drive1")

    assert result == []


def test_list_all_folders_no_response(read_client: ReadClient) -> None:
    """Test list_all_folders when make_graph_request returns None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_all_folders("drive1")

    assert result == []


def test_list_all_folders_no_access_token(read_client: ReadClient) -> None:
    """Test list_all_folders when access token is missing."""
    read_client.client.access_token = None
    result = read_client.list_all_folders("drive1")
    assert result == []


def test_list_parent_folders_success(read_client: ReadClient, caplog: Any) -> None:
    """Test that list_parent_folders returns the correct parent folders."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_response = {
        "value": [
            {
                "name": "ParentFolder1",
                "id": "folder1",
                "parentReference": {"path": "/Drive1"},
                "folder": {},
            },
            {
                "name": "ParentFolder2",
                "id": "folder2",
                "parentReference": {"path": "/Drive1"},
                "folder": {},
            },
        ]
    }

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_parent_folders("drive1")

    expected = [
        {"name": "ParentFolder1", "path": "/Drive1/ParentFolder1"},
        {"name": "ParentFolder2", "path": "/Drive1/ParentFolder2"},
    ]
    assert result == expected
    assert "Found parent folder: ParentFolder1" in caplog.text
    assert "Found parent folder: ParentFolder2" in caplog.text
    assert "Found 2 parent folders" in caplog.text


def test_list_parent_folders_no_access_token(read_client: ReadClient) -> None:
    """Test that list_parent_folders returns None if no access token is present."""
    read_client.client.access_token = None
    result = read_client.list_parent_folders("drive1")
    assert result is None


def test_list_parent_folders_no_response(read_client: ReadClient) -> None:
    """Test that list_parent_folders returns None when make_graph_request returns None."""
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_parent_folders("drive1")
    assert result is None


def test_list_parent_folders_empty(read_client: ReadClient, caplog: Any) -> None:
    """Test that list_parent_folders handles no folders correctly."""
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
    mock_response: Dict[str, List[Any]] = {"value": []}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_parent_folders("drive1")

    assert result == []
    assert "Found 0 parent folders" in caplog.text


def test_get_root_folder_id_by_name_success(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful retrieval of root folder ID by name."""
    # Mocking client responses with proper typing
    mock_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"name": "TestFolder", "id": "12345"},
            {"name": "OtherFolder", "id": "67890"},
        ]
    }

    mock_base_client.format_graph_url = MagicMock(return_value="mock_url")
    mock_base_client.make_graph_request = MagicMock(return_value=mock_response)

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    folder_id = read_client.get_root_folder_id_by_name("dummy_drive_id", "TestFolder")

    # Assertions
    assert folder_id == "12345"
    assert "Found folder: TestFolder, ID: 12345" in caplog.text


def test_get_root_folder_id_by_name_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    folder_id = read_client.get_root_folder_id_by_name("dummy_drive_id", "TestFolder")

    # Assertions
    assert folder_id is None
    assert "Found folder:" not in caplog.text


def test_get_root_folder_id_by_name_folder_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_base_client.format_graph_url.return_value = "mock_url"
    mock_base_client.make_graph_request.return_value = {
        "value": [{"name": "OtherFolder", "id": "67890"}]
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    folder_id = read_client.get_root_folder_id_by_name("dummy_drive_id", "TestFolder")

    # Assertions
    assert folder_id is None
    assert "Found folder:" not in caplog.text


def test_get_folder_content_success(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful retrieval of folder contents."""
    mock_base_client.format_graph_url.return_value = "mock_url"
    mock_base_client.make_graph_request.return_value = {
        "value": [
            {
                "id": "123",
                "name": "File1",
                "webUrl": "http://mockurl.com/file1",
                "size": 2048,
            },
            {
                "id": "124",
                "name": "Folder1",
                "folder": {},
                "webUrl": "http://mockurl.com/folder1",
            },
        ]
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    folder_contents = read_client.get_folder_content(
        "dummy_drive_id", "dummy_folder_id"
    )

    assert folder_contents == [
        {
            "id": "123",
            "name": "File1",
            "type": "file",
            "webUrl": "http://mockurl.com/file1",
            "size": 2048,
        },
        {
            "id": "124",
            "name": "Folder1",
            "type": "folder",
            "webUrl": "http://mockurl.com/folder1",
            "size": "N/A",
        },
    ]
    assert "Found 1 folders and 1 files" in caplog.text


def test_get_folder_content_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None
    folder_contents = read_client.get_folder_content(
        "dummy_drive_id", "dummy_folder_id"
    )
    assert folder_contents is None


def test_get_folder_content_no_response(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.format_graph_url.return_value = "mock_url"
    mock_base_client.make_graph_request.return_value = None

    folder_contents = read_client.get_folder_content(
        "dummy_drive_id", "dummy_folder_id"
    )
    assert folder_contents is None


def test_get_nested_folder_info_success(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful nested folder traversal."""
    mock_base_client.format_graph_url = MagicMock(
        side_effect=lambda *args: f"mock_url/{'/'.join(args)}"
    )
    mock_base_client.make_graph_request = MagicMock(
        side_effect=[
            {
                "value": [
                    {"id": "123", "name": "Folder1", "folder": {}, "extra": "data"}
                ]
            },
            {
                "value": [
                    {"id": "456", "name": "SubFolder", "folder": {}, "extra": "data"}
                ]
            },
        ]
    )

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    with patch.object(
        read_client, "parse_folder_path", return_value=["Folder1", "SubFolder"]
    ):
        folder_info = read_client.get_nested_folder_info(
            "dummy_drive_id", "Folder1/SubFolder"
        )

    assert folder_info == {"id": "456", "name": "SubFolder"}
    assert "Processing folder: Folder1" in caplog.text
    assert "Processing folder: SubFolder" in caplog.text
    assert "Found deepest folder: SubFolder" in caplog.text


def test_get_nested_folder_info_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None
    folder_info = read_client.get_nested_folder_info(
        "dummy_drive_id", "Folder1/SubFolder"
    )
    assert folder_info is None


def test_get_nested_folder_info_no_response(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.format_graph_url = MagicMock(return_value="mock_url")
    mock_base_client.make_graph_request = MagicMock(return_value=None)

    with patch.object(read_client, "parse_folder_path", return_value=["Folder1"]):
        folder_info = read_client.get_nested_folder_info("dummy_drive_id", "Folder1")

    assert folder_info is None


def test_get_nested_folder_info_folder_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when folder is not found in the response."""
    mock_base_client.format_graph_url = MagicMock(return_value="mock_url")
    mock_base_client.make_graph_request = MagicMock(
        return_value={"value": [{"id": "123", "name": "DifferentFolder", "folder": {}}]}
    )

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    with patch.object(read_client, "parse_folder_path", return_value=["Folder1"]):
        folder_info = read_client.get_nested_folder_info("dummy_drive_id", "Folder1")

    assert folder_info is None
    assert "Folder not found: Folder1" in caplog.text


def test_get_nested_folder_info_empty_path(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when folder path is empty."""
    with patch.object(read_client, "parse_folder_path", return_value=[]):
        folder_info = read_client.get_nested_folder_info("dummy_drive_id", "")

    assert folder_info is None


def test_file_exists_in_folder_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when file is found in folder."""
    mock_base_client.make_graph_request.return_value = {
        "value": [
            {
                "name": "test.txt",
                "file": {},
            }
        ]
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    result = read_client.file_exists_in_folder("drive123", "folder123", "test.txt")

    assert result is True
    assert "Found file: test.txt" in caplog.text


def test_file_exists_in_folder_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when file is not found in folder."""
    mock_base_client.make_graph_request.return_value = {
        "value": [
            {
                "name": "other.txt",
                "file": {},
            }
        ]
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    result = read_client.file_exists_in_folder("drive123", "folder123", "test.txt")

    assert result is False
    assert "File not found: test.txt" in caplog.text


def test_file_exists_in_folder_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    result = read_client.file_exists_in_folder("drive123", "folder123", "test.txt")

    assert result is False


def test_file_exists_in_folder_no_response(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.make_graph_request.return_value = None

    result = read_client.file_exists_in_folder("drive123", "folder123", "test.txt")

    assert result is False


def test_download_file_success(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful file download."""
    # Mock responses for each step
    mock_base_client.make_graph_request.side_effect = [
        {"id": "site123"},  # get_site_id response
        {"value": [{"name": "TestDrive", "id": "drive123"}]},  # get_drive_id response
        {"value": [{"name": "test.txt", "id": "file123"}]},  # list_response
    ]

    # Mock the download request
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"file content"

    with patch("requests.get", return_value=mock_response):
        caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
        result = read_client.download_file("test.txt", "TestSite", "TestDrive")

    assert result == b"file content"
    assert "Found file: test.txt" in caplog.text
    assert "Successfully downloaded: test.txt" in caplog.text


def test_download_file_no_access_token(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None
    result = read_client.download_file("test.txt", "TestSite", "TestDrive")
    assert result is None


def test_download_file_no_list_response(
    read_client: ReadClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when list_response is None."""
    mock_base_client.make_graph_request.side_effect = [
        {"id": "site123"},  # get_site_id response
        {"value": [{"name": "TestDrive", "id": "drive123"}]},  # get_drive_id response
        None,  # list_response is None
    ]

    result = read_client.download_file("test.txt", "TestSite", "TestDrive")
    assert result is None


def test_download_file_site_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when site is not found."""
    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
    result = read_client.download_file("test.txt", "NonexistentSite", "TestDrive")

    assert result is None
    assert "Site not found: NonexistentSite" in caplog.text


def test_download_file_drive_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when drive is not found."""
    mock_base_client.make_graph_request.side_effect = [
        {"id": "site123"},  # get_site_id response
        {"value": []},  # empty drive list
    ]

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
    result = read_client.download_file("test.txt", "TestSite", "NonexistentDrive")

    assert result is None
    assert "Drive not found: NonexistentDrive" in caplog.text


def test_download_file_not_found(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when file is not found."""
    mock_base_client.make_graph_request.side_effect = [
        {"id": "site123"},  # get_site_id response
        {"value": [{"name": "TestDrive", "id": "drive123"}]},  # get_drive_id response
        {"value": []},  # empty file list
    ]

    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
    result = read_client.download_file("nonexistent.txt", "TestSite", "TestDrive")

    assert result is None
    assert "File not found: nonexistent.txt" in caplog.text


def test_download_file_download_failed(
    read_client: ReadClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when download request fails."""
    mock_base_client.make_graph_request.side_effect = [
        {"id": "site123"},  # get_site_id response
        {"value": [{"name": "TestDrive", "id": "drive123"}]},  # get_drive_id response
        {"value": [{"name": "test.txt", "id": "file123"}]},  # list_response
    ]

    # Mock failed download request
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        caplog.set_level(logging.INFO, logger="sharepycrud.readClient")
        result = read_client.download_file("test.txt", "TestSite", "TestDrive")

    assert result is None
    assert "Failed to download: test.txt" in caplog.text
