from sharepycrud.client import SharePointClient
from sharepycrud.utils import setup_client


def main() -> None:
    """Example: List drives and root contents in SharePoint site"""
    client = setup_client()
    if client is None:
        return

    site_id = client.get_site_id(site_name="TestSite1")
    if not site_id:
        print("Failed to get site ID")
        return

    drive_id = client.get_drive_id(site_id, "Documents")
    print(f"Drive ID: {drive_id}")
    if not drive_id:
        print("Failed to get drive ID")
        return

    folder_id = client.get_folder_id(drive_id, "Folder1Test")
    print(f"Folder ID: {folder_id}")
    if not folder_id:
        print("Failed to get folder ID")
        return

    folder_content = client.get_folder_content(drive_id=drive_id, folder_id=folder_id)
    print(f"Folder content: {folder_content}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
