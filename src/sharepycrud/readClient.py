from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Optional, List, Dict, Any, Tuple
import requests
from requests import Response
from sharepycrud.logger import get_logger

logger = get_logger("sharepycrud.readClient")


class ReadClient:
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

    def list_sites(self) -> Optional[List[Optional[str]]]:
        """List all sites
        Args:
            None

        Returns:
            List of site names, or None if request fails.
            Individual site names can be None if they don't have a name.
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("sites")
        response = self.client.make_graph_request(url)

        if response is None:
            return None

        site_names = [site.get("name") for site in response.get("value", [])]
        logger.info(f"Found {len(site_names)} sites")
        logger.info(f"Site names: {site_names}")
        return site_names

    def get_site_id(
        self, site_name: str, sharepoint_url: Optional[str] = None
    ) -> Optional[str]:
        """Get site ID from SharePoint URL.

        Args:
            site_name: Name of the SharePoint site (required)
            sharepoint_url: Optional SharePoint URL, defaults to configured URL

        Returns:
            Site ID if found, None otherwise
        """
        if not self.client.access_token:
            return None

        if not site_name:
            logger.error("Site name is required")
            return None

        base_url = sharepoint_url or self.client.config.sharepoint_url
        url = self.client.format_graph_url(f"sites/{base_url}:/sites/{site_name}")

        response = self.client.make_graph_request(url)
        if not response:
            return None

        site_id = response.get("id")
        if isinstance(site_id, str):
            logger.info(f"Found site: {site_name}")
            logger.info(f"Site ID: {site_id}")
            return site_id

        return None

    def list_drive_names(self, site_id: str) -> Optional[List[str]]:
        """List all drive names for a site.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            List of drive names, or None if request fails
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("sites", site_id, "drives")
        response = self.client.make_graph_request(url)
        if not response:
            return None

        drive_names = [drive.get("name") for drive in response.get("value", [])]
        logger.info(f"Found {len(drive_names)} drives")
        logger.info(f"Drive names: {drive_names}")
        return drive_names

    def list_drives_and_root_contents(self, site_id: str) -> Optional[Dict[str, Any]]:
        """List all drives and their root contents.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            Dictionary of drives and their root contents, or None if request fails.
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("sites", site_id, "drives")
        response = self.client.make_graph_request(url)

        if not response:
            return None

        logger.info(f"Found {len(response.get('value', []))} drives")

        for drive in response.get("value", []):
            logger.info(f"Processing drive: {drive['name']}")

            root_url = self.client.format_graph_url(
                "drives", drive["id"], "root", "children"
            )
            root_contents = self.client.make_graph_request(root_url)

            if root_contents:
                items = root_contents.get("value", [])
                folders = sum(1 for item in items if "folder" in item)
                files = len(items) - folders
                logger.info(
                    f"Drive '{drive['name']}' contains {folders} folders and {files} files"
                )

        return response

    def get_drive_id(self, site_id: str, drive_name: str) -> Optional[str]:
        """Get drive ID by its name.

        Args:
            site_id: ID of the SharePoint site
            drive_name: Name of the drive

        Returns:
            Drive ID if found, None otherwise
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("sites", site_id, "drives")
        response = self.client.make_graph_request(url)

        if not response:
            return None

        drives: List[Dict[str, Any]] = response.get("value", [])
        for drive in drives:
            if isinstance(drive, dict) and drive.get("name") == drive_name:
                drive_id = drive.get("id")
                if isinstance(drive_id, str):
                    logger.info(f"Found drive: {drive_name}, ID: {drive_id}")
                    return drive_id

        logger.info(f"Drive not found: {drive_name}")
        return None

    def list_drive_ids(self, site_id: str) -> List[Tuple[str, str]]:
        """Get all drive IDs and names for a site.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            List of tuples containing drive IDs and names, or an empty list if no drives are found.
        """
        if not self.client.access_token:
            return []
        url = self.client.format_graph_url("sites", site_id, "drives")
        response = self.client.make_graph_request(url)
        drives = response.get("value", []) if response else []
        logger.info(f"Found {len(drives)} drives")
        return [(drive["id"], drive["name"]) for drive in drives]

    def list_all_folders(
        self, drive_id: str, parent_path: str = "root", level: int = 0
    ) -> List[Dict[str, Any]]:
        """Recursively list all folders within a drive.

        Args:
            drive_id: ID of the drive.
            parent_path: Path of the parent folder.
            level: Current level of recursion.

        Returns:
            A list of folders within the specified parent path.
        """
        if not self.client.access_token:
            return []

        url = self.client.format_graph_url(
            "drives", drive_id, "items", parent_path, "children"
        )
        response = self.client.make_graph_request(url)

        folders: List[Dict[str, Any]] = []
        if not response:
            return folders

        for item in response.get("value", []):
            if "folder" in item:
                folder_name = item["name"]
                folder_id = item["id"]
                folder_path = item["parentReference"]["path"] + f"/{folder_name}"

                logger.info(f"Processing folder: {folder_name} at level {level}")
                folders.append(
                    {"name": folder_name, "id": folder_id, "path": folder_path}
                )

                subfolders = self.list_all_folders(drive_id, folder_id, level + 1)
                folders.extend(subfolders)
                if subfolders:
                    logger.info(f"Found {len(subfolders)} subfolders in {folder_name}")

        return folders

    def list_parent_folders(self, drive_id: str) -> Optional[List[Dict[str, Any]]]:
        """List only top-level (parent) folders within a drive.

        Args:
            drive_id: ID of the drive to search in.

        Returns:
            A list of parent folders, or None if the request fails.
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("drives", drive_id, "root/children")
        response = self.client.make_graph_request(url)

        if not response:
            return None

        parent_folders = []
        for item in response.get("value", []):
            if "folder" in item:
                folder_name = item["name"]
                folder_path = item["parentReference"]["path"] + f"/{folder_name}"
                parent_folders.append({"name": folder_name, "path": folder_path})
                logger.info(f"Found parent folder: {folder_name}")

        logger.info(f"Found {len(parent_folders)} parent folders")
        return parent_folders

    def get_root_folder_id_by_name(
        self, drive_id: str, folder_name: str
    ) -> Optional[str]:
        """Get a drive's root folder ID by its name.

        Args:
            drive_id: ID of the drive.
            folder_name: Name of the folder.

        Returns:
            The ID of the root folder, or None if not found.
        """
        if not self.client.access_token:
            return None
        url = self.client.format_graph_url("drives", drive_id, "root/children")
        response = self.client.make_graph_request(url)
        if response and "value" in response:
            for item in response["value"]:
                if item.get("name") == folder_name:
                    folder_id = item.get("id")
                    if isinstance(folder_id, str):
                        logger.info(f"Found folder: {folder_name}, ID: {folder_id}")
                        return folder_id

        return None

    def get_folder_content(
        self, drive_id: str, folder_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get contents of a folder using its ID.

        Args:
            drive_id: ID of the drive.
            folder_id: ID of the folder.

        Returns:
            A list of folder contents, or None if the request fails.
        """
        if not self.client.access_token:
            return None

        url = self.client.format_graph_url(
            "drives", drive_id, "items", folder_id, "children"
        )
        response = self.client.make_graph_request(url)

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

        folders = sum(1 for item in folder_contents if item["type"] == "folder")
        files = len(folder_contents) - folders
        logger.info(f"Found {folders} folders and {files} files")

        return folder_contents

    def get_nested_folder_info(
        self, drive_id: str, folder_path: str
    ) -> Optional[Dict[str, str]]:
        """
        Validate and find the ID and name of the deepest folder in a nested folder path.

        Args:
            drive_id: ID of the drive.
            folder_path: Full path of the nested folder structure (e.g., "Folder1/FolderNest1/FolderNest2").

        Returns:
            A dictionary with the 'id' and 'name' of the deepest folder, or None if any folder in the hierarchy is missing.
        """
        if not self.client.access_token:
            return None

        folder_names = self.parse_folder_path(folder_path)
        current_parent_id = "root"
        deepest_folder_name: Optional[str] = None

        for folder_name in folder_names:
            url = self.client.format_graph_url(
                "drives", drive_id, "items", current_parent_id, "children"
            )
            response = self.client.make_graph_request(url)

            if not response:
                return None

            folders = [
                item
                for item in response.get("value", [])
                if item["name"] == folder_name and "folder" in item
            ]

            if folders:
                current_parent_id = folders[0]["id"]
                deepest_folder_name = folders[0]["name"]
                logger.info(f"Processing folder: {folder_name}")
            else:
                logger.info(f"Folder not found: {folder_name}")
                return None

        if deepest_folder_name is None:
            return None

        logger.info(f"Found deepest folder: {deepest_folder_name}")
        return {"id": current_parent_id, "name": deepest_folder_name}

    def file_exists_in_folder(
        self, drive_id: str, folder_id: str, file_name: str
    ) -> bool:
        """
        Check if a file with the given name exists in a specified folder.

        Args:
            drive_id: ID of the drive.
            folder_id: ID of the folder to search in.
            file_name: Name of the file to check.

        Returns:
            True if the file exists, False otherwise.
        """
        if not self.client.access_token:
            return False

        url = self.client.format_graph_url(
            "drives", drive_id, "items", folder_id, "children"
        )
        response = self.client.make_graph_request(url)

        if not response:
            return False

        for item in response.get("value", []):
            if item.get("name") == file_name and "file" in item:
                logger.info(f"Found file: {file_name}")
                return True

        logger.info(f"File not found: {file_name}")
        return False

    def download_file(
        self, file_path: str, site_name: str, drive_name: Optional[str] = None
    ) -> Optional[bytes]:
        """Download a file from SharePoint

        Args:
            file_path: Path to the file in SharePoint
            site_name: Optional name of the SharePoint site
            drive_name: Optional name of the drive containing the file

        Returns:
            File content as bytes if successful, None otherwise
        """
        if not self.client.access_token:
            return None

        site_id = self.get_site_id(site_name=site_name)
        if not site_id:
            logger.info(f"Site not found: {site_name}")
            return None

        drive_id = self.get_drive_id(site_id, drive_name) if drive_name else None
        if not drive_id:
            logger.info(f"Drive not found: {drive_name}")
            return None

        url = self.client.format_graph_url("drives", drive_id, "root/children")
        list_response = self.client.make_graph_request(url)

        if not list_response:
            return None

        file_id = None
        for item in list_response.get("value", []):
            if item.get("name") == file_path:
                file_id = item.get("id")
                logger.info(f"Found file: {file_path}")
                break

        if not file_id:
            logger.info(f"File not found: {file_path}")
            return None

        download_url = self.client.format_graph_url(
            "drives", drive_id, "items", file_id, "content"
        )
        headers = {
            "Authorization": f"Bearer {self.client.access_token}",
        }

        download_response: Response = requests.get(download_url, headers=headers)
        if download_response.status_code == 200:
            logger.info(f"Successfully downloaded: {file_path}")
            return download_response.content

        logger.info(f"Failed to download: {file_path}")
        return None
