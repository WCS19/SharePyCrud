#  _________.__                        __________        _________                  .___
# /   _____/|  |__ _____ _______   ____\______   \___.__.\_   ___ \_______ __ __  __| _/
# \_____  \ |  |  \\__  \\_  __ \_/ __ \|     ___<   |  |/    \  \/\_  __ \  |  \/ __ |
# /        \|   Y  \/ __ \|  | \/\  ___/|    |    \___  |\     \____|  | \/  |  / /_/ |
# /_______  /|___|  (____  /__|    \___  >____|    / ____| \______  /|__|  |____/\____ |
#         \/      \/     \/            \/          \/             \/                  \/

"""SharePyCrud: A Python library for SharePoint CRUD operations."""

__version__ = "0.1.2"

from .auth import SharePointAuth
from .config import SharePointConfig
from .client import SharePointClient
from .utils import make_graph_request, format_graph_url

__all__ = [
    "SharePointAuth",
    "SharePointConfig",
    "SharePointClient",
    "make_graph_request",
    "format_graph_url",
    "setup_client",
]
