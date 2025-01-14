from sharepycrud.baseClient import BaseClient
from sharepycrud.config import SharePointConfig
from typing import Optional
import requests


class CreateClient(BaseClient):
    def __init__(self, config: SharePointConfig):
        super().__init__(config)

    def create_folder(self, drive_id: str, folder_name: str) -> Optional[str]:
        """
        Create a folder in a drive.

        Args:
            drive_id: ID of the drive where the folder will be created.
            folder_name: Name of the folder to create.

        Returns:
            The ID of the created folder, or None if the request fails.
        """
        if not self.access_token:
            return None

        url = self.format_graph_url("drives", drive_id, "root/children")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "name": folder_name,
            "folder": {},  # Required to indicate creation of a folder
            "@microsoft.graph.conflictBehavior": "fail",  # Explicitly fail on conflicts
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:  # HTTP 201 Created
            response_json = response.json()
            folder_id = response_json.get("id")
            if isinstance(folder_id, str):
                return folder_id
            print("Error: Created folder ID is not a string")
            return None
        else:
            print(f"Error creating folder: {response.status_code}")
            print(response.json())
            return None

    def create_file(
        self, drive_id: str, folder_id: str, file_name: str
    ) -> Optional[str]:
        """
        Create an empty file in a specified folder.

        Args:
            drive_id: ID of the drive where the file will be created.
            folder_id: ID of the folder to create the file in.
            file_name: Name of the file to create.

        Returns:
            The ID of the created file, or None if the request fails.
        """
        if not self.access_token:
            return None

        url = self.format_graph_url("drives", drive_id, "items", folder_id, "children")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "name": file_name,
            "file": {},  # Indicates the creation of a file
            "@microsoft.graph.conflictBehavior": "fail",  # Fail if a file with the same name exists
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:  # HTTP 201 Created
            response_json = response.json()
            file_id = response_json.get("id")
            if isinstance(file_id, str):
                return file_id
            print("Error: Created file ID is not a string")
            return None
        else:
            print(f"Error creating file: {response.status_code}")
            print(response.json())
            return None

    def upload_file_to_folder(
        self, drive_id: str, folder_id: str, file_name: str, file_path: str
    ) -> Optional[str]:
        """
        Upload a file from the local file system to a specified folder in the drive.

        Args:
            drive_id: ID of the drive.
            folder_id: ID of the folder where the file will be uploaded.
            file_name: Name of the file to use in the destination folder.
            file_path: Path to the file on the local file system.

        Returns:
            The ID of the uploaded file, or None if the request fails.
        """
        if not self.access_token:
            return None

        # Read the file as binary data
        with open(file_path, "rb") as file:
            file_content = file.read()

        url = self.format_graph_url(
            "drives", drive_id, "items", f"{folder_id}:/{file_name}:/content"
        )
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/octet-stream",
        }

        response = requests.put(url, headers=headers, data=file_content)

        if response.status_code == 201:  # HTTP 201 Created
            response_json = response.json()
            file_id = response_json.get("id")
            if isinstance(file_id, str):
                return file_id
            print("Error: Uploaded file ID is not a string")
            return None
        else:
            print(f"Error uploading file: {response.status_code}")
            print(response.json())
            return None

    def create_list(
        self, site_id: str, list_name: str, list_template: str = "genericList"
    ) -> Optional[str]:
        """
        Create a new SharePoint list.

        Args:
            site_id: ID of the SharePoint site where the list will be created.
            list_name: Name of the list to create.
            list_template: Template type for the list (default: "genericList").

        Returns:
            The ID of the created list, or None if the request fails.
        """
        if not self.access_token:
            return None

        url = self.format_graph_url("sites", site_id, "lists")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "displayName": list_name,
            "list": {
                "template": list_template,
            },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:  # HTTP 201 Created
            response_json = response.json()
            list_id = response_json.get("id")
            if isinstance(list_id, str):
                return list_id
            print("Error: Created list ID is not a string")
            return None
        else:
            print(f"Error creating list: {response.status_code}")
            print(response.json())
            return None

    def create_document_library(self, site_id: str, library_name: str) -> Optional[str]:
        """
        Create a document library in a SharePoint site.

        Args:
            site_id: ID of the SharePoint site.
            library_name: Name of the document library to create.

        Returns:
            The ID of the created document library, or None if the request fails.
        """
        if not self.access_token:
            return None

        url = self.format_graph_url("sites", site_id, "lists")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "displayName": library_name,
            "list": {
                "template": "documentLibrary",  # Template for document libraries
            },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:  # HTTP 201 Created
            response_json = response.json()
            library_id = response_json.get("id")
            if isinstance(library_id, str):
                return library_id
            print("Error: Created library ID is not a string")
            return None
        else:
            print(f"Error creating document library: {response.status_code}")
            print(response.json())
            return None
