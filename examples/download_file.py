from sharepycrud.client import SharePointClient
from sharepycrud.utils import setup_client
import os


def main() -> None:
    """Example: Download a file from SharePoint"""
    client = setup_client()
    if client is None:
        return

    # Download and save file
    file_content = client.download_file(
        file_path="Willem Seethaler Resume 2024.docx",
        site_name="TestSite1",
        drive_name="Files",
    )

    if file_content:
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Willem Seethaler Resume 2024.docx")
        with open(save_path, "wb") as f:
            f.write(file_content)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
