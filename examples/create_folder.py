from sharepycrud.client import SharePointClient
from sharepycrud.utils import setup_client


def main() -> None:
    """Example: Create a folder in the Documents drive"""
    client = setup_client()
    if client is None:
        return

    # Get site ID
    site_id = client.get_site_id(site_name="TestSite1")
    if not site_id:
        print("Failed to get site ID")
        return

    print(f"Site ID: {site_id}")

    # Get drive ID
    drive_id = client.get_drive_id(site_id=site_id, drive_name="Documents")
    if not drive_id:
        print("Failed to get drive ID")
        return

    print(f"Drive ID: {drive_id}")

    # Documents drive ID
    folder_name = "Folder1Test2"

    print(f"Creating folder '{folder_name}' in Documents drive...")
    response = client.create_folder(
        drive_id=drive_id,
        parent_folder_id="root",
        folder_name=folder_name,
        site_id=site_id,
    )

    if response:
        print(f"✓ Folder created successfully")
        print(f"Folder details: {response}")
    else:
        print("✗ Failed to create folder")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
