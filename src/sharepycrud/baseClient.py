from typing import Dict, Any, Optional, cast, List, Union
import requests
from urllib.parse import quote
from sharepycrud.config import SharePointConfig
from sharepycrud.logger import get_logger

logger = get_logger("sharepycrud.baseClient")


class BaseClient:
    def __init__(self, config: SharePointConfig):
        """
        Initialize BaseClient with configuration.
        Automatically fetches an access token during initialization.
        """
        self.config = config
        self.access_token = self._get_access_token()
        if not self.access_token:
            logger.error("Failed to obtain access token during initialization")
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

            if token:
                logger.debug("Successfully obtained access token")
                return token

            logger.error("No access token in response")
            raise ValueError("Failed to obtain access token")

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error getting access token: {e.response.status_code} - {e.response.reason}"
            )
            logger.debug(f"Response content: {e.response.text}")
            raise ValueError("Failed to obtain access token")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise ValueError("Failed to obtain access token")

    def make_graph_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Union[Dict[str, Any], bytes]] = None,  # Allow Dict or bytes
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generic function to make Microsoft Graph API requests.

        Args:
            url: URL of the API request.
            method: HTTP method to use (default is GET).
            data: Data to send with the request (can be dict or bytes).
            headers: Optional headers to include in the request.

        Returns:
            The response from the API request as a dictionary.

        Raises:
            ValueError: If access token is missing or invalid
            requests.exceptions.RequestException: For any request-related errors
        """
        if not self.access_token:
            logger.error("Access token is missing or invalid")
            raise ValueError("Access token is missing or invalid")

        default_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        if headers:
            default_headers.update(headers)

        try:
            logger.debug(f"Making {method} request to {url}")
            response = requests.request(
                method,
                url,
                headers=default_headers,
                json=data if isinstance(data, dict) else None,
                data=data if isinstance(data, bytes) else None,
            )
            response.raise_for_status()

            # For non-JSON responses, just return an empty dict
            if not response.headers.get("Content-Type", "").startswith(
                "application/json"
            ):
                return {}

            result = cast(Dict[str, Any], response.json())
            logger.debug(f"Request successful: {method} {url}")
            return result

        except requests.exceptions.HTTPError as e:
            if e.response:
                logger.error(
                    f"HTTP error in request: {e.response.status_code} - {e.response.reason}"
                )
                logger.debug(f"Response content: {e.response.text}")
            else:
                logger.error(f"HTTP error occurred without a response: {str(e)}")
            logger.debug(f"Failed URL: {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.debug(f"Failed URL: {url}")
            raise

    def format_graph_url(self, base_path: str, *args: str) -> str:
        """
        Format Microsoft Graph API URL with proper encoding.

        Args:
            base_path: Base path of the API request.
            args: Additional path components to append to the base path.

        Returns:
            The formatted URL.
        """
        try:
            encoded_args = [quote(str(arg), safe="") for arg in args]
            if not args:
                url = f"https://graph.microsoft.com/v1.0/{base_path}"
            else:
                url = f"https://graph.microsoft.com/v1.0/{base_path}/{'/'.join(encoded_args)}"

            logger.debug(f"Formatted Graph API URL: {url}")
            return url

        except Exception as e:
            logger.error(f"Error formatting Graph API URL: {str(e)}")
            logger.debug(f"base_path: {base_path}, args: {args}")
            raise

    def parse_folder_path(self, folder_path: str) -> List[str]:
        """
        Parse a nested folder path into its components.

        Args:
            folder_path: Full path of the nested folder structure (e.g., "Folder1/FolderNest1/FolderNest2").

        Returns:
            A list of folder names in the path.
        """
        try:
            components = folder_path.strip("/").split("/")
            logger.debug(f"Parsed folder path '{folder_path}' into: {components}")
            return components

        except Exception as e:
            logger.error(f"Error parsing folder path: {str(e)}")
            logger.debug(f"Input folder_path: {folder_path}")
            raise
