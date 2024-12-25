from dataclasses import dataclass
from typing import Optional, Tuple, List
import os
from dotenv import load_dotenv


@dataclass
class SharePointConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    sharepoint_url: str
    resource_url: str = "https://graph.microsoft.com/"

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate config and return status and list of missing fields"""
        required_fields = {
            "TENANT_ID": self.tenant_id,
            "CLIENT_ID": self.client_id,
            "CLIENT_SECRET": self.client_secret,
            "SHAREPOINT_URL": self.sharepoint_url,
        }

        missing_fields = [
            field_name for field_name, value in required_fields.items() if not value
        ]

        if len(missing_fields) == 0:
            print("✓ Configuration validated successfully")
        else:
            print("⚠ Configuration validation failed")

        return (len(missing_fields) == 0, missing_fields)

    @classmethod
    def from_env(cls) -> "SharePointConfig":
        load_dotenv()
        return cls(
            tenant_id=os.getenv("TENANT_ID", ""),
            client_id=os.getenv("CLIENT_ID", ""),
            client_secret=os.getenv("CLIENT_SECRET", ""),
            sharepoint_url=os.getenv("SHAREPOINT_URL", ""),
        )
