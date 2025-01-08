from sharepycrud.client import SharePointClient
from sharepycrud.utils import setup_client


def main() -> None:
    """Example: Get drive ID by its name"""
    client = setup_client()
    if client is None:
        return

    site_id = client.get_site_id(site_name="TestSite1")
    if not site_id:
        print("Failed to get site ID")
        return

    drive_id = client.get_drive_id(
        site_id=site_id, drive_name="Files"
    )  # Drive name set to "Files" since I created a files drive
    if not drive_id:
        print("Failed to get drive ID")
        return

    print(f"Drive ID: {drive_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
