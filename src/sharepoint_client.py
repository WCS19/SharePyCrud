from typing import Dict, List, Optional, Tuple, Any
import os
from src.utils import make_graph_request, format_graph_url
from src.config import SharePointConfig


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

    def get_site_id(
        self, sharepoint_url: Optional[str] = None, site_name: Optional[str] = None
    ) -> Optional[str]:
        """Get site ID from SharePoint URL"""
        if not self.access_token:
            return None
        base_url = sharepoint_url or self.config.sharepoint_url
        site = site_name or self.config.site_name

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
            print("Drives:")
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

    def get_drive_id(self, site_id: str) -> List[Tuple[str, str]]:
        """Get all drive IDs and names for a site"""
        if not self.access_token:
            return []
        url = format_graph_url("sites", site_id, "drives")
        response = make_graph_request(url, self.access_token)
        drives = response.get("value", []) if response else []
        return [(drive["id"], drive["name"]) for drive in drives]

    def get_drive_id_by_name(self, site_id: str, drive_name: str) -> Optional[str]:
        """Get drive ID by its name"""
        if not self.access_token:
            return None

        url = format_graph_url("sites", site_id, "drives")
        response = make_graph_request(url, self.access_token)

        if response and "value" in response:
            for drive in response["value"]:
                drive_id = drive.get("id")
                if (
                    isinstance(drive_id, str)
                    and drive["name"].lower() == drive_name.lower()
                ):
                    return drive_id
            print(f"Drive with name '{drive_name}' not found.")
        return None

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
