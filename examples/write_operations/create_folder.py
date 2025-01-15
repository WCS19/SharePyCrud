from sharepycrud.clientFactory import ClientFactory
from sharepycrud.config import SharePointConfig
from sharepycrud.logger import setup_logging


def main() -> None:
    setup_logging(level="DEBUG", log_file="create_folder_example.log")

    config = SharePointConfig.from_env()
    create_client = ClientFactory.create_write_client(config)
    read_client = ClientFactory.create_read_client(config)

    site_id = read_client.get_site_id(site_name="TestSite1")
    if site_id is None:
        print("Failed to get site ID")
        return

    drive_id = read_client.get_drive_id(site_id, "Documents")
    if drive_id is None:
        print("Failed to get drive ID")
        return

    folder_id = create_client.create_folder(drive_id, "New Folder 7")
    if folder_id is None:
        print("Failed to create folder")
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
