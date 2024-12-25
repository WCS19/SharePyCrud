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

    print(f"\nSite ID: {site_id}")

    # List drives and root contents
    drives = client.list_drives(site_id)
    if not drives:
        print("No drives found")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
