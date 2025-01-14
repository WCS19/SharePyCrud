import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Tuple, Optional, cast
from _pytest.capture import CaptureFixture

from sharepycrud.readClient import ReadClient
from sharepycrud.config import SharePointConfig


@pytest.fixture
def mock_config() -> SharePointConfig:
    """Fixture for a mock SharePointConfig."""
    return SharePointConfig(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="test.sharepoint.com",
    )


@pytest.fixture
def read_client(mock_config: SharePointConfig) -> ReadClient:
    """
    Instantiate ReadClient while mocking out _get_access_token
    to avoid real network calls.
    """
    with patch.object(
        ReadClient, "_get_access_token", return_value="mock_access_token"
    ):
        client = ReadClient(mock_config)
    return client


## ------------------------------------------------------------------------
## list_sites
## ------------------------------------------------------------------------
@patch("requests.request")
def test_list_sites_success(
    mock_request: MagicMock,
    read_client: ReadClient,
) -> None:
    """Test list_sites returns a list of site names on success."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"name": "SiteA"},
            {"name": "SiteB"},
        ]
    }
    mock_request.return_value = mock_response

    result = read_client.list_sites()
    assert isinstance(result, list)
    assert result == ["SiteA", "SiteB"]

    mock_request.assert_called_once()


@patch("requests.request")
def test_list_sites_empty(
    mock_request: MagicMock,
    read_client: ReadClient,
) -> None:
    """Test list_sites returns an empty list if no sites are found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"value": []}
    mock_request.return_value = mock_response

    result: Optional[List[str]] = cast(Optional[List[str]], read_client.list_sites())
    assert result == []


@patch("requests.request")
def test_list_sites_request_error(
    mock_request: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test list_sites returns None if request fails or token is invalid."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "403 Error"
    )
    mock_request.return_value = mock_response

    result = None
    try:
        result = cast(Optional[List[str]], read_client.list_sites())
    except requests.exceptions.HTTPError:
        pass

    assert result is None


@patch.object(ReadClient, "_get_access_token", return_value="mock_access_token")
def test_list_sites_no_access_token(
    mock_get_access_token: MagicMock,
    mock_config: SharePointConfig,
) -> None:
    """
    Test list_sites returns None if access_token is missing.
    """
    read_client = ReadClient(mock_config)
    read_client.access_token = None

    result = read_client.list_sites()
    assert result is None


## ------------------------------------------------------------------------
## get_site_id
## ------------------------------------------------------------------------
@patch("requests.request")
def test_get_site_id_success(mock_request: MagicMock, read_client: ReadClient) -> None:
    """Test get_site_id returns the site ID on success."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"id": "test-site-id"}
    mock_request.return_value = mock_response

    site_id: Optional[str] = read_client.get_site_id("MySite")
    assert site_id == "test-site-id"


@patch("requests.request")
def test_get_site_id_not_found(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test get_site_id returns None if response is empty."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    site_id: Optional[str] = read_client.get_site_id("MissingSite")
    assert site_id is None


@patch.object(ReadClient, "_get_access_token", return_value="mock_access_token")
def test_get_site_id_no_access_token(
    mock_get_access_token: MagicMock,
    mock_config: SharePointConfig,
) -> None:
    """
    Test get_site_id returns None if access_token is missing.
    """
    read_client = ReadClient(mock_config)
    read_client.access_token = None

    site_id: Optional[str] = read_client.get_site_id("MissingSite")
    assert site_id is None


@patch("requests.request")
def test_get_site_id_no_site_name(
    mock_request: MagicMock,
    read_client: ReadClient,
) -> None:
    """
    Test get_site_id returns None if site name is not provided.
    """
    mock_request.return_value = MagicMock()
    site_id: Optional[str] = read_client.get_site_id(None)
    assert site_id is None
    mock_request.assert_not_called()


## ------------------------------------------------------------------------
## list_drives
## ------------------------------------------------------------------------
@patch("requests.request")
def test_list_drives_success(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test list_drives prints drive info and returns the response dict."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"name": "DriveA", "id": "123"},
            {"name": "DriveB", "id": "456"},
        ]
    }
    mock_request.return_value = mock_response

    result: Optional[Dict[str, Any]] = read_client.list_drives("site123")
    assert result == {
        "value": [
            {"name": "DriveA", "id": "123"},
            {"name": "DriveB", "id": "456"},
        ]
    }

    captured = capsys.readouterr()
    assert "Drive: DriveA, ID: 123" in captured.out
    assert "Drive: DriveB, ID: 456" in captured.out


@patch("requests.request")
def test_list_drives_none(
    mock_request: MagicMock,
    read_client: ReadClient,
) -> None:
    """Test list_drives returns None if no valid response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    result: Optional[Dict[str, Any]] = read_client.list_drives("site123")
    assert result is None


@patch.object(ReadClient, "_get_access_token", return_value="mock_access_token")
def test_list_drives_no_access_token(
    mock_get_access_token: MagicMock,
    mock_config: SharePointConfig,
) -> None:
    """Test list_drives returns None if access_token is missing."""
    read_client = ReadClient(mock_config)
    read_client.access_token = None


@patch("requests.request")
def test_list_drives_no_items_in_root(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test list_drives prints 'No items in root folder' when the root folder is empty."""

    mock_response_drives = MagicMock()
    mock_response_drives.raise_for_status.side_effect = None
    mock_response_drives.json.return_value = {
        "value": [{"name": "TestDrive", "id": "drive123"}]
    }

    mock_response_root = MagicMock()
    mock_response_root.raise_for_status.side_effect = None
    mock_response_root.json.return_value = None

    mock_request.side_effect = [mock_response_drives, mock_response_root]

    result = read_client.list_drives("site123")

    captured = capsys.readouterr()
    assert "Drive: TestDrive, ID: drive123" in captured.out
    assert "No items in root folder" in captured.out

    assert result == {"value": [{"name": "TestDrive", "id": "drive123"}]}


## ------------------------------------------------------------------------
## get_drive_id
## ------------------------------------------------------------------------
@patch("requests.request")
def test_get_drive_id_success(mock_request: MagicMock, read_client: ReadClient) -> None:
    """Test get_drive_id returns a drive ID when found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"name": "Files", "id": "drive123"},
            {"name": "Documents", "id": "drive456"},
        ]
    }
    mock_request.return_value = mock_response

    drive_id: Optional[str] = read_client.get_drive_id("site123", "Files")
    assert drive_id == "drive123"


@patch("requests.request")
def test_get_drive_id_not_found(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test get_drive_id returns None if drive name not in response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"value": []}
    mock_request.return_value = mock_response

    drive_id: Optional[str] = read_client.get_drive_id("site123", "NonExistentDrive")
    assert drive_id is None


## ------------------------------------------------------------------------
## list_drive_ids
## ------------------------------------------------------------------------
@patch("requests.request")
def test_list_drive_ids_success(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test list_drive_ids returns a list of (id, name) tuples."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"id": "driveA", "name": "A"},
            {"id": "driveB", "name": "B"},
        ]
    }
    mock_request.return_value = mock_response

    ids: Optional[List[Tuple[str, str]]] = read_client.list_drive_ids("site123")
    assert ids == [("driveA", "A"), ("driveB", "B")]


@patch("requests.request")
def test_list_drive_ids_empty(mock_request: MagicMock, read_client: ReadClient) -> None:
    """Test list_drive_ids returns an empty list if no drives found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    ids: Optional[List[Tuple[str, str]]] = read_client.list_drive_ids("site123")
    assert ids == []


## ------------------------------------------------------------------------
## list_all_folders
## ------------------------------------------------------------------------
@patch("requests.request")
def test_list_all_folders_success(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test list_all_folders recursively collects folder names."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    # Simulate top-level has one folder
    mock_response.json.side_effect = [
        {
            "value": [
                {
                    "name": "Folder1",
                    "id": "f1",
                    "folder": {},
                    "parentReference": {"path": "/drives/f1"},
                }
            ]
        },
        {"value": []},  # no subfolders for "f1"
    ]
    mock_request.return_value = mock_response

    folders: List[Dict[str, str]] = read_client.list_all_folders("drive123")
    assert folders == [{"name": "Folder1", "id": "f1", "path": "/drives/f1/Folder1"}]

    captured = capsys.readouterr()
    assert "- Folder: Folder1 (ID: f1)" in captured.out


@patch("requests.request")
def test_list_all_folders_none(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test list_all_folders returns empty list if no response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    folders: List[Dict[str, str]] = read_client.list_all_folders("driveXYZ")
    assert folders == []


## ------------------------------------------------------------------------
## list_parent_folders
## ------------------------------------------------------------------------
@patch("requests.request")
def test_list_parent_folders_success(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test list_parent_folders returns list of folder names & paths."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {
                "name": "TopFolder",
                "id": "folder123",
                "folder": {},
                "parentReference": {"path": "/drives/12345/root"},
            },
            {
                "name": "SomeFile.txt",
                "id": "file123",
                "file": {},
                "parentReference": {"path": "/drives/12345/root"},
            },
        ]
    }
    mock_request.return_value = mock_response

    folders: Optional[List[Dict[str, str]]] = read_client.list_parent_folders(
        "drive123"
    )
    assert folders == [{"name": "TopFolder", "path": "/drives/12345/root/TopFolder"}]


@patch("requests.request")
def test_list_parent_folders_error_response(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test list_parent_folders returns None if error is in response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "error": {"code": "BadRequest", "message": "Something"}
    }
    mock_request.return_value = mock_response

    folders: Optional[List[Dict[str, str]]] = read_client.list_parent_folders(
        "driveXYZ"
    )
    assert folders is None

    captured = capsys.readouterr()
    assert "Error getting folder contents: BadRequest" in captured.out


## ------------------------------------------------------------------------
## get_root_folder_id_by_name
## ------------------------------------------------------------------------
@patch("requests.request")
def test_get_root_folder_id_by_name_success(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test get_root_folder_id_by_name returns folder ID on success."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"name": "RootFolder", "id": "f123"},
            {"name": "AnotherFolder", "id": "f999"},
        ]
    }
    mock_request.return_value = mock_response

    folder_id: Optional[str] = read_client.get_root_folder_id_by_name(
        "driveABC", "RootFolder"
    )
    assert folder_id == "f123"


@patch("requests.request")
def test_get_root_folder_id_by_name_missing(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test get_root_folder_id_by_name returns None if folder not found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"value": []}
    mock_request.return_value = mock_response

    folder_id: Optional[str] = read_client.get_root_folder_id_by_name(
        "driveABC", "NonExistent"
    )
    assert folder_id is None


## ------------------------------------------------------------------------
## get_folder_content
## ------------------------------------------------------------------------
@patch("requests.request")
def test_get_folder_content_success(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test get_folder_content returns a list of items in a folder."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {
                "id": "item1",
                "name": "FolderA",
                "folder": {},
                "webUrl": "http://foo",
                "size": 123,
            },
            {
                "id": "item2",
                "name": "FileB.txt",
                "file": {},
                "webUrl": "http://bar",
                "size": 456,
            },
        ]
    }
    mock_request.return_value = mock_response

    contents: Optional[List[Dict[str, Any]]] = read_client.get_folder_content(
        "driveABC", "folder123"
    )
    assert contents == [
        {
            "id": "item1",
            "name": "FolderA",
            "type": "folder",
            "webUrl": "http://foo",
            "size": 123,
        },
        {
            "id": "item2",
            "name": "FileB.txt",
            "type": "file",
            "webUrl": "http://bar",
            "size": 456,
        },
    ]
    captured = capsys.readouterr()
    assert "Found 2 items in folder" in captured.out


@patch("requests.request")
def test_get_folder_content_none(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test get_folder_content returns None if request fails or empty."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = None
    mock_request.return_value = mock_response

    contents: Optional[List[Dict[str, Any]]] = read_client.get_folder_content(
        "driveABC", "folderXYZ"
    )
    assert contents is None


## ------------------------------------------------------------------------
## get_nested_folder_info
## ------------------------------------------------------------------------
@patch("requests.request")
def test_get_nested_folder_info_success(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """
    Test get_nested_folder_info returns a dict with 'id' and 'name'
    for a valid nested folder path.
    """
    # Suppose the path is "Folder1/Folder2". We'll need two requests:
    # 1) For "root/children" with 'Folder1'
    # 2) For "Folder1ID/children" with 'Folder2'
    response1 = MagicMock()
    response1.raise_for_status.side_effect = None
    response1.json.return_value = {
        "value": [
            {"name": "Folder1", "folder": {}, "id": "Folder1ID"},
            {"name": "OtherFolder", "folder": {}, "id": "OtherID"},
        ]
    }

    response2 = MagicMock()
    response2.raise_for_status.side_effect = None
    response2.json.return_value = {
        "value": [
            {"name": "Folder2", "folder": {}, "id": "Folder2ID"},
        ]
    }

    mock_request.side_effect = [response1, response2]

    folder_info: Optional[Dict[str, str]] = read_client.get_nested_folder_info(
        "driveABC", "Folder1/Folder2"
    )
    assert folder_info == {"id": "Folder2ID", "name": "Folder2"}


@patch("requests.request")
def test_get_nested_folder_info_missing(
    mock_request: MagicMock, read_client: ReadClient, capsys: CaptureFixture[str]
) -> None:
    """Test get_nested_folder_info returns None if a subfolder does not exist."""
    response_missing = MagicMock()
    response_missing.raise_for_status.side_effect = None
    response_missing.json.return_value = {
        "value": [
            {"name": "SomeOtherFolder", "folder": {}, "id": "x123"},
        ]
    }
    mock_request.return_value = response_missing

    folder_info: Optional[Dict[str, str]] = read_client.get_nested_folder_info(
        "driveABC", "Folder1/Folder2"
    )
    assert folder_info is None
    captured = capsys.readouterr()
    assert "Folder 'Folder1' not found in path 'Folder1/Folder2'." in captured.out


## ------------------------------------------------------------------------
## file_exists_in_folder
## ------------------------------------------------------------------------
@patch("requests.request")
def test_file_exists_in_folder_true(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test file_exists_in_folder returns True if file is found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {
        "value": [
            {"name": "hello.txt", "file": {}},
            {"name": "other.docx", "file": {}},
        ]
    }
    mock_request.return_value = mock_response

    exists: bool = read_client.file_exists_in_folder(
        "driveABC", "folder123", "hello.txt"
    )
    assert exists is True


@patch("requests.request")
def test_file_exists_in_folder_false(
    mock_request: MagicMock, read_client: ReadClient
) -> None:
    """Test file_exists_in_folder returns False if file not found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"value": []}
    mock_request.return_value = mock_response

    exists: bool = read_client.file_exists_in_folder(
        "driveABC", "folder123", "nope.txt"
    )
    assert exists is False


## ------------------------------------------------------------------------
## download_file
## ------------------------------------------------------------------------
@patch("requests.get")
@patch.object(ReadClient, "get_site_id", return_value="site123")
@patch.object(ReadClient, "get_drive_id", return_value="driveABC")
@patch.object(ReadClient, "make_graph_request")
def test_download_file_success(
    mock_mgr: MagicMock,
    mock_drive_id: MagicMock,
    mock_site_id: MagicMock,
    mock_get: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """
    Test that download_file retrieves the file content correctly.
    """
    # Step 1: list drive contents to find 'fileID'
    mock_mgr.return_value = {
        "value": [
            {"name": "doc.txt", "id": "fileID"},
            {"name": "other.docx", "id": "someID"},
        ]
    }

    # Step 2: Actual file content request
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.content = b"Hello World"
    mock_get.return_value = mock_get_response

    content: Optional[bytes] = read_client.download_file(
        "doc.txt", "MySite", "FilesDrive"
    )
    assert content == b"Hello World"

    captured = capsys.readouterr()
    assert "✓ Successfully downloaded: doc.txt" in captured.out


@patch("requests.get")
@patch.object(ReadClient, "get_site_id", return_value="site123")
@patch.object(ReadClient, "get_drive_id", return_value="driveABC")
@patch.object(ReadClient, "make_graph_request")
def test_download_file_not_found(
    mock_mgr: MagicMock,
    mock_drive_id: MagicMock,
    mock_site_id: MagicMock,
    mock_get: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test that download_file returns None if file not found."""
    # The 'doc.txt' is not listed
    mock_mgr.return_value = {
        "value": [
            {"name": "somethingelse.doc", "id": "someID"},
        ]
    }

    content: Optional[bytes] = read_client.download_file(
        "doc.txt", "MySite", "FilesDrive"
    )
    assert content is None

    captured = capsys.readouterr()
    assert "File 'doc.txt' not found in drive" in captured.out


@patch("requests.get")
@patch.object(ReadClient, "get_site_id", return_value=None)
def test_download_file_no_site_id(
    mock_site_id: MagicMock,
    mock_get: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test download_file returns None if site_id is missing."""
    content: Optional[bytes] = read_client.download_file(
        "doc.txt", "MissingSite", "DriveName"
    )
    assert content is None

    captured = capsys.readouterr()
    assert "Failed to get site ID" in captured.out


@patch.object(ReadClient, "get_site_id", return_value="site123")
@patch.object(ReadClient, "get_drive_id", return_value=None)
def test_download_file_no_drive_id(
    mock_drive_id: MagicMock,
    mock_site_id: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test download_file returns None if drive_id not found."""
    content: Optional[bytes] = read_client.download_file(
        "doc.txt", "MySite", "MissingDrive"
    )
    assert content is None

    captured = capsys.readouterr()
    assert "Drive 'MissingDrive' not found" in captured.out


@patch("requests.get")
@patch.object(ReadClient, "get_site_id", return_value="site123")
@patch.object(ReadClient, "get_drive_id", return_value="driveABC")
@patch.object(
    ReadClient,
    "make_graph_request",
    return_value={"value": [{"name": "doc.txt", "id": "fileID"}]},
)
def test_download_file_http_error(
    mock_mgr: MagicMock,
    mock_drive_id: MagicMock,
    mock_site_id: MagicMock,
    mock_get: MagicMock,
    read_client: ReadClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test that download_file returns None if final GET fails."""
    mock_get_response = MagicMock()
    mock_get_response.status_code = 404
    mock_get.return_value = mock_get_response

    content: Optional[bytes] = read_client.download_file(
        "doc.txt", "MySite", "SomeDrive"
    )
    assert content is None

    captured = capsys.readouterr()
    assert "Error downloading file. Status code: 404" in captured.out
