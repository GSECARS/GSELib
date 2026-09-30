# SPDX-License-Identifier: MIT

import pytest

pytest.importorskip("requests")
pytest.importorskip("paramiko")

from unittest.mock import MagicMock, patch

from gselib import main


def _run(*argv: str) -> None:
    with patch("sys.argv", ["gselib", *argv]):
        main()


class TestNextcloudCLIHelp:
    def test_cloud_help(self) -> None:
        """gselib cloud --help exits 0."""
        with pytest.raises(SystemExit) as exc:
            _run("cloud", "--help")
        assert exc.value.code == 0

    def test_nextcloud_help(self) -> None:
        """gselib cloud nextcloud --help exits 0."""
        with pytest.raises(SystemExit) as exc:
            _run("cloud", "nextcloud", "--help")
        assert exc.value.code == 0


class TestNextcloudCLIShares:
    def _mock_client(self, shares=None):
        mock = MagicMock()
        mock.share_with_many.return_value = [{"id": 1, "share_with": "alice"}]
        mock.list_shares.return_value = shares or [{"id": 1, "path": "/data", "share_with": "alice"}]
        return mock

    def test_share_command(self, capsys: pytest.CaptureFixture) -> None:
        """share command calls share_with_many with the correct path, recipient, and permissions."""
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value = self._mock_client()
            _run(
                "cloud",
                "nextcloud",
                "--url",
                "https://cloud.example.com",
                "--user",
                "admin",
                "--password",
                "secret",
                "share",
                "--nc-path",
                "/data",
                "--recipients",
                "alice",
                "--permissions",
                "read",
            )
        mock_cls.return_value.share_with_many.assert_called_once_with("/data", ["alice"], 1)

    def test_share_multiple_permissions(self) -> None:
        """share command ORs multiple permission flags into a bitmask."""
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value = self._mock_client()
            _run(
                "cloud",
                "nextcloud",
                "--url",
                "https://cloud.example.com",
                "--user",
                "admin",
                "--password",
                "secret",
                "share",
                "--nc-path",
                "/data",
                "--recipients",
                "alice",
                "--permissions",
                "read",
                "update",
            )
        _, kwargs = mock_cls.return_value.share_with_many.call_args
        assert mock_cls.return_value.share_with_many.call_args.args[2] == 3  # read(1) | update(2)

    def test_list_shares_command(self, capsys: pytest.CaptureFixture) -> None:
        """list-shares command calls list_shares and logs output."""
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value = self._mock_client()
            _run(
                "cloud",
                "nextcloud",
                "--url",
                "https://cloud.example.com",
                "--user",
                "admin",
                "--password",
                "secret",
                "list-shares",
            )
        mock_cls.return_value.list_shares.assert_called_once_with(path=None)

    def test_list_shares_with_path(self) -> None:
        """list-shares --nc-path passes the path filter to list_shares."""
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value = self._mock_client()
            _run(
                "cloud",
                "nextcloud",
                "--url",
                "https://cloud.example.com",
                "--user",
                "admin",
                "--password",
                "secret",
                "list-shares",
                "--nc-path",
                "/data",
            )
        mock_cls.return_value.list_shares.assert_called_once_with(path="/data")

    def test_delete_share_command(self) -> None:
        """delete-share command calls delete_share with the given ID."""
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value = self._mock_client()
            _run(
                "cloud",
                "nextcloud",
                "--url",
                "https://cloud.example.com",
                "--user",
                "admin",
                "--password",
                "secret",
                "delete-share",
                "--id",
                "7",
            )
        mock_cls.return_value.delete_share.assert_called_once_with(7)


class TestNextcloudCLIStorages:
    def _mock_occ(self, mounts=None):
        mock = MagicMock()
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__ = MagicMock(return_value=False)
        mock.create_local_storage.return_value = {"id": 3, "mount_point": "/TestMount"}
        mock.list_storages.return_value = mounts or [{"mount_id": 1, "mount_point": "/TestMount"}]
        return mock

    def test_create_storage_local(self) -> None:
        """create-storage without SSH flags calls NextcloudOCC with no host."""
        with patch("gselib.cloud.nextcloud.NextcloudOCC") as mock_cls:
            mock_cls.return_value = self._mock_occ()
            _run(
                "cloud",
                "nextcloud",
                "--occ-cmd",
                "php occ",
                "create-storage",
                "--mount",
                "TestMount",
                "--path",
                "/srv/data",
            )
        mock_cls.assert_called_once_with(occ_cmd="php occ")
        mock_cls.return_value.create_local_storage.assert_called_once_with("TestMount", "/srv/data", None, None)

    def test_create_storage_with_users(self) -> None:
        """create-storage --users passes the user list to create_local_storage."""
        with patch("gselib.cloud.nextcloud.NextcloudOCC") as mock_cls:
            mock_cls.return_value = self._mock_occ()
            _run(
                "cloud",
                "nextcloud",
                "--occ-cmd",
                "php occ",
                "create-storage",
                "--mount",
                "TestMount",
                "--path",
                "/srv/data",
                "--users",
                "alice",
                "bob",
            )
        mock_cls.return_value.create_local_storage.assert_called_once_with("TestMount", "/srv/data", ["alice", "bob"], None)

    def test_list_storages_command(self) -> None:
        """list-storages command calls list_storages on the OCC instance."""
        with patch("gselib.cloud.nextcloud.NextcloudOCC") as mock_cls:
            mock_cls.return_value = self._mock_occ()
            _run(
                "cloud",
                "nextcloud",
                "--occ-cmd",
                "php occ",
                "list-storages",
            )
        mock_cls.return_value.list_storages.assert_called_once()

    def test_delete_storage_command(self) -> None:
        """delete-storage command calls delete_storage with the given ID."""
        with patch("gselib.cloud.nextcloud.NextcloudOCC") as mock_cls:
            mock_cls.return_value = self._mock_occ()
            _run(
                "cloud",
                "nextcloud",
                "--occ-cmd",
                "php occ",
                "delete-storage",
                "--id",
                "3",
            )
        mock_cls.return_value.delete_storage.assert_called_once_with(3)


class TestNextcloudCLIEnvFallback:
    def test_url_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """NEXTCLOUD_URL env var is used when --url is not passed."""
        monkeypatch.setenv("NEXTCLOUD_URL", "https://env.example.com")
        monkeypatch.setenv("NEXTCLOUD_USER", "admin")
        monkeypatch.setenv("NEXTCLOUD_PASSWORD", "secret")
        with patch("gselib.cloud.nextcloud.NextcloudClient") as mock_cls:
            mock_cls.return_value.list_shares.return_value = []
            _run("cloud", "nextcloud", "list-shares")
        mock_cls.assert_called_once_with("https://env.example.com", "admin", "secret")

    def test_occ_cmd_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """NEXTCLOUD_OCC_CMD env var is used when --occ-cmd is not passed."""
        monkeypatch.setenv("NEXTCLOUD_OCC_CMD", "php /var/www/html/occ")
        with patch("gselib.cloud.nextcloud.NextcloudOCC") as mock_cls:
            occ = MagicMock()
            occ.__enter__ = MagicMock(return_value=occ)
            occ.__exit__ = MagicMock(return_value=False)
            occ.list_storages.return_value = []
            mock_cls.return_value = occ
            _run("cloud", "nextcloud", "list-storages")
        mock_cls.assert_called_once_with(occ_cmd="php /var/www/html/occ")

    def test_missing_url_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing --url and NEXTCLOUD_URL causes a non-zero exit."""
        monkeypatch.delenv("NEXTCLOUD_URL", raising=False)
        with pytest.raises(SystemExit) as exc:
            _run("cloud", "nextcloud", "list-shares")
        assert exc.value.code != 0
