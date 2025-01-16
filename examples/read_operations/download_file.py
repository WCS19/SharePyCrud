from sharepycrud.readClient import ReadClient
from sharepycrud.config import SharePointConfig
import os
from sharepycrud.logger import setup_logging
from sharepycrud.clientFactory import ClientFactory


def main() -> None:
    """Example: Download a file from SharePoint"""
    setup_logging(level="INFO", log_file="download_file.log")

    config = SharePointConfig.from_env()
    read_client = ClientFactory.create_read_client(config)

    # Download and save file
    file_content = read_client.download_file(
        file_path="Willem Seethaler Resume 2024.docx",
        site_name="TestSite1",
        drive_name="Files",
    )

    if file_content:
        save_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Willem Seethaler Resume 2024.docx",
        )
        with open(save_path, "wb") as f:
            f.write(file_content)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
