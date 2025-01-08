from typing import Dict, List, Optional, Union, cast, TYPE_CHECKING, Any
import requests
from urllib.parse import quote
from .config import SharePointConfig

# Used for type hints only, prevents circular imports
if TYPE_CHECKING:
    from .client import SharePointClient


def setup_client() -> Optional["SharePointClient"]:
    """Initialize SharePoint client with configuration"""
    config = SharePointConfig.from_env()
    is_valid, missing_fields = config.validate()

    if not is_valid:
        print("Error: Missing required environment variables.")
        for field in missing_fields:
            print(f"{field}: {'Set' if getattr(config, field) else 'Missing'}")
        return None

    # Import here to avoid circular import
    from .client import SharePointClient

    return SharePointClient(config)


def make_graph_request(
    url: str,
    access_token: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generic function to make Microsoft Graph API requests"""
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    # Special handling for token request
    if method == "POST" and "oauth2/v2.0/token" in url:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, headers=headers, data=data)
    else:
        response = requests.request(method, url, headers=headers, json=data)

    response_json = cast(Dict[str, Any], response.json())

    # 200 is OK, 201 is created
    if response.status_code not in [200, 201]:
        print(f"Error making request to {url}. Status code: {response.status_code}")
        print("Response:", response_json)
        return {}

    return response_json


def format_graph_url(base_path: str, *args: str) -> str:
    """Format Microsoft Graph API URL with proper encoding"""
    encoded_args = [quote(str(arg), safe="") for arg in args]
    if not args:
        return f"https://graph.microsoft.com/v1.0/{base_path}"
    return f"https://graph.microsoft.com/v1.0/{base_path}/{'/'.join(encoded_args)}"
