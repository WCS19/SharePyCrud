import pytest
from sharepycrud.config import SharePointConfig
import os
from unittest.mock import patch


@pytest.fixture
def config() -> SharePointConfig:
    """Create a SharePointConfig instance with test values"""
    return SharePointConfig(
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
        sharepoint_url="https://test.sharepoint.com",
    )


def test_config_initialization(config: SharePointConfig) -> None:
    """Test SharePointConfig initialization with all fields"""
    assert config.tenant_id == "test-tenant"
    assert config.client_id == "test-client"
    assert config.client_secret == "test-secret"
    assert config.sharepoint_url == "https://test.sharepoint.com"
    assert config.resource_url == "https://graph.microsoft.com/"


def test_config_validation_success(config: SharePointConfig) -> None:
    """Test validation with all required fields"""
    is_valid, missing_fields = config.validate()
    assert is_valid is True
    assert len(missing_fields) == 0


def test_config_validation_failure() -> None:
    """Test validation with missing fields"""
    config = SharePointConfig(
        tenant_id="", client_id="test-client", client_secret="", sharepoint_url=""
    )
    is_valid, missing_fields = config.validate()
    assert is_valid is False
    assert set(missing_fields) == {"TENANT_ID", "CLIENT_SECRET", "SHAREPOINT_URL"}


def test_config_from_env() -> None:
    """Test creating config from environment variables"""
    env_vars = {
        "TENANT_ID": "env-tenant",
        "CLIENT_ID": "env-client",
        "CLIENT_SECRET": "env-secret",
        "SHAREPOINT_URL": "https://env.sharepoint.com",
    }

    with (
        patch.dict(os.environ, env_vars),
        patch("sharepycrud.config.load_dotenv"),
    ):  # Mock load_dotenv
        config = SharePointConfig.from_env()

        assert config.tenant_id == "env-tenant"
        assert config.client_id == "env-client"
        assert config.client_secret == "env-secret"
        assert config.sharepoint_url == "https://env.sharepoint.com"


def test_config_from_env_missing_vars() -> None:
    """Test creating config from environment with missing variables"""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("sharepycrud.config.load_dotenv"),
    ):  # Mock load_dotenv
        config = SharePointConfig.from_env()

        assert config.tenant_id == ""
        assert config.client_id == ""
        assert config.client_secret == ""
        assert config.sharepoint_url == ""

        is_valid, missing_fields = config.validate()
        assert is_valid is False
        assert set(missing_fields) == {
            "TENANT_ID",
            "CLIENT_ID",
            "CLIENT_SECRET",
            "SHAREPOINT_URL",
        }
