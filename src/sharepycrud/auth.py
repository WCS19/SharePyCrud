### RENDERED OBSOLETE BY BASECLIENT


# from typing import Dict
# import requests
# import os


# class SharePointAuth:
#     def __init__(self, tenant_id: str, client_id: str, client_secret: str):
#         self.tenant_id = tenant_id
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.base_url = (
#             f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
#         )
#         self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

#     def get_access_token(self) -> str:
#         body = {
#             "grant_type": "client_credentials",
#             "client_id": self.client_id,
#             "client_secret": self.client_secret,
#             "scope": "https://graph.microsoft.com/.default",
#         }
#         response = requests.post(self.base_url, headers=self.headers, data=body)
#         token = response.json().get("access_token")
#         if not isinstance(token, str):
#             raise ValueError("Failed to get valid access token")
#         return token
