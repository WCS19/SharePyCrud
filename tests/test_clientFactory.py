import pytest
from unittest.mock import patch, MagicMock
from typing import Any, Generator
import logging

from sharepycrud.clientFactory import ClientFactory
from sharepycrud.baseClient import BaseClient
from sharepycrud.readClient import ReadClient
from sharepycrud.createClient import CreateClient
from sharepycrud.config import SharePointConfig


@pytest.fixture
def mock_config() -> SharePointConfig:
    """Provides a SharePointConfig fixture for testing."""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


def test_get_base_client_singleton(mock_config: SharePointConfig) -> None:
    """
    Test that get_base_client returns the same BaseClient instance (singleton).
    """
    # Reset any existing singleton
    ClientFactory.reset_base_client()

    with patch.object(BaseClient, "__init__", return_value=None) as mock_init:
        # Force BaseClient to not do any real init logic
        instance1 = ClientFactory.get_base_client(mock_config)
        instance2 = ClientFactory.get_base_client(mock_config)

    # __init__ should have been called only once
    assert mock_init.call_count == 1, "BaseClient.__init__ called more than once"
    assert instance1 is instance2, "Multiple BaseClient instances returned"


def test_get_base_client_error(mock_config: SharePointConfig, caplog: Any) -> None:
    """
    Test that get_base_client logs an error and re-raises if BaseClient creation fails.
    """
    ClientFactory.reset_base_client()

    caplog.set_level(logging.ERROR, logger="sharepycrud.clientFactory")

    with patch.object(
        BaseClient, "__init__", side_effect=Exception("Initialization error")
    ):
        with pytest.raises(Exception, match="Initialization error"):
            ClientFactory.get_base_client(mock_config)
    assert "Failed to create BaseClient: Initialization error" in caplog.text


def test_create_read_client(mock_config: SharePointConfig) -> None:
    """
    Test that create_read_client creates a ReadClient using the shared BaseClient.
    """
    ClientFactory.reset_base_client()

    with patch.object(BaseClient, "__init__", return_value=None):
        read_client: ReadClient = ClientFactory.create_read_client(mock_config)

        assert isinstance(read_client, ReadClient), "Expected a ReadClient instance"
        # Since ReadClient uses self.client to store the base client:
        assert isinstance(read_client.client, BaseClient)


def test_create_write_client(mock_config: SharePointConfig) -> None:
    """
    Test that create_write_client creates a CreateClient using the shared BaseClient.
    """
    ClientFactory.reset_base_client()

    with patch.object(BaseClient, "__init__", return_value=None):
        write_client: CreateClient = ClientFactory.create_write_client(mock_config)

        assert isinstance(
            write_client, CreateClient
        ), "Expected a CreateClient instance"
        # Since CreateClient uses self.client to store the base client:
        assert isinstance(write_client.client, BaseClient)


def test_reset_base_client(mock_config: SharePointConfig) -> None:
    """
    Test that reset_base_client sets the singleton BaseClient to None.
    """
    ClientFactory.reset_base_client()
    with patch.object(BaseClient, "__init__", return_value=None):
        instance_before_reset = ClientFactory.get_base_client(mock_config)
        assert instance_before_reset is not None

    ClientFactory.reset_base_client()
    with patch.object(BaseClient, "__init__", return_value=None) as mock_init:
        instance_after_reset = ClientFactory.get_base_client(mock_config)
        assert instance_after_reset is not None
        assert (
            mock_init.call_count == 1
        ), "Expected BaseClient init to be called after reset"
