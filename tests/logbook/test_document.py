# SPDX-License-Identifier: MIT

import pytest

pytest.importorskip("google.oauth2")
pytest.importorskip("googleapiclient")

from unittest.mock import MagicMock

from gselib.logbook.document import create_document, share_document


class TestCreateDocument:
    def test_returns_document_id(self) -> None:
        """create_document returns the documentId from the API response."""
        docs = MagicMock()
        docs.documents().create().execute.return_value = {"documentId": "abc-123"}
        result = create_document(docs, "My Logbook")
        assert result == "abc-123"

    def test_passes_title(self) -> None:
        """create_document sends the title in the request body."""
        docs = MagicMock()
        docs.documents().create().execute.return_value = {"documentId": "x"}
        create_document(docs, "Test Title")
        call_kwargs = docs.documents().create.call_args.kwargs
        assert call_kwargs["body"]["title"] == "Test Title"


class TestShareDocument:
    def test_share_sets_permission(self) -> None:
        """share_document calls Drive permissions.create with the correct payload."""
        drive = MagicMock()
        share_document(drive, "doc-id", "user@example.com", "writer")
        body = drive.permissions().create.call_args.kwargs["body"]
        assert body["type"] == "user"
        assert body["role"] == "writer"
        assert body["emailAddress"] == "user@example.com"

    def test_share_targets_correct_file(self) -> None:
        """share_document passes the document_id as fileId."""
        drive = MagicMock()
        share_document(drive, "doc-id", "user@example.com", "reader")
        assert drive.permissions().create.call_args.kwargs["fileId"] == "doc-id"

    def test_share_sends_notification_email(self) -> None:
        """share_document enables notification emails."""
        drive = MagicMock()
        share_document(drive, "doc-id", "user@example.com", "writer")
        assert drive.permissions().create.call_args.kwargs["sendNotificationEmail"] is True
