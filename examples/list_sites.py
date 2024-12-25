from sharepycrud.client import SharePointClient
from sharepycrud.utils import setup_client


def main() -> None:
    """Example: List all sites, drives, and root contents in SharePoint site"""
    client = setup_client()
    if client is None:
        return

    # Get site ID and list drives
    sites = client.list_sites()
    if not sites:
        print("Failed to get sites")
        return
    print(f"Sites: {sites}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
