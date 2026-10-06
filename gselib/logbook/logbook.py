# SPDX-License-Identifier: MIT

import datetime
import os
from pathlib import Path

from .auth import get_services
from .document import create_document, share_document
from .styles import apply_logbook_template, entry_style, timestamp_style


class Logbook:
    def __init__(self, document_id: str = None, env_file: str = ".env", create_title: str = None) -> None:
        self._docs, self._drive = get_services(env_file)

        if document_id:
            self.document_id = document_id
        elif create_title:
            self.document_id = create_document(self._docs, create_title)
            apply_logbook_template(self._docs, self.document_id, create_title)
        else:
            self.document_id = os.environ.get("LOGBOOK_DOCUMENT_ID")
            if not self.document_id:
                raise ValueError("Provide document_id, create_title, or set LOGBOOK_DOCUMENT_ID in your .env")

    def append(self, text: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}]  {text}\n"

        doc = self._docs.documents().get(documentId=self.document_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        ts_end = end_index + len(f"[{timestamp}]") + 2

        requests = [
            {"insertText": {"location": {"index": end_index}, "text": entry}},
            timestamp_style(end_index + 1, ts_end),
            entry_style(ts_end, end_index + len(entry)),
        ]

        self._docs.documents().batchUpdate(documentId=self.document_id, body={"requests": requests}).execute()
        print(f"Appended: [{timestamp}]  {text}")

    def save(self, path: str) -> None:
        ext = Path(path).suffix.lower()
        mime_map = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".md": "text/plain",
        }
        mime = mime_map.get(ext, "application/pdf")

        content = self._drive.files().export_media(fileId=self.document_id, mimeType=mime).execute()

        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        with open(path, "wb") as f:
            f.write(content)

        print(f"Saved local copy ({ext or '.pdf'}) to: {path}")

    def share(self, email: str, role: str = "writer") -> None:
        share_document(self._drive, self.document_id, email, role)
        print(f"Shared document with {email} as {role}")
