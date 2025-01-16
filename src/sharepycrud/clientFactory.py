from threading import Lock
from typing import Optional
from sharepycrud.baseClient import BaseClient
from sharepycrud.readClient import ReadClient
from sharepycrud.createClient import CreateClient
from sharepycrud.config import SharePointConfig
import logging

logger = logging.getLogger(__name__)


class ClientFactory:
    _base_client: Optional[BaseClient] = None
    _lock = Lock()

    @classmethod
    def get_base_client(cls, config: SharePointConfig) -> BaseClient:
        """
        Get or create the singleton BaseClient instance.
        """
        if cls._base_client is None:
            with cls._lock:
                if cls._base_client is None:  # Double-checked locking
                    try:
                        cls._base_client = BaseClient(config)
                    except Exception as e:
                        logger.error("Failed to create BaseClient: %s", str(e))
                        raise  # Re-raise the exception for proper handling
        return cls._base_client

    @classmethod
    def create_read_client(cls, config: SharePointConfig) -> ReadClient:
        """
        Create a ReadClient instance using the shared BaseClient.
        """
        base_client = cls.get_base_client(config)
        return ReadClient(base_client)

    @classmethod
    def create_write_client(cls, config: SharePointConfig) -> CreateClient:
        """
        Create a CreateClient instance using the shared BaseClient.
        """
        base_client = cls.get_base_client(config)
        return CreateClient(base_client)

    @classmethod
    def reset_base_client(cls) -> None:
        """
        Reset the singleton BaseClient instance. Call this if the configuration changes.
        """
        with cls._lock:
            cls._base_client = None
