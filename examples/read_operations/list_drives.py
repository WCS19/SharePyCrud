from sharepycrud.readClient import ReadClient
from sharepycrud.config import SharePointConfig


def main() -> None:
    """Example: List drives and root contents in SharePoint site"""
    config = SharePointConfig.from_env()
    client = ReadClient(config)

    site_id = client.get_site_id(site_name="TestSite1")
    if not site_id:
        print("Failed to get site ID")
        return

    print(f"\nSite ID: {site_id}")

    # List drives and root contents
    drives = client.list_drives(site_id)
    if not drives:
        print("No drives found")

    drive_name = "Documents"
    drive_id = client.get_drive_id(site_id, drive_name)
    if not drive_id:
        print("Failed to get drive ID")
        return

    parent_folders = client.list_parent_folders(drive_id=drive_id)
    print(f"\nParent folders: {parent_folders}")
    if parent_folders is not None:
        for folder in parent_folders:
            print(f"Folder: {folder['name']} (ID: {folder['path']})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
