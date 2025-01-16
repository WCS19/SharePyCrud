import pytest
from unittest.mock import MagicMock, patch
from sharepycrud.createClient import CreateClient
from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Any, List, Dict, Optional
import requests
import logging
import sys
from pathlib import Path


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
def create_client(mock_base_client: BaseClient) -> CreateClient:
    """CreateClient initialized with a mocked BaseClient."""
    return CreateClient(mock_base_client)


def test_make_graph_request(create_client: CreateClient) -> None:
    """Test delegating make_graph_request to BaseClient."""
    with patch.object(
        create_client.client, "make_graph_request", return_value={"key": "value"}
    ) as mock_method:
        result = create_client.make_graph_request(
            "https://mock-url.com", "POST", {"data": "test"}
        )
        mock_method.assert_called_once_with(
            "https://mock-url.com", "POST", {"data": "test"}
        )
        assert result == {"key": "value"}


def test_format_graph_url(create_client: CreateClient) -> None:
    """Test delegating format_graph_url to BaseClient."""
    with patch.object(
        create_client.client, "format_graph_url", return_value="https://mocked-url.com"
    ) as mock_method:
        result = create_client.format_graph_url("sites", "mock-site")
        mock_method.assert_called_once_with("sites", "mock-site")
        assert result == "https://mocked-url.com"


def test_parse_folder_path(create_client: CreateClient) -> None:
    """Test delegating parse_folder_path to BaseClient."""
    with patch.object(
        create_client.client, "parse_folder_path", return_value=["Folder1", "Folder2"]
    ) as mock_method:
        result = create_client.parse_folder_path("/Folder1/Folder2/")
        mock_method.assert_called_once_with("/Folder1/Folder2/")
        assert result == ["Folder1", "Folder2"]


def test_create_folder_success(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful folder creation."""
    mock_base_client.make_graph_request.return_value = {
        "id": "folder123",
        "name": "TestFolder",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    folder_id = create_client.create_folder("drive123", "TestFolder")

    assert folder_id == "folder123"
    assert "Creating folder: TestFolder" in caplog.text
    assert "Successfully created folder: TestFolder" in caplog.text


def test_create_folder_no_access_token(
    create_client: CreateClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    folder_id = create_client.create_folder("drive123", "TestFolder")

    assert folder_id is None


def test_create_folder_no_response(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    folder_id = create_client.create_folder("drive123", "TestFolder")

    assert folder_id is None
    assert "Creating folder: TestFolder" in caplog.text
    assert "Failed to create folder: TestFolder" in caplog.text


def test_create_folder_invalid_id(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when folder ID is not a string."""
    mock_base_client.make_graph_request.return_value = {
        "id": 123,  # Invalid ID type
        "name": "TestFolder",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    folder_id = create_client.create_folder("drive123", "TestFolder")

    assert folder_id is None
    assert "Creating folder: TestFolder" in caplog.text
    assert "Failed to create folder: TestFolder" in caplog.text


def test_create_file_success(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful file creation."""
    mock_base_client.make_graph_request.return_value = {
        "id": "file123",
        "name": "test.txt",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.create_file("drive123", "folder123", "test.txt")

    assert file_id == "file123"
    assert "Creating file: test.txt" in caplog.text
    assert "Successfully created file: test.txt" in caplog.text


def test_create_file_no_access_token(
    create_client: CreateClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    file_id = create_client.create_file("drive123", "folder123", "test.txt")

    assert file_id is None


def test_create_file_no_response(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.create_file("drive123", "folder123", "test.txt")

    assert file_id is None
    assert "Creating file: test.txt" in caplog.text
    assert "Failed to create file: test.txt" in caplog.text


def test_create_file_invalid_id(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when file ID is not a string."""
    mock_base_client.make_graph_request.return_value = {
        "id": 123,  # Invalid ID type
        "name": "test.txt",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.create_file("drive123", "folder123", "test.txt")

    assert file_id is None
    assert "Creating file: test.txt" in caplog.text
    assert "Failed to create file: test.txt" in caplog.text


def test_upload_file_success(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test successful file upload."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    mock_base_client.make_graph_request.return_value = {
        "id": "file123",
        "name": "test.txt",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.upload_file_to_folder(
        "drive123", "folder123", "test.txt", str(test_file)
    )

    assert file_id == "file123"
    assert "Uploading file: test.txt" in caplog.text
    assert "Successfully uploaded file: test.txt" in caplog.text


def test_upload_file_no_access_token(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    tmp_path: Path,
) -> None:
    """Test when access token is missing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    mock_base_client.access_token = None

    file_id = create_client.upload_file_to_folder(
        "drive123", "folder123", "test.txt", str(test_file)
    )

    assert file_id is None


def test_upload_file_not_found(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when file is not found."""
    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.upload_file_to_folder(
        "drive123", "folder123", "test.txt", "nonexistent.txt"
    )

    assert file_id is None
    assert "Uploading file: test.txt" in caplog.text
    assert "File not found: test.txt" in caplog.text


def test_upload_file_no_response(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test when make_graph_request returns None."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.upload_file_to_folder(
        "drive123", "folder123", "test.txt", str(test_file)
    )

    assert file_id is None
    assert "Uploading file: test.txt" in caplog.text
    assert "Failed to upload file: test.txt" in caplog.text


def test_upload_file_invalid_id(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test when file ID is not a string."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    mock_base_client.make_graph_request.return_value = {
        "id": 123,  # Invalid ID type
        "name": "test.txt",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    file_id = create_client.upload_file_to_folder(
        "drive123", "folder123", "test.txt", str(test_file)
    )

    assert file_id is None
    assert "Uploading file: test.txt" in caplog.text
    assert "Failed to upload file: test.txt" in caplog.text


def test_create_list_success(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful list creation."""
    mock_base_client.make_graph_request.return_value = {
        "id": "list123",
        "displayName": "TestList",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    list_id = create_client.create_list("site123", "TestList")

    assert list_id == "list123"
    assert "Creating list: TestList" in caplog.text
    assert "Successfully created list: TestList" in caplog.text


def test_create_list_no_access_token(
    create_client: CreateClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    list_id = create_client.create_list("site123", "TestList")

    assert list_id is None


def test_create_list_no_response(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when make_graph_request returns None."""
    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    list_id = create_client.create_list("site123", "TestList")

    assert list_id is None
    assert "Creating list: TestList" in caplog.text
    assert "Failed to create list: TestList" in caplog.text


def test_create_list_invalid_id(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when list ID is not a string."""
    mock_base_client.make_graph_request.return_value = {
        "id": 123,  # Invalid ID type
        "displayName": "TestList",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    list_id = create_client.create_list("site123", "TestList")

    assert list_id is None
    assert "Creating list: TestList" in caplog.text
    assert "Failed to create list: TestList" in caplog.text


def test_create_list_custom_template(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test list creation with custom template."""
    mock_base_client.make_graph_request.return_value = {
        "id": "list123",
        "displayName": "TestList",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    list_id = create_client.create_list("site123", "TestList", "customTemplate")

    assert list_id == "list123"
    assert "Creating list: TestList" in caplog.text
    assert "Successfully created list: TestList" in caplog.text


def test_create_document_library_success(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful document library creation."""
    mock_base_client.make_graph_request.return_value = {
        "id": "lib123",
        "displayName": "TestLibrary",
    }

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    library_id = create_client.create_document_library("site123", "TestLibrary")

    assert library_id == "lib123"
    assert "Creating document library: TestLibrary" in caplog.text
    assert "Successfully created document library: TestLibrary" in caplog.text


def test_create_document_library_no_access_token(
    create_client: CreateClient,
    mock_base_client: MagicMock,
) -> None:
    """Test when access token is missing."""
    mock_base_client.access_token = None

    library_id = create_client.create_document_library("site123", "TestLibrary")

    assert library_id is None


def test_create_document_library_creation_failed(
    create_client: CreateClient,
    mock_base_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when document library creation fails."""
    mock_base_client.make_graph_request.return_value = None

    caplog.set_level(logging.INFO, logger="sharepycrud.createClient")

    library_id = create_client.create_document_library("site123", "TestLibrary")

    assert library_id is None
    assert "Creating document library: TestLibrary" in caplog.text
    assert "Failed to create document library: TestLibrary" in caplog.text
