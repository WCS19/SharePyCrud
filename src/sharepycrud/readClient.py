from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Optional, List, Dict, Any, Tuple
import requests
from requests import Response
import logging

logger = logging.getLogger(__name__)


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

        if response is None:  # Request failed
            logger.error("Failed to retrieve sites")
            return None

        site_names = [site.get("name") for site in response.get("value", [])]
        if not site_names:  # No sites found
            logger.info("No sites found")
        else:
            logger.info(f"Found {len(site_names)} sites")

        return site_names

    # def list_sites(self) -> Optional[List[Optional[str]]]:
    #     """List all sites

    #     Args:
    #         None

    #     Returns:
    #         List of site names, or None if request fails.
    #         Individual site names can be None if they don't have a name.
    #     """
    #     if not self.client.access_token:
    #         return None
    #     url = self.client.format_graph_url("sites")
    #     response = self.client.make_graph_request(url)

    #     # Extract site names, allowing for None values
    #     site_names = (
    #         [site.get("name") for site in response.get("value", [])]
    #         if response
    #         else None
    #     )
    #     if not site_names:
    #         logger.info("No sites found")
    #     else:
    #         logger.info(f"Found {len(site_names)} sites")
    #     return site_names

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

        try:
            response = self.client.make_graph_request(url)
            site_id = response.get("id")

            if isinstance(site_id, str):
                logger.info(f"Found site: {site_name}")
                logger.info(f"Site ID: {site_id}")
                return site_id

            return None

        except (requests.exceptions.RequestException, ValueError):
            return None

    def list_drives(self, site_id: str) -> Optional[Dict[str, Any]]:
        """List all drives and their root contents.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            Dictionary of drives and their root contents, or None if request fails.
        """
        if not self.client.access_token:
            logger.error("Access token is missing or invalid")
            return None

        url = self.client.format_graph_url("sites", site_id, "drives")
        response = self.client.make_graph_request(url)

        if response and "value" in response:
            logger.info("=== Drives ===")
            for drive in response["value"]:
                logger.info(f"Drive: {drive['name']}, ID: {drive['id']}")

                # Get root folder contents
                root_url = self.client.format_graph_url(
                    "drives", drive["id"], "root", "children"
                )
                root_contents = self.client.make_graph_request(root_url)

                if root_contents and "value" in root_contents:
                    logger.info("Root contents:")
                    for item in root_contents["value"]:
                        item_type = "folder" if "folder" in item else "file"
                        logger.info(f"- {item['name']} ({item_type})")
                else:
                    logger.info("No items in root folder")

            return response

        logger.error("Failed to list drives")
        return None

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

        if not response or "value" not in response:
            logger.error("Failed to list drives")
            return None

        drives: List[Dict[str, Any]] = response["value"]
        for drive in drives:
            if isinstance(drive, dict) and drive.get("name") == drive_name:
                drive_id = drive.get("id")
                if isinstance(drive_id, str):
                    logger.info(f"Found drive: {drive_name}")
                    return drive_id

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
        if not response or "value" not in response:
            logger.error("Failed to list folder contents")
            return folders

        for item in response["value"]:
            if "folder" in item:
                folder_name = item["name"]
                folder_id = item["id"]
                folder_path = item["parentReference"]["path"] + f"/{folder_name}"

                logger.info(f"{'  ' * level}- Folder: {folder_name} (ID: {folder_id})")
                folders.append(
                    {"name": folder_name, "id": folder_id, "path": folder_path}
                )

                subfolders = self.list_all_folders(drive_id, folder_id, level + 1)
                folders.extend(subfolders)
                logger.info(f"Found {len(subfolders)} subfolders")

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

        try:
            response = self.client.make_graph_request(url)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return None

        # Ensure response is a dictionary
        if not isinstance(response, dict):
            logger.error("Unexpected response format")
            return None

        # Check if the response contains an error
        if "error" in response:
            logger.error(
                f"Error getting folder contents: {response['error'].get('code')}"
            )
            logger.error(f"Message: {response['error'].get('message')}")
            return None

        items = response.get("value", [])
        parent_folders = []

        for item in items:
            if "folder" in item:
                folder_name = item["name"]
                folder_id = item["id"]
                folder_path = item["parentReference"]["path"] + f"/{folder_name}"
                parent_folders.append({"name": folder_name, "path": folder_path})
                logger.info(f"Found parent folder: {folder_name}")

        return parent_folders

    # def list_parent_folders(self, drive_id: str) -> Optional[List[Dict[str, Any]]]:
    #     """List only top-level (parent) folders within a drive.

    #     Args:
    #         drive_id: ID of the drive to search in.

    #     Returns:
    #         A list of parent folders, or None if the request fails.
    #     """
    #     if not self.client.access_token:
    #         return None

    #     url = self.client.format_graph_url("drives", drive_id, "root/children")
    #     response = self.client.make_graph_request(url)

    #     # Ensure response is a dictionary
    #     if not isinstance(response, dict):
    #         logger.error("Unexpected response format")
    #         return None

    #     # Check if the response contains an error
    #     if "error" in response:
    #         logger.error(
    #             f"Error getting folder contents: {response['error'].get('code')}"
    #         )
    #         logger.error("Message:", response["error"].get("message"))
    #         return None

    #     items = response.get("value", [])
    #     parent_folders = []

    #     for item in items:
    #         if "folder" in item:
    #             folder_name = item["name"]
    #             folder_id = item["id"]
    #             folder_path = item["parentReference"]["path"] + f"/{folder_name}"
    #             parent_folders.append({"name": folder_name, "path": folder_path})
    #             logger.info(f"Found parent folder: {folder_name}")

    #     return parent_folders

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
            logger.error("Failed to get folder contents")
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

        logger.info(f"Found {len(folder_contents)} items in folder")
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

            if "value" in response:
                folders = [
                    item
                    for item in response["value"]
                    if item["name"] == folder_name and "folder" in item
                ]
                if (
                    folders
                    and isinstance(folders[0]["id"], str)
                    and isinstance(folders[0]["name"], str)
                ):
                    current_parent_id = folders[0]["id"]
                    deepest_folder_name = folders[0]["name"]
                else:
                    logger.error(
                        f"Folder '{folder_name}' not found in path '{folder_path}'."
                    )
                    return None
            else:
                logger.error(f"Error validating folder path. Response: {response}")
                return None

        if deepest_folder_name is None:
            logger.error(f"No folder found in path '{folder_path}'.")
            return None
        logger.info(f"Found folder: {deepest_folder_name}, ID: {current_parent_id}")
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

        if "value" in response:
            # Look for a file with the same name
            for item in response["value"]:
                if item.get("name") == file_name and "file" in item:
                    logger.info(f"File '{file_name}' exists in folder '{folder_id}'")
                    return True
        else:
            logger.error(f"Error checking file existence. Response: {response}")
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
            logger.error("Failed to get site ID")
            return None

        drive_id = self.get_drive_id(site_id, drive_name) if drive_name else None
        if not drive_id:
            logger.error(f"Drive '{drive_name}' not found")
            return None

        url = self.client.format_graph_url("drives", drive_id, "root/children")

        # Get the file ID
        list_response = self.client.make_graph_request(url)
        if not list_response or "value" not in list_response:
            logger.error("Failed to list drive contents")
            return None

        file_id = None
        for item in list_response["value"]:
            if item.get("name") == file_path:
                file_id = item.get("id")
                logger.info(f"Found file: {file_path}")
                break

        if not file_id:
            logger.error(f"File '{file_path}' not found in drive")
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
        logger.error(
            f"Error downloading file. Status code: {download_response.status_code}"
        )
        return None
