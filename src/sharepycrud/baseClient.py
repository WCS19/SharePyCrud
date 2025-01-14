from typing import Dict, Any, Optional, cast, List
import requests
from urllib.parse import quote
from .config import SharePointConfig


class BaseClient:
    def __init__(self, config: SharePointConfig):
        """
        Initialize BaseClient with configuration.
        Automatically fetches an access token during initialization.
        """
        self.config = config
        self.access_token = self._get_access_token()
        if not self.access_token:
            raise ValueError("Failed to obtain access token")

    # Using a direct requests.post call rather than self.make_graph_request
    # to avoid bootstrapping issue with self.make_graph_request.
    def _get_access_token(self) -> Optional[str]:
        """
        Retrieve an access token using Azure AD client credentials flow.
        """
        url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }

        try:
            # Make a direct requests.post call without depending on self.access_token
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()
            token = cast(Optional[str], response.json().get("access_token"))
            return token
        except requests.exceptions.RequestException as e:
            return None

    def make_graph_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generic function to make Microsoft Graph API requests.

        Args:
            url: URL of the API request.
            method: HTTP method to use (default is GET).
            data: Data to send with the request (optional).

        Returns:
            The response from the API request as a dictionary, or an empty dictionary if the request fails.
        """

        if not self.access_token:
            raise ValueError("Access token is missing or invalid")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        if method == "POST" and "oauth2/v2.0/token" in url:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = requests.post(url, headers=headers, data=data)
        else:
            response = requests.request(method, url, headers=headers, json=data)

        response.raise_for_status()  # Raise an exception for HTTP errors

        return cast(Dict[str, Any], response.json())

    def format_graph_url(self, base_path: str, *args: str) -> str:
        """Format Microsoft Graph API URL with proper encoding
        Args:
            base_path: Base path of the API request.
            args: Additional path components to append to the base path.
        Returns:
            The formatted URL.
        """
        encoded_args = [quote(str(arg), safe="") for arg in args]
        if not args:
            return f"https://graph.microsoft.com/v1.0/{base_path}"
        return f"https://graph.microsoft.com/v1.0/{base_path}/{'/'.join(encoded_args)}"

    def parse_folder_path(self, folder_path: str) -> List[str]:
        """
        Parse a nested folder path into its components.
        Args:
            folder_path: Full path of the nested folder structure within a drive.(e.g., "Folder1/FolderNest1/FolderNest2").
        Returns:
            A list of folder names in the path (e.g., ["Folder1", "FolderNest1", "FolderNest2"]).
        """
        return folder_path.strip("/").split("/")
