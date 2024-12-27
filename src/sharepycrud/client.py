from typing import Dict, List, Optional, Tuple, Any
import os
from .utils import make_graph_request, format_graph_url
from .config import SharePointConfig
from requests import Response
import requests


class SharePointClient:
    def __init__(self, config: SharePointConfig):
        """Initialize SharePoint client with configuration"""
        self.config = config
        self.access_token = self._get_access_token()
        if not self.access_token:
            raise ValueError("Failed to obtain access token")

    def _get_access_token(self) -> Optional[str]:
        """Get access token from Azure AD"""
        url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }

        response = make_graph_request(url, "", method="POST", data=body)
        return response.get("access_token") if response else None

    ##################################################################################
    # Read Logic
    ##################################################################################
    def list_sites(self) -> Optional[List[Optional[str]]]:
        """List all sites

        Returns:
            Optional[List[Optional[str]]]: List of site names, or None if request fails.
            Individual site names can be None if they don't have a name.
        """
        if not self.access_token:
            return None
        url = format_graph_url("sites")
        response = make_graph_request(url, self.access_token)

        # Extract site names, allowing for None values
        site_names = (
            [site.get("name") for site in response.get("value", [])]
            if response
            else None
        )
        return site_names

    def get_site_id(
        self, sharepoint_url: Optional[str] = None, site_name: Optional[str] = None
    ) -> Optional[str]:
        """Get site ID from SharePoint URL"""
        if not self.access_token:
            return None
        base_url = sharepoint_url or self.config.sharepoint_url
        site = site_name

        url = format_graph_url(f"sites/{base_url}:/sites/{site}")
        response = make_graph_request(url, self.access_token)

        return response.get("id") if response else None

    def list_drives(self, site_id: str) -> Optional[Dict[str, Any]]:
        """List all drives and their root contents"""
        if not self.access_token:
            return None
        url = format_graph_url("sites", site_id, "drives")
        response = make_graph_request(url, self.access_token)

        if response and "value" in response:
            print("=== Drives ===:")
            for drive in response["value"]:
                print(f"\nDrive: {drive['name']}, ID: {drive['id']}")

                # Get root folder contents
                root_url = format_graph_url("drives", drive["id"], "root", "children")
                root_contents = make_graph_request(root_url, self.access_token)

                if root_contents and "value" in root_contents:
                    print("Root contents:")
                    for item in root_contents["value"]:
                        item_type = "folder" if "folder" in item else "file"
                        print(f"- {item['name']} ({item_type})")
                else:
                    print("No items in root folder")

            return response
        return None

    def get_drive_id(self, site_id: str, drive_name: str) -> Optional[str]:
        """Get drive ID by its name"""
        if not self.access_token:
            return None
        url = format_graph_url("sites", site_id, "drives")
        response = make_graph_request(url, self.access_token)

        # Check if response exists and has a 'value' key
        if not response or "value" not in response:
            return None

        # Type hint for the drives list
        drives: List[Dict[str, Any]] = response["value"]

        # Look for matching drive name
        for drive in drives:
            if isinstance(drive, dict) and drive.get("name") == drive_name:
                drive_id = drive.get("id")
                if isinstance(drive_id, str):
                    return drive_id

        return None

    def list_drive_ids(self, site_id: str) -> List[Tuple[str, str]]:
        """Get all drive IDs and names for a site"""
        if not self.access_token:
            return []
        url = format_graph_url("sites", site_id, "drives")
        response = make_graph_request(url, self.access_token)
        drives = response.get("value", []) if response else []
        return [(drive["id"], drive["name"]) for drive in drives]

    def list_all_folders(
        self, drive_id: str, parent_path: str = "root", level: int = 0
    ) -> List[Dict[str, Any]]:
        """Recursively list all folders within a drive"""
        if not self.access_token:
            return []

        url = format_graph_url("drives", drive_id, "items", parent_path, "children")
        response = make_graph_request(url, self.access_token)

        folders: List[Dict[str, Any]] = []
        if not response or "value" not in response:
            return folders

        for item in response["value"]:
            if "folder" in item:
                folder_name = item["name"]
                folder_id = item["id"]
                folder_path = item["parentReference"]["path"] + f"/{folder_name}"

                print(f"{'  ' * level}- Folder: {folder_name} (ID: {folder_id})")
                folders.append(
                    {"name": folder_name, "id": folder_id, "path": folder_path}
                )

                subfolders = self.list_all_folders(drive_id, folder_id, level + 1)
                folders.extend(subfolders)

        return folders

    def get_folder_content(
        self, drive_id: str, folder_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get contents of a folder using its ID"""
        if not self.access_token:
            return None

        url = format_graph_url("drives", drive_id, "items", folder_id, "children")
        print(f"Requesting folder contents from: {url}")  # Debug print

        response = make_graph_request(url, self.access_token)

        if not response:
            return None

        folder_contents: List[Dict[str, Any]] = []
        for item in response.get("value", []):
            folder_contents.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "type": "folder" if "folder" in item else "file",
                    "webUrl": item.get("webUrl"),
                    "size": item.get("size", "N/A"),
                }
            )

        print(f"Found {len(folder_contents)} items in folder")  # Debug print
        return folder_contents

    def download_file(
        self,
        file_path: str,
        site_name: Optional[str] = None,
        drive_name: Optional[str] = None,
    ) -> Optional[bytes]:
        """Download a file from SharePoint

        Args:
            file_path: Path to the file in SharePoint
            site_name: Optional name of the SharePoint site
            drive_name: Optional name of the drive containing the file

        Returns:
            File content as bytes if successful, None otherwise
        """
        if not self.access_token:
            print("No access token available")
            return None

        # Get site ID
        site_id = self.get_site_id(site_name=site_name)
        if not site_id:
            print("Failed to get site ID")
            return None

        # Get drive ID
        drive_id = self.get_drive_id(site_id, drive_name) if drive_name else None
        if not drive_id:
            print(f"Drive '{drive_name}' not found")
            return None

        # Download file - using items endpoint
        url = format_graph_url("drives", drive_id, "root/children")

        # First, get the file ID
        list_response = make_graph_request(url, self.access_token)
        if not list_response or "value" not in list_response:
            print("Failed to list drive contents")
            return None

        file_id = None
        for item in list_response["value"]:
            if item.get("name") == file_path:
                file_id = item.get("id")
                break

        if not file_id:
            print(f"File '{file_path}' not found in drive")
            return None

        # Now download the file using its ID
        download_url = format_graph_url("drives", drive_id, "items", file_id, "content")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        download_response: Response = requests.get(download_url, headers=headers)
        if download_response.status_code == 200:
            print(f"✓ Successfully downloaded: {file_path}")
            return download_response.content
        print(f"Error downloading file. Status code: {download_response.status_code}")
        return None

    ##################################################################################
    # Create Logic
    ##################################################################################
    def create_folder(
        self, drive_id: str, parent_folder_id: str, folder_name: str, site_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create a new folder in SharePoint"""
        if not self.access_token:
            return None

        # Use drives/{drive_id} directly without site context
        url = format_graph_url(
            "drives", drive_id, "items", parent_folder_id, "children"
        )
        data = {
            "name": folder_name,
            "folder": {},  # Folder indicator
            "@microsoft.graph.conflictBehavior": "rename",
        }

        response = make_graph_request(url, self.access_token, method="POST", data=data)
        return response if response else None
