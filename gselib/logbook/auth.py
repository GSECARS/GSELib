# SPDX-License-Identifier: MIT

import os
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def load_credentials(env_file: str = ".env") -> Credentials:
    load_dotenv(Path(env_file))
    service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT", "service-account.json")
    return Credentials.from_service_account_file(service_account_file, scopes=SCOPES)


def get_services(env_file: str = ".env") -> tuple:
    creds = load_credentials(env_file)
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return docs, drive
