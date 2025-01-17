import pytest
from unittest.mock import patch, MagicMock
from typing import Any, List, Tuple
import os
from sharepycrud.config import SharePointConfig
from sharepycrud.logger import get_logger

logger = get_logger("sharepycrud.config")


@pytest.fixture
def valid_config() -> SharePointConfig:
    """
    Returns a valid SharePointConfig instance for testing.
    """
    return SharePointConfig(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


def test_validate_success(valid_config: SharePointConfig, caplog: Any) -> None:
    """
    Test that validate returns True when all fields are provided.
    """
    caplog.set_level("DEBUG", logger="sharepycrud.config")
    is_valid, missing_fields = valid_config.validate()
    assert is_valid, "Expected validation to succeed."
    assert missing_fields == [], "Expected no missing fields."
    assert "Configuration validated successfully" in caplog.text


def test_validate_missing_fields(caplog: Any) -> None:
    """
    Test that validate raises ValueError and logs missing fields when some fields are missing.
    """
    caplog.set_level("DEBUG", logger="sharepycrud.config")

    config = SharePointConfig(
        tenant_id="",
        client_id="test-client-id",
        client_secret="",
        sharepoint_url="https://test.sharepoint.com",
    )

    with pytest.raises(
        ValueError,
        match="Configuration validation failed. Missing fields: TENANT_ID, CLIENT_SECRET",
    ):
        config.validate()

    assert (
        "Configuration validation failed. Missing fields: TENANT_ID, CLIENT_SECRET"
        in caplog.text
    )


def test_from_env(monkeypatch: Any) -> None:
    """
    Test that from_env correctly loads configuration from environment variables.
    """
    monkeypatch.setenv("TENANT_ID", "test-tenant-id")
    monkeypatch.setenv("CLIENT_ID", "test-client-id")
    monkeypatch.setenv("CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("SHAREPOINT_URL", "https://test.sharepoint.com")

    config = SharePointConfig.from_env()

    assert config.tenant_id == "test-tenant-id"
    assert config.client_id == "test-client-id"
    assert config.client_secret == "test-client-secret"
    assert config.sharepoint_url == "https://test.sharepoint.com"


def test_from_env_missing_fields(monkeypatch: Any) -> None:
    """
    Test that from_env returns empty strings for missing environment variables.
    """
    # Mock os.getenv to always return None for all environment variable lookups
    with patch("os.getenv", side_effect=lambda key, default="": default):
        config = SharePointConfig.from_env()

    assert config.tenant_id == ""
    assert config.client_id == ""
    assert config.client_secret == ""
    assert config.sharepoint_url == ""


def test_validate_logging_for_missing_fields(caplog: Any) -> None:
    """
    Test that validate logs missing fields at DEBUG level when validation fails.
    """
    caplog.set_level("DEBUG", logger="sharepycrud.config")

    config = SharePointConfig(
        tenant_id="",
        client_id="",
        client_secret="",
        sharepoint_url="",
    )

    with pytest.raises(ValueError):
        config.validate()

    assert (
        "Configuration validation failed. Missing fields: TENANT_ID, CLIENT_ID, CLIENT_SECRET, SHAREPOINT_URL"
        in caplog.text
    )
