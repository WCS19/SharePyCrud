#  _________.__                        __________        _________                  .___
# /   _____/|  |__ _____ _______   ____\______   \___.__.\_   ___ \_______ __ __  __| _/
# \_____  \ |  |  \\__  \\_  __ \_/ __ \|     ___<   |  |/    \  \/\_  __ \  |  \/ __ |
# /        \|   Y  \/ __ \|  | \/\  ___/|    |    \___  |\     \____|  | \/  |  / /_/ |
# /_______  /|___|  (____  /__|    \___  >____|    / ____| \______  /|__|  |____/\____ |
#         \/      \/     \/            \/          \/             \/                  \/

"""SharePyCrud: A Python library for SharePoint CRUD operations."""

__version__ = "0.2.0.dev1"

from .auth import SharePointAuth
from .config import SharePointConfig
from .baseClient import BaseClient
from .createClient import CreateClient
from .readClient import ReadClient

__all__ = [
    "SharePointAuth",
    "SharePointConfig",
    "BaseClient",
    "CreateClient",
    "ReadClient",
    "SharePointClient",
]
