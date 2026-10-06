# SPDX-License-Identifier: MIT

import pytest

pytest.importorskip("google.oauth2")
pytest.importorskip("googleapiclient")
pytest.importorskip("dotenv")

from unittest.mock import MagicMock, patch

from gselib.logbook.logbook import Logbook


def _make_doc(end_index: int = 20) -> dict:
    return {"body": {"content": [{"endIndex": end_index + 1}]}}


@pytest.fixture
def services():
    docs = MagicMock()
    drive = MagicMock()
    docs.documents().get().execute.return_value = _make_doc()
    docs.documents().batchUpdate().execute.return_value = {}
    return docs, drive


@pytest.fixture
def logbook(services):
    docs, drive = services
    with patch("gselib.logbook.logbook.get_services", return_value=(docs, drive)):
        lb = Logbook(document_id="doc-123")
    return lb, docs, drive


class TestLogbookInit:
    def test_document_id_argument(self, services) -> None:
        """Passing document_id stores it directly without querying Google."""
        docs, drive = services
        with patch("gselib.logbook.logbook.get_services", return_value=(docs, drive)):
            lb = Logbook(document_id="explicit-id")
        assert lb.document_id == "explicit-id"

    def test_document_id_from_env(self, services, monkeypatch: pytest.MonkeyPatch) -> None:
        """LOGBOOK_DOCUMENT_ID env var is used when document_id is not passed."""
        monkeypatch.setenv("LOGBOOK_DOCUMENT_ID", "env-doc-id")
        docs, drive = services
        with patch("gselib.logbook.logbook.get_services", return_value=(docs, drive)):
            lb = Logbook()
        assert lb.document_id == "env-doc-id"

    def test_missing_document_id_raises(self, services, monkeypatch: pytest.MonkeyPatch) -> None:
        """Raises ValueError when no document_id is given and env var is unset."""
        monkeypatch.delenv("LOGBOOK_DOCUMENT_ID", raising=False)
        docs, drive = services
        with patch("gselib.logbook.logbook.get_services", return_value=(docs, drive)):
            with pytest.raises(ValueError, match="LOGBOOK_DOCUMENT_ID"):
                Logbook()

    def test_create_title_makes_new_document(self, services) -> None:
        """Passing create_title creates a new Google Doc and stores the new ID."""
        docs, drive = services
        with (
            patch("gselib.logbook.logbook.get_services", return_value=(docs, drive)),
            patch("gselib.logbook.logbook.create_document", return_value="new-doc-id") as mock_create,
            patch("gselib.logbook.logbook.apply_logbook_template") as mock_template,
        ):
            lb = Logbook(create_title="My Logbook")
        assert lb.document_id == "new-doc-id"
        mock_create.assert_called_once_with(docs, "My Logbook")
        mock_template.assert_called_once_with(docs, "new-doc-id", "My Logbook")


class TestLogbookAppend:
    def test_append_inserts_text(self, logbook) -> None:
        """append calls batchUpdate with an insertText request."""
        lb, docs, _ = logbook
        docs.documents().get().execute.return_value = _make_doc(end_index=20)
        lb.append("beam on")
        body = docs.documents().batchUpdate.call_args.kwargs["body"]
        insert = next(r for r in body["requests"] if "insertText" in r)
        assert "beam on" in insert["insertText"]["text"]

    def test_append_inserts_at_end_index(self, logbook) -> None:
        """append inserts at the last content element's endIndex minus 1."""
        lb, docs, _ = logbook
        docs.documents().get().execute.return_value = _make_doc(end_index=50)
        lb.append("test")
        body = docs.documents().batchUpdate.call_args.kwargs["body"]
        insert = next(r for r in body["requests"] if "insertText" in r)
        assert insert["insertText"]["location"]["index"] == 50

    def test_append_styles_timestamp_bold(self, logbook) -> None:
        """append includes an updateTextStyle request that sets bold on the timestamp."""
        lb, docs, _ = logbook
        lb.append("test entry")
        body = docs.documents().batchUpdate.call_args.kwargs["body"]
        style = next(r for r in body["requests"] if "updateTextStyle" in r)
        assert style["updateTextStyle"]["textStyle"]["bold"] is True

    def test_append_prints_confirmation(self, logbook, capsys: pytest.CaptureFixture) -> None:
        """append prints the timestamped entry to stdout."""
        lb, _, _ = logbook
        lb.append("ring current 102 mA")
        output = capsys.readouterr().out
        assert "ring current 102 mA" in output


class TestLogbookSave:
    def _setup_drive(self, drive, content: bytes = b"%PDF-content") -> None:
        drive.files().export_media().execute.return_value = content

    def test_save_pdf(self, logbook, tmp_path) -> None:
        """save exports as application/pdf for a .pdf path."""
        lb, _, drive = logbook
        self._setup_drive(drive)
        dest = tmp_path / "logbook.pdf"
        lb.save(str(dest))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert call_kwargs["mimeType"] == "application/pdf"
        assert dest.exists()

    def test_save_docx(self, logbook, tmp_path) -> None:
        """save exports as the Word MIME type for a .docx path."""
        lb, _, drive = logbook
        self._setup_drive(drive)
        dest = tmp_path / "logbook.docx"
        lb.save(str(dest))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert "wordprocessingml" in call_kwargs["mimeType"]

    def test_save_txt(self, logbook, tmp_path) -> None:
        """save exports as text/plain for a .txt path."""
        lb, _, drive = logbook
        self._setup_drive(drive, b"plain text")
        dest = tmp_path / "logbook.txt"
        lb.save(str(dest))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert call_kwargs["mimeType"] == "text/plain"

    def test_save_md(self, logbook, tmp_path) -> None:
        """save exports as text/plain for a .md path."""
        lb, _, drive = logbook
        self._setup_drive(drive, b"# Logbook")
        dest = tmp_path / "logbook.md"
        lb.save(str(dest))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert call_kwargs["mimeType"] == "text/plain"

    def test_save_unknown_extension_defaults_to_pdf(self, logbook, tmp_path) -> None:
        """An unrecognised extension falls back to application/pdf."""
        lb, _, drive = logbook
        self._setup_drive(drive)
        dest = tmp_path / "logbook.xyz"
        lb.save(str(dest))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert call_kwargs["mimeType"] == "application/pdf"

    def test_save_creates_missing_directories(self, logbook, tmp_path) -> None:
        """save creates intermediate directories that don't yet exist."""
        lb, _, drive = logbook
        self._setup_drive(drive)
        dest = tmp_path / "subdir" / "nested" / "logbook.pdf"
        lb.save(str(dest))
        assert dest.exists()

    def test_save_writes_correct_content(self, logbook, tmp_path) -> None:
        """The bytes returned by the Drive API are written verbatim to disk."""
        lb, _, drive = logbook
        self._setup_drive(drive, b"expected-bytes")
        dest = tmp_path / "out.pdf"
        lb.save(str(dest))
        assert dest.read_bytes() == b"expected-bytes"

    def test_save_uses_document_id(self, logbook, tmp_path) -> None:
        """save passes the logbook's document_id as fileId to the Drive API."""
        lb, _, drive = logbook
        self._setup_drive(drive)
        lb.save(str(tmp_path / "out.pdf"))
        call_kwargs = drive.files().export_media.call_args.kwargs
        assert call_kwargs["fileId"] == "doc-123"


class TestLogbookShare:
    def test_share_calls_share_document(self, logbook) -> None:
        """share delegates to share_document with the correct arguments."""
        lb, _, drive = logbook
        with patch("gselib.logbook.logbook.share_document") as mock_share:
            lb.share("alice@example.com", "writer")
        mock_share.assert_called_once_with(drive, "doc-123", "alice@example.com", "writer")

    def test_share_default_role_is_writer(self, logbook) -> None:
        """share uses 'writer' as the default role."""
        lb, _, drive = logbook
        with patch("gselib.logbook.logbook.share_document") as mock_share:
            lb.share("alice@example.com")
        assert mock_share.call_args.args[3] == "writer"

    def test_share_prints_confirmation(self, logbook, capsys: pytest.CaptureFixture) -> None:
        """share prints a confirmation line to stdout."""
        lb, _, _ = logbook
        with patch("gselib.logbook.logbook.share_document"):
            lb.share("alice@example.com", "reader")
        output = capsys.readouterr().out
        assert "alice@example.com" in output
