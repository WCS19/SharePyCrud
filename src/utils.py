from typing import Dict, List, Optional, Union, cast
import requests
from urllib.parse import quote
from typing import Any, Dict, List, Optional, Union


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

    if response.status_code != 200:
        print(f"Error making request to {url}. Status code: {response.status_code}")
        print("Response:", response_json)
        return {}

    return response_json


def format_graph_url(base_path: str, *args: str) -> str:
    """Format Microsoft Graph API URL with proper encoding"""
    encoded_args = [quote(str(arg)) for arg in args]
    return f"https://graph.microsoft.com/v1.0/{base_path}/{'/'.join(encoded_args)}"
