import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Optional

from _pytest.capture import CaptureFixture

from sharepycrud.createClient import CreateClient
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
def create_client(mock_config: SharePointConfig) -> CreateClient:
    """
    Instantiate CreateClient while mocking out its token retrieval
    to avoid real network calls.
    """
    with patch.object(
        CreateClient, "_get_access_token", return_value="mock_access_token"
    ):
        client = CreateClient(mock_config)
    return client


## -----------------------------
## Tests for create_folder
## -----------------------------
@patch("requests.post")
def test_create_folder_success(
    mock_post: MagicMock, create_client: CreateClient
) -> None:
    """Test create_folder returns a valid folder ID on success (201)."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "fake-folder-id"}
    mock_post.return_value = mock_response

    folder_id: Optional[str] = create_client.create_folder("drive123", "TestFolder")
    assert folder_id == "fake-folder-id"

    expected_url = create_client.format_graph_url("drives", "drive123", "root/children")
    mock_post.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        json={
            "name": "TestFolder",
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        },
    )


@patch("requests.post")
def test_create_folder_failure(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """Test create_folder returns None and prints error on non-201 response."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad Request"}
    mock_post.return_value = mock_response

    folder_id: Optional[str] = create_client.create_folder("drive123", "FailFolder")
    assert folder_id is None

    captured = capsys.readouterr()
    assert "Error creating folder: 400" in captured.out
    assert "Bad Request" in captured.out


@patch("requests.post")
def test_create_folder_no_access_token(
    mock_post: MagicMock, create_client: CreateClient
) -> None:
    """Test create_folder returns None if access_token is missing."""
    create_client.access_token = None
    folder_id: Optional[str] = create_client.create_folder("drive123", "TestFolder")
    assert folder_id is None
    assert create_client.access_token is None


@patch("requests.post")
def test_create_folder_invalid_folder_id(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """
    Test create_folder prints an error and returns None when the created folder ID is not a string.
    """

    mock_response = MagicMock()
    mock_response.status_code = 201  # HTTP 201 Created
    mock_response.json.return_value = {"id": 12345}  # ID is an integer, not a string
    mock_post.return_value = mock_response

    folder_id: Optional[str] = create_client.create_folder("drive123", "TestFolder")

    assert folder_id is None

    captured = capsys.readouterr()
    assert "Error: Created folder ID is not a string" in captured.out


## -----------------------------
## Tests for create_file
## -----------------------------
@patch("requests.post")
def test_create_file_success(mock_post: MagicMock, create_client: CreateClient) -> None:
    """Test create_file returns a valid file ID on success."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "fake-file-id"}
    mock_post.return_value = mock_response

    file_id: Optional[str] = create_client.create_file(
        "drive123", "folderABC", "NewFile.txt"
    )
    assert file_id == "fake-file-id"

    expected_url = create_client.format_graph_url(
        "drives", "drive123", "items", "folderABC", "children"
    )
    mock_post.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        json={
            "name": "NewFile.txt",
            "file": {},
            "@microsoft.graph.conflictBehavior": "fail",
        },
    )


@patch("requests.post")
def test_create_file_failure(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """Test create_file returns None and prints error on failure."""
    mock_response = MagicMock()
    mock_response.status_code = 409
    mock_response.json.return_value = {"error": "Conflict"}
    mock_post.return_value = mock_response

    file_id: Optional[str] = create_client.create_file(
        "drive123", "folderABC", "DuplicateFile.txt"
    )
    assert file_id is None

    captured = capsys.readouterr()
    assert "Error creating file: 409" in captured.out
    assert "Conflict" in captured.out


@patch("requests.post")
def test_create_file_no_access_token(
    mock_post: MagicMock, create_client: CreateClient
) -> None:
    """Test create_file returns None if access_token is missing."""
    create_client.access_token = None
    file_id: Optional[str] = create_client.create_file(
        "drive123", "TestFolder", "TestFile.txt"
    )
    assert file_id is None
    assert create_client.access_token is None


@patch("requests.post")
def test_create_file_invalid_file_id(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """
    Test create_file prints an error and returns None when the created file ID is not a string.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201  # HTTP 201 Created
    mock_response.json.return_value = {"id": 12345}  # ID is an integer, not a string
    mock_post.return_value = mock_response

    file_id: Optional[str] = create_client.create_file(
        "drive123", "TestFolder", "TestFile.txt"
    )

    assert file_id is None
    captured = capsys.readouterr()
    assert "Error: Created file ID is not a string" in captured.out


## -----------------------------
## Tests for upload_file_to_folder
## -----------------------------
@patch("builtins.open", create=True)
@patch("requests.put")
def test_upload_file_to_folder_success(
    mock_put: MagicMock, mock_open: MagicMock, create_client: CreateClient
) -> None:
    """Test upload_file_to_folder returns valid file ID on success."""
    # Mock file reading
    mock_file = MagicMock()
    mock_file.read.return_value = b"file content"
    mock_open.return_value.__enter__.return_value = mock_file

    # Mock the PUT response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "uploaded-file-id"}
    mock_put.return_value = mock_response

    file_id: Optional[str] = create_client.upload_file_to_folder(
        "drive123", "folderABC", "upload.txt", "/path/to/upload.txt"
    )
    assert file_id == "uploaded-file-id"

    expected_url = create_client.format_graph_url(
        "drives", "drive123", "items", "folderABC:/upload.txt:/content"
    )
    mock_put.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/octet-stream",
        },
        data=b"file content",
    )


@patch("builtins.open", create=True)
@patch("requests.put")
def test_upload_file_to_folder_failure(
    mock_put: MagicMock,
    mock_open: MagicMock,
    create_client: CreateClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test upload_file_to_folder returns None and prints error on failure."""
    # Mock file reading
    mock_file = MagicMock()
    mock_file.read.return_value = b"file content"
    mock_open.return_value.__enter__.return_value = mock_file

    # Mock the PUT response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not Found"}
    mock_put.return_value = mock_response

    file_id: Optional[str] = create_client.upload_file_to_folder(
        "drive123", "folderABC", "fail.txt", "/path/to/fail.txt"
    )
    assert file_id is None

    captured = capsys.readouterr()
    assert "Error uploading file: 404" in captured.out
    assert "Not Found" in captured.out


@patch("requests.put")
def test_upload_file_to_folder_no_access_token(
    mock_put: MagicMock, create_client: CreateClient
) -> None:
    """Test upload_file_to_folder returns None if access_token is missing."""
    create_client.access_token = None

    file_id: Optional[str] = create_client.upload_file_to_folder(
        "drive123", "TestFolder", "TestFile.txt", "/path/to/TestFile.txt"
    )

    assert file_id is None
    mock_put.assert_not_called()


@patch("builtins.open", create=True)
@patch("requests.put")
def test_upload_file_to_folder_invalid_file_id(
    mock_put: MagicMock,
    mock_open: MagicMock,
    create_client: CreateClient,
    capsys: CaptureFixture[str],
) -> None:
    """Test upload_file_to_folder prints an error and returns None when the uploaded file ID is not a string."""

    mock_file = MagicMock()
    mock_file.read.return_value = b"file content"
    mock_open.return_value.__enter__.return_value = mock_file

    mock_response = MagicMock()
    mock_response.status_code = 201  # HTTP 201 Created
    mock_response.json.return_value = {"id": 12345}  # ID is an integer, not a string
    mock_put.return_value = mock_response

    file_id: Optional[str] = create_client.upload_file_to_folder(
        "drive123", "TestFolder", "TestFile.txt", "/path/to/TestFile.txt"
    )

    assert file_id is None

    captured = capsys.readouterr()
    assert "Error: Uploaded file ID is not a string" in captured.out


## -----------------------------
## Tests for create_list
## -----------------------------
@patch("requests.post")
def test_create_list_success(mock_post: MagicMock, create_client: CreateClient) -> None:
    """Test create_list returns the list ID on success."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "new-list-id"}
    mock_post.return_value = mock_response

    list_id: Optional[str] = create_client.create_list("site123", "MyList")
    assert list_id == "new-list-id"

    expected_url = create_client.format_graph_url("sites", "site123", "lists")
    mock_post.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        json={
            "displayName": "MyList",
            "list": {
                "template": "genericList",
            },
        },
    )


@patch("requests.post")
def test_create_list_failure(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """Test create_list returns None and prints error on failure."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {"error": "Forbidden"}
    mock_post.return_value = mock_response

    list_id: Optional[str] = create_client.create_list("site123", "MyFailList")
    assert list_id is None

    captured = capsys.readouterr()
    assert "Error creating list: 403" in captured.out
    assert "Forbidden" in captured.out


@patch("requests.post")
def test_create_list_no_access_token(
    mock_post: MagicMock, create_client: CreateClient
) -> None:
    "Test create list returns None if access_token is missing"
    create_client.access_token = None
    list_id: Optional[str] = create_client.create_list("site123", "MyList")
    assert list_id is None
    mock_post.assert_not_called()


@patch("requests.post")
def test_create_list_invalid_list_id(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """Test create_list prints an error and returns None when the created list ID is not a string."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 12345}
    mock_post.return_value = mock_response

    list_id: Optional[str] = create_client.create_list("site123", "MyList")
    assert list_id is None
    captured = capsys.readouterr()
    assert "Error: Created list ID is not a string" in captured.out


## -----------------------------
## Tests for create_document_library
## -----------------------------
@patch("requests.post")
def test_create_document_library_success(
    mock_post: MagicMock, create_client: CreateClient
) -> None:
    """Test create_document_library returns library ID on success."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "new-library-id"}
    mock_post.return_value = mock_response

    library_id: Optional[str] = create_client.create_document_library(
        "site123", "DocsLibrary"
    )
    assert library_id == "new-library-id"

    expected_url = create_client.format_graph_url("sites", "site123", "lists")
    mock_post.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        json={
            "displayName": "DocsLibrary",
            "list": {
                "template": "documentLibrary",
            },
        },
    )


@patch("requests.post")
def test_create_document_library_failure(
    mock_post: MagicMock, create_client: CreateClient, capsys: CaptureFixture[str]
) -> None:
    """Test create_document_library returns None and prints error on failure."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Server Error"}
    mock_post.return_value = mock_response

    library_id: Optional[str] = create_client.create_document_library(
        "site123", "BadLibrary"
    )
    assert library_id is None

    captured = capsys.readouterr()
    assert "Error creating document library: 500" in captured.out
    assert "Server Error" in captured.out
