from sharepycrud.clientFactory import ClientFactory
from sharepycrud.config import SharePointConfig
from sharepycrud.logger import setup_logging


def main() -> None:
    """Example: Get drive ID by its name"""
    setup_logging(level="INFO", log_file="get_drive_id.log")
    config = SharePointConfig.from_env()

    client = ClientFactory.create_read_client(config)

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
