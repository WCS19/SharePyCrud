#  _________.__                        __________        _________                  .___
# /   _____/|  |__ _____ _______   ____\______   \___.__.\_   ___ \_______ __ __  __| _/
# \_____  \ |  |  \\__  \\_  __ \_/ __ \|     ___<   |  |/    \  \/\_  __ \  |  \/ __ |
# /        \|   Y  \/ __ \|  | \/\  ___/|    |    \___  |\     \____|  | \/  |  / /_/ |
# /_______  /|___|  (____  /__|    \___  >____|    / ____| \______  /|__|  |____/\____ |
#         \/      \/     \/            \/          \/             \/                  \/

"""SharePyCrud: A Python library for SharePoint CRUD operations."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(
        "sharepycrud"
    )  # dynamically fetch version from pyproject.toml
except PackageNotFoundError:
    __version__ = "0.0.0"


from .config import SharePointConfig
from .clientFactory import ClientFactory
from .baseClient import BaseClient
from .createClient import CreateClient
from .readClient import ReadClient
from .logger import setup_logging, get_logger
from .loggerConfig import LogConfig

__all__ = [
    "SharePointConfig",
    "ClientFactory",
    "BaseClient",
    "CreateClient",
    "ReadClient",
    "setup_logging",
    "get_logger",
    "LogConfig",
]
