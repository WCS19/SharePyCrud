from sharepycrud.createClient import CreateClient
from sharepycrud.readClient import ReadClient
from sharepycrud.config import SharePointConfig


def main() -> None:
    config = SharePointConfig.from_env()
    create_client = CreateClient(config)
    read_client = ReadClient(config)

    site_id = read_client.get_site_id(site_name="TestSite1")
    if site_id is None:
        print("Failed to get site ID")
        return

    drive_id = read_client.get_drive_id(site_id, "Documents")
    if drive_id is None:
        print("Failed to get drive ID")
        return

    folder_id = create_client.create_folder(drive_id, "New Folder 1")
    if folder_id is None:
        print("Failed to create folder")
        return

    print(f"Folder created successfully with ID: {folder_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
