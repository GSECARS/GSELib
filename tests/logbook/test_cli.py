# SPDX-License-Identifier: MIT

import pytest

pytest.importorskip("google.oauth2")
pytest.importorskip("googleapiclient")
pytest.importorskip("dotenv")

from unittest.mock import MagicMock, patch

from gselib import main


def _run(*argv: str) -> None:
    with patch("sys.argv", ["gselib", *argv]):
        main()


def _mock_logbook(document_id: str = "doc-123") -> MagicMock:
    lb = MagicMock()
    lb.document_id = document_id
    return lb


class TestLogbookCLIHelp:
    def test_logbook_help(self) -> None:
        """gselib logbook --help exits 0."""
        with pytest.raises(SystemExit) as exc:
            _run("logbook", "--help")
        assert exc.value.code == 0

    def test_logbook_append_help(self) -> None:
        """gselib logbook append --help exits 0."""
        with pytest.raises(SystemExit) as exc:
            _run("logbook", "append", "--help")
        assert exc.value.code == 0


class TestLogbookCLIAppend:
    def test_append_command(self) -> None:
        """append command calls logbook.append with the given text."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "append", "beam on")
        lb.append.assert_called_once_with("beam on")

    def test_append_passes_doc_id(self) -> None:
        """--doc-id is forwarded to the Logbook constructor."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb) as mock_cls:
            _run("logbook", "--doc-id", "my-doc", "append", "test")
        assert mock_cls.call_args.kwargs["document_id"] == "my-doc"

    def test_append_passes_env_file(self) -> None:
        """--env is forwarded to the Logbook constructor."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb) as mock_cls:
            _run("logbook", "--env", "/custom/.env", "append", "test")
        assert mock_cls.call_args.kwargs["env_file"] == "/custom/.env"


class TestLogbookCLISave:
    def test_save_command(self, tmp_path) -> None:
        """save command calls logbook.save with the given path."""
        lb = _mock_logbook()
        dest = str(tmp_path / "out.pdf")
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "save", dest)
        lb.save.assert_called_once_with(dest)


class TestLogbookCLICreate:
    def test_create_command(self, capsys: pytest.CaptureFixture) -> None:
        """create command instantiates Logbook with create_title and prints the document ID."""
        lb = _mock_logbook("new-doc-id")
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "create", "My Logbook")
        output = capsys.readouterr().out
        assert "new-doc-id" in output

    def test_create_passes_title(self) -> None:
        """create command passes the title as create_title to Logbook."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb) as mock_cls:
            _run("logbook", "create", "My Logbook")
        assert mock_cls.call_args.kwargs["create_title"] == "My Logbook"


class TestLogbookCLIShare:
    def test_share_command(self) -> None:
        """share command calls logbook.share with the email and mapped role."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "share", "user@example.com")
        lb.share.assert_called_once_with("user@example.com", "writer")

    def test_share_viewer_role(self) -> None:
        """--role viewer maps to 'reader' for the Drive API."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "share", "user@example.com", "--role", "viewer")
        lb.share.assert_called_once_with("user@example.com", "reader")

    def test_share_commenter_role(self) -> None:
        """--role commenter passes through as 'commenter'."""
        lb = _mock_logbook()
        with patch("gselib.logbook.logbook.Logbook", return_value=lb):
            _run("logbook", "share", "user@example.com", "--role", "commenter")
        lb.share.assert_called_once_with("user@example.com", "commenter")


class TestLogbookCLIEnvFallback:
    def test_doc_id_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """LOGBOOK_DOCUMENT_ID is used when --doc-id is not passed."""
        monkeypatch.setenv("LOGBOOK_DOCUMENT_ID", "env-doc-id")
        lb = _mock_logbook("env-doc-id")
        with patch("gselib.logbook.logbook.Logbook", return_value=lb) as mock_cls:
            _run("logbook", "append", "test")
        assert mock_cls.call_args.kwargs["document_id"] is None
