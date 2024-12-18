import os
from src.config import SharePointConfig
from src.sharepoint_client import SharePointClient
from typing import Optional, NoReturn


def setup_client() -> Optional[SharePointClient]:
    """Initialize SharePoint client with configuration"""
    config = SharePointConfig.from_env()

    # Validate config (Debug print)
    if not all([config.tenant_id, config.client_id, config.client_secret]):
        print("Error: Missing required environment variables.")
        print(f"TENANT_ID: {'Set' if config.tenant_id else 'Missing'}")
        print(f"CLIENT_ID: {'Set' if config.client_id else 'Missing'}")
        print(f"CLIENT_SECRET: {'Set' if config.client_secret else 'Missing'}")
        return None
    return SharePointClient(config)


def list_site_drives(client: SharePointClient, site_name: Optional[str] = None) -> None:
    """List all drives in a SharePoint site"""
    site_id = client.get_site_id(site_name=site_name)
    if not site_id:
        print("Failed to get site ID")
        return

    print(f"\nSite ID: {site_id}")

    drives = client.list_drives(site_id)
    if not drives:
        print("No drives found")


def explore_drive_contents(
    client: SharePointClient,
    site_name: Optional[str] = None,
    drive_name: Optional[str] = None,
) -> None:
    """Explore contents of a specific drive"""
    site_id = client.get_site_id(site_name=site_name)
    if not site_id:
        print("Failed to get site ID")
        return

    drive_id = client.get_drive_id_by_name(site_id, drive_name) if drive_name else None
    if not drive_id:
        print(f"Drive '{drive_name}' not found")
        return

    print(f"\nExploring drive: {drive_name}")
    print("Folder structure:")
    folders = client.list_all_folders(drive_id)

    if folders:
        print("\nFolder contents:")
        for folder in folders:
            contents = client.get_folder_content(drive_id, folder["id"])
            if contents:
                print(f"\nContents of {folder['name']}:")
                for item in contents:
                    print(f"- {item['name']} ({item['type']})")


def main() -> None:
    """Main execution function"""
    print("=== SharePoint Explorer ===")

    config = SharePointConfig.from_env()
    print("Config values:")
    print(f"Tenant ID: {config.tenant_id}")
    print(f"Client ID: {config.client_id}")
    print(f"Client Secret: {'*' * len(config.client_secret)}")
    print(f"Site Name: {config.site_name}")
    print(f"SharePoint URL: {config.sharepoint_url}")

    client = setup_client()
    if not client:
        print("Failed to initialize client")
        return

    if client.access_token:
        print(f"Access Token: {client.access_token[:50]}")

    print("=== SharePoint Explorer ===")

    list_site_drives(client)
    explore_drive_contents(client, site_name="TestSite1", drive_name="Files")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
