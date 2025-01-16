from sharepycrud.config import SharePointConfig
from sharepycrud.clientFactory import ClientFactory
from sharepycrud.logger import setup_logging


def main() -> None:
    setup_logging(level="DEBUG", log_file="nested_folder_file_upload.log")

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

    folder_info = read_client.get_nested_folder_info(
        drive_id, "Folder1Test/FolderNest1/FolderNest2"
    )
    if folder_info is None:
        print("Failed to get folder info")
        return

    folder_id = folder_info["id"]
    print(f"Uploading to folder: {folder_info['name']} (ID: {folder_id})")

    # Specify the file name and path
    file_name = "upload_test.txt"
    file_path = "/Users/willemseethaler/Documents/GitHub/SharePyCrud/upload_test.txt"
    # Call the upload method
    file_id = create_client.upload_file_to_folder(
        drive_id, folder_id, file_name, file_path
    )
    if file_id:
        print(f"File uploaded successfully with ID: {file_id}")
    else:
        print("File upload failed or was aborted due to an existing file.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
