from typing import Optional, Dict, Any, List
from sharepycrud.baseClient import BaseClient
from sharepycrud.logger import get_logger

logger = get_logger("sharepycrud.deleteClient")


class DeleteClient:
    def __init__(self, base_client: BaseClient):
        self.client = base_client

    ### Delegate methods to BaseClient
    def make_graph_request(
        self, url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delegate make_graph_request to BaseClient.

        Args:
            url: URL of the API request.
            method: HTTP method to use (default is GET).
            data: Data to send with the request (optional).

        Returns:
            The response from the API request as a dictionary.

        Raises:
            ValueError: If access token is missing or invalid.
            requests.exceptions.RequestException: For any request-related errors.
        """
        return self.client.make_graph_request(url, method, data)

    def format_graph_url(self, base_path: str, *args: str) -> str:
        """
        Delegate format_graph_url to BaseClient.

        Args:
            base_path: Base path of the API request.
            args: Additional path components to append to the base path.

        Returns:
            The formatted URL.
        """
        return self.client.format_graph_url(base_path, *args)

    def parse_folder_path(self, folder_path: str) -> List[str]:
        """
        Delegate parse_folder_path to BaseClient.

        Args:
            folder_path: Full path of the nested folder structure (e.g., "Folder1/FolderNest1/FolderNest2").

        Returns:
            A list of folder names in the path.
        """
        return self.client.parse_folder_path(folder_path)
