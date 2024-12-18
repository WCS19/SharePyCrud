from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv


@dataclass
class SharePointConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    site_name: str
    sharepoint_url: str
    resource_url: str = "https://graph.microsoft.com/"

    @classmethod
    def from_env(cls) -> "SharePointConfig":
        load_dotenv()
        return cls(
            tenant_id=os.getenv("TENANT_ID", ""),
            client_id=os.getenv("CLIENT_ID", ""),
            client_secret=os.getenv("CLIENT_SECRET", ""),
            site_name=os.getenv("SITE_NAME", ""),
            sharepoint_url=os.getenv("SHAREPOINT_URL", ""),
        )
