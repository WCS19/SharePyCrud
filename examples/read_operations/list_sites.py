from sharepycrud.readClient import ReadClient
from sharepycrud.config import SharePointConfig


def main() -> None:
    """Example: List all sites, drives, and root contents in SharePoint site"""
    config = SharePointConfig.from_env()
    client = ReadClient(config)

    # Get site ID and list drives
    sites = client.list_sites()
    if not sites:
        print("Failed to get sites")
        return
    print(f"Sites: {sites}")

    # Get site ID
    site_id = client.get_site_id(site_name="TestSite1")
    if not site_id:
        print("Failed to get site ID")
        return

    print(f"Site ID: {site_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
