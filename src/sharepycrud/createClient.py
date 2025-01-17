from typing import Optional, Dict, Any, List
import requests
from sharepycrud.baseClient import BaseClient
from sharepycrud.logger import get_logger

logger = get_logger("sharepycrud.createClient")


class CreateClient:
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

    def create_folder(self, drive_id: str, folder_name: str) -> Optional[str]:
        """
        Create a folder in a drive.

        Args:
            drive_id: ID of the drive where the folder will be created.
            folder_name: Name of the folder to create.

        Returns:
            The ID of the created folder, or None if the request fails.
        """
        logger.info(f"Creating folder: {folder_name}")

        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("drives", drive_id, "root/children")
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }

        response = self.client.make_graph_request(url, method="POST", data=data)
        if not response:
            logger.info(f"Failed to create folder: {folder_name}")
            return None

        folder_id = response.get("id")
        if isinstance(folder_id, str):
            logger.info(f"Successfully created folder: {folder_name}")
            return folder_id

        logger.info(f"Failed to create folder: {folder_name}")
        return None

    def create_file(
        self, drive_id: str, folder_id: str, file_name: str
    ) -> Optional[str]:
        """Create an empty file in a specified folder.
        Args:
            drive_id: ID of the drive where the file will be created.
            folder_id: ID of the folder where the file will be created.
            file_name: Name of the file to create.
        Returns:
            The ID of the created file, or None if the request fails.
        """
        logger.info(f"Creating file: {file_name}")

        if not self.client.access_token:
            return None

        url = self.client.format_graph_url(
            "drives", drive_id, "items", folder_id, "children"
        )
        data = {
            "name": file_name,
            "file": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }

        response = self.client.make_graph_request(url, method="POST", data=data)
        if not response:
            logger.info(f"Failed to create file: {file_name}")
            return None

        file_id = response.get("id")
        if isinstance(file_id, str):
            logger.info(f"Successfully created file: {file_name}")
            return file_id

        logger.info(f"Failed to create file: {file_name}")
        return None

    def upload_file_to_folder(
        self, drive_id: str, folder_id: str, file_name: str, file_path: str
    ) -> Optional[str]:
        """Upload a file to a specified folder.
        Args:
            drive_id: ID of the drive where the file will be uploaded.
            folder_id: ID of the folder where the file will be uploaded.
            file_name: Name of the file to upload.
            file_path: Path to the file to upload.
        Returns:
            The ID of the uploaded file, or None if the request fails.
        """
        logger.info(f"Uploading file: {file_name}")

        if not self.client.access_token:
            return None

        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
        except FileNotFoundError:
            logger.info(f"File not found: {file_name}")
            return None

        url = self.client.format_graph_url(
            "drives", drive_id, "items", f"{folder_id}:/{file_name}:/content"
        )

        response = self.client.make_graph_request(
            url,
            method="PUT",
            data=file_content,
            headers={"Content-Type": "application/octet-stream"},
        )

        if not response:
            logger.info(f"Failed to upload file: {file_name}")
            return None

        file_id = response.get("id")
        if isinstance(file_id, str):
            logger.info(f"Successfully uploaded file: {file_name}")
            return file_id

        logger.info(f"Failed to upload file: {file_name}")
        return None

    def create_list(
        self, site_id: str, list_name: str, list_template: str = "genericList"
    ) -> Optional[str]:
        """Create a new SharePoint list.
        Args:
            site_id: ID of the SharePoint site where the list will be created.
            list_name: Name of the list to create.
            list_template: Template to use for the list (default is "genericList").
        Returns:
            The ID of the created list, or None if the request fails.
        """
        logger.info(f"Creating list: {list_name}")

        if not self.client.access_token:
            return None

        url = self.client.format_graph_url("sites", site_id, "lists")
        data = {
            "displayName": list_name,
            "list": {
                "template": list_template,
            },
        }

        response = self.client.make_graph_request(url, method="POST", data=data)
        if not response:
            logger.info(f"Failed to create list: {list_name}")
            return None

        list_id = response.get("id")
        if isinstance(list_id, str):
            logger.info(f"Successfully created list: {list_name}")
            return list_id

        logger.info(f"Failed to create list: {list_name}")
        return None

    def create_document_library(self, site_id: str, library_name: str) -> Optional[str]:
        """Create a document library in a SharePoint site.
        Args:
            site_id: ID of the SharePoint site where the document library will be created.
            library_name: Name of the document library to create.
        Returns:
            The ID of the created document library, or None if the request fails.
        """
        logger.info(f"Creating document library: {library_name}")

        if not self.client.access_token:
            return None

        library_id = self.create_list(
            site_id, library_name, list_template="documentLibrary"
        )
        if library_id:
            logger.info(f"Successfully created document library: {library_name}")
        else:
            logger.info(f"Failed to create document library: {library_name}")

        return library_id
