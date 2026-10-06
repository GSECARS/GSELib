# SPDX-License-Identifier: MIT


def create_document(docs, title: str) -> str:
    doc = docs.documents().create(body={"title": title}).execute()
    return doc["documentId"]


def share_document(drive, document_id: str, email: str, role: str = "writer") -> None:
    permission = {"type": "user", "role": role, "emailAddress": email}
    drive.permissions().create(fileId=document_id, body=permission, sendNotificationEmail=True).execute()
