import pytest
from unittest.mock import MagicMock, patch
from sharepycrud.readClient import ReadClient
from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Any, List, Dict, Optional
import requests
import logging


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
        assert "No sites found" in caplog.text


def test_list_sites_request_failure(read_client: ReadClient, caplog: Any) -> None:
    """
    Test listing sites when the API request fails.
    """
    caplog.set_level("INFO", logger="sharepycrud.readClient")

    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_sites()
        assert result is None
        assert "No sites found" not in caplog.text
        assert "Failed to retrieve sites" in caplog.text


def test_list_sites_no_token(read_client: ReadClient) -> None:
    """Test listing sites when access token is missing."""
    read_client.client.access_token = None
    result = read_client.list_sites()
    assert result is None


def test_get_site_id_success(read_client: ReadClient, caplog: Any) -> None:
    """Test getting a site ID successfully."""
    caplog.set_level("INFO")
    mock_response = {"id": "mock-site-id"}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_site_id("mock-site-name")
        assert result == "mock-site-id"
        assert "Found site: mock-site-name" in caplog.text
        assert "Site ID: mock-site-id" in caplog.text


def test_get_site_id_no_access_token(read_client: ReadClient) -> None:
    """
    Test that get_site_id returns None when there is no access token.
    """
    read_client.client.access_token = None
    result = read_client.get_site_id(site_name="TestSite")
    assert result is None


def test_get_site_id_no_site_name(read_client: ReadClient, caplog: Any) -> None:
    """
    Test that get_site_id logs an error and returns None when site_name is empty.
    """
    caplog.set_level("ERROR", logger="sharepycrud.readClient")
    result = read_client.get_site_id(site_name="")
    assert result is None
    assert "Site name is required" in caplog.text


def test_get_site_id_not_found(read_client: ReadClient) -> None:
    """
    Test that get_site_id returns None when the site ID is not found.
    """
    mock_response = {"id": None}  # Site ID is not present
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_site_id(site_name="TestSite")
        assert result is None


def test_get_site_id_request_failure(read_client: ReadClient) -> None:
    """
    Test that get_site_id returns None when the API request fails.
    """
    with patch.object(read_client.client, "make_graph_request", side_effect=ValueError):
        result = read_client.get_site_id(site_name="TestSite")
        assert result is None


def test_get_site_id_failure(read_client: ReadClient, caplog: Any) -> None:
    """Test failure to get a site ID."""
    caplog.set_level("ERROR")
    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=requests.exceptions.RequestException,
    ):
        result = read_client.get_site_id("mock-site-name")
        assert result is None
        assert "Site name is required" not in caplog.text


def test_list_drives_success(read_client: ReadClient) -> None:
    """Test listing drives successfully."""
    mock_response: Dict[str, List[Dict[str, str]]] = {
        "value": [{"name": "Drive1", "id": "drive-id-1"}]
    }
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_drives("mock-site-id")
        assert result == mock_response


def test_list_drives_no_access_token(read_client: ReadClient) -> None:
    """
    Test that list_drives returns None when there is no access token.
    """
    read_client.client.access_token = None
    result = read_client.list_drives(site_id="mock-site-id")
    assert result is None


def test_list_drives_no_drives(read_client: ReadClient, caplog: Any) -> None:
    """
    Test that list_drives handles no drives being present.
    """
    caplog.set_level("INFO", logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Any]] = {"value": []}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_drives(site_id="mock-site-id")
        assert result == {"value": []}
        assert "No items in root folder" not in caplog.text


def test_list_drives_with_items(read_client: ReadClient, caplog: Any) -> None:
    """
    Test listing drives with items.
    """
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

    # Simulate sequence of calls for make_graph_request
    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_response, mock_root_contents],
    ):
        result = read_client.list_drives("site123")
        assert result == mock_response
        assert "=== Drives ===" in caplog.text
        assert "Drive: Drive1, ID: drive1" in caplog.text
        assert "Root contents:" in caplog.text
        assert "- Folder1 (folder)" in caplog.text
        assert "- File1 (file)" in caplog.text


def test_list_drives_no_items_in_root_folder(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test listing drives where root folder contains no items.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_drive_response: Dict[str, List[Dict[str, str]]] = {
        "value": [
            {"id": "drive1", "name": "Drive1"},
        ]
    }
    mock_empty_root_response: Dict[str, Any] = (
        {}
    )  # Simulate no "value" key in root contents

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=[mock_drive_response, mock_empty_root_response],
    ):
        result = read_client.list_drives("site123")
        assert result == mock_drive_response
        assert "=== Drives ===" in caplog.text
        assert "Drive: Drive1, ID: drive1" in caplog.text
        assert "No items in root folder" in caplog.text


def test_list_drives_request_failure(read_client: ReadClient, caplog: Any) -> None:
    """
    Test failure to list drives due to a request error.
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_drives("site123")
        assert result is None
        assert "Failed to list drives" in caplog.text


def test_get_drive_id_success(read_client: ReadClient, caplog: Any) -> None:
    """Test getting a drive ID successfully."""
    caplog.set_level("INFO")
    mock_response = {"value": [{"name": "Drive1", "id": "mock-drive-id"}]}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_drive_id("mock-site-id", "Drive1")
        assert result == "mock-drive-id"
        assert "Found drive: Drive1" in caplog.text


def test_get_drive_id_no_access_token(read_client: ReadClient) -> None:
    """
    Test that get_drive_id returns None when there is no access token.
    """
    read_client.client.access_token = None
    result = read_client.get_drive_id(site_id="mock-site-id", drive_name="Drive1")
    assert result is None


def test_get_drive_id_failed_to_list_drives(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test that get_drive_id returns None when the API request fails.
    """
    caplog.set_level("ERROR", logger="sharepycrud.readClient")
    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.get_drive_id(site_id="mock-site-id", drive_name="Drive1")
        assert result is None
        assert "Failed to list drives" in caplog.text


def test_get_drive_id_not_found(read_client: ReadClient, caplog: Any) -> None:
    """
    Test that getting a drive ID fails when not found.
    """
    caplog.set_level("ERROR", logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Dict[str, str]]] = {"value": []}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.get_drive_id("mock-site-id", "NonexistentDrive")
        assert result is None
        assert "Failed to list drives" not in caplog.text


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
    """
    Test list_all_folders with valid folders in the response, including controlled recursion.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    # Mock responses for different folder levels
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

    subfolder1_response: Dict[str, List[Dict[str, Any]]] = {
        "value": []
    }  # Termination case

    # Keep track of call count to return different responses
    call_count = 0

    def mock_make_graph_request(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        nonlocal call_count
        call_count += 1

        if call_count == 1:  # First call for root folder
            return root_response
        elif call_count == 2:  # Second call for Folder1
            return folder1_response
        else:
            return subfolder1_response

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

    assert result == expected, f"Expected: {expected}, Got: {result}"
    assert "- Folder: Folder1 (ID: folder1)" in caplog.text
    assert "  - Folder: SubFolder1 (ID: subfolder1)" in caplog.text
    assert "Found 0 subfolders" in caplog.text
    assert "Found 1 subfolders" in caplog.text


def test_list_all_folders_no_folders(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_all_folders when no folders are returned in the response.
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Any]] = {"value": []}
    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_all_folders("drive1")

    assert result == []
    assert "Failed to list folder contents" not in caplog.text


def test_list_all_folders_request_failure(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_all_folders when the request fails (no response or invalid format).
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    with patch.object(read_client.client, "make_graph_request", return_value=None):
        result = read_client.list_all_folders("drive1")

    assert result == []
    assert "Failed to list folder contents" in caplog.text


def test_list_all_folders_no_access_token(read_client: ReadClient, caplog: Any) -> None:
    """
    Test list_all_folders when the access token is missing.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    read_client.client.access_token = None
    result = read_client.list_all_folders("drive1")

    assert result == []
    assert "Failed to list folder contents" not in caplog.text
    assert "Found" not in caplog.text


def test_list_parent_folders_success(read_client: ReadClient, caplog: Any) -> None:
    """
    Test that list_parent_folders returns the correct parent folders.
    """
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
    assert result == expected, f"Expected: {expected}, Got: {result}"
    assert "Found parent folder: ParentFolder1" in caplog.text
    assert "Found parent folder: ParentFolder2" in caplog.text


def test_list_parent_folders_no_access_token(read_client: ReadClient) -> None:
    """
    Test that list_parent_folders returns None if no access token is present.
    """
    read_client.client.access_token = None
    result = read_client.list_parent_folders("drive1")
    assert result is None


def test_list_parent_folders_unexpected_response_format(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test that list_parent_folders handles an unexpected response format.
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    with patch.object(read_client.client, "make_graph_request", return_value=[]):
        result = read_client.list_parent_folders("drive1")
    assert result is None
    assert "Unexpected response format" in caplog.text


def test_list_parent_folders_with_error_response(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test that list_parent_folders handles an error response.
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    mock_response = {
        "error": {
            "code": "BadRequest",
            "message": "An error occurred while fetching folder contents.",
        }
    }

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_parent_folders("drive1")
    assert result is None
    assert "Error getting folder contents: BadRequest" in caplog.text
    assert "Message: An error occurred while fetching folder contents." in caplog.text


def test_list_parent_folders_empty_response(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test that list_parent_folders returns an empty list if there are no folders.
    """
    caplog.set_level(logging.INFO, logger="sharepycrud.readClient")

    mock_response: Dict[str, List[Any]] = {"value": []}

    with patch.object(
        read_client.client, "make_graph_request", return_value=mock_response
    ):
        result = read_client.list_parent_folders("drive1")
    assert result == []
    assert "Found parent folder:" not in caplog.text


def test_list_parent_folders_request_exception(
    read_client: ReadClient, caplog: Any
) -> None:
    """
    Test that list_parent_folders handles request exceptions.
    """
    caplog.set_level(logging.ERROR, logger="sharepycrud.readClient")

    with patch.object(
        read_client.client,
        "make_graph_request",
        side_effect=Exception("Mock Exception"),
    ):
        result = read_client.list_parent_folders("drive1")
    assert result is None
    assert "An unexpected error occurred: Mock Exception" in caplog.text
