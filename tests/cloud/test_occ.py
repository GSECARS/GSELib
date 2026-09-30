# SPDX-License-Identifier: MIT

import json

import pytest

pytest.importorskip("paramiko")

from unittest.mock import MagicMock, patch

from gselib.cloud.nextcloud.occ import NextcloudOCC


@pytest.fixture
def local_occ() -> NextcloudOCC:
    return NextcloudOCC(occ_cmd="php occ")


@pytest.fixture
def remote_occ() -> NextcloudOCC:
    return NextcloudOCC(host="server.example.com", user="admin", password="secret", occ_cmd="php occ")


def _proc(stdout: str = "", returncode: int = 0) -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.stderr = ""
    mock.returncode = returncode
    return mock


class TestNextcloudOCCLocal:
    def test_run_raises_without_occ_cmd(self) -> None:
        """_run raises ValueError when no occ_cmd was provided."""
        occ = NextcloudOCC()
        with pytest.raises(ValueError, match="occ_cmd is required"):
            occ._run("files_external:list")

    def test_run_includes_no_interaction(self, local_occ: NextcloudOCC) -> None:
        """Every occ invocation passes --no-interaction to suppress prompts."""
        with patch("subprocess.run", return_value=_proc("ok")) as mock:
            local_occ._run("files_external:list")
        cmd = mock.call_args.args[0]
        assert "--no-interaction" in cmd

    def test_run_failure_raises_runtime_error(self, local_occ: NextcloudOCC) -> None:
        """A non-zero exit code raises RuntimeError with the occ error text."""
        with patch("subprocess.run", return_value=_proc("error output", returncode=1)):
            with pytest.raises(RuntimeError, match="occ failed"):
                local_occ._run("files_external:list")

    def test_create_local_storage_dict_result(self, local_occ: NextcloudOCC) -> None:
        """When occ returns a JSON object it is passed through directly."""
        data = {"id": 3, "mount_point": "/TestMount"}
        with patch("subprocess.run", return_value=_proc(json.dumps(data))):
            result = local_occ.create_local_storage("TestMount", "/srv/data")
        assert result == data

    def test_create_local_storage_int_result(self, local_occ: NextcloudOCC) -> None:
        """When occ returns a bare integer it is wrapped with the mount_point name."""
        with patch("subprocess.run", return_value=_proc("3")):
            result = local_occ.create_local_storage("TestMount", "/srv/data")
        assert result["id"] == 3
        assert result["mount_point"] == "TestMount"

    def test_create_local_storage_fallback_parse(self, local_occ: NextcloudOCC) -> None:
        """When occ returns plain text the first integer found is used as the ID."""
        with patch("subprocess.run", return_value=_proc("Storage with id 7 created.")):
            result = local_occ.create_local_storage("TestMount", "/srv/data")
        assert result["id"] == 7
        assert result["mount_point"] == "TestMount"

    def test_create_local_storage_with_users(self, local_occ: NextcloudOCC) -> None:
        """applicable_users are applied via files_external:applicable --add-user."""
        with patch("subprocess.run", return_value=_proc("1")) as mock:
            local_occ.create_local_storage("Mount", "/path", applicable_users=["alice", "bob"])
        calls = [c.args[0] for c in mock.call_args_list]
        applicable_cmd = next(c for c in calls if "files_external:applicable" in c)
        assert "--add-user=alice" in applicable_cmd
        assert "--add-user=bob" in applicable_cmd

    def test_create_local_storage_with_groups(self, local_occ: NextcloudOCC) -> None:
        """applicable_groups are applied via files_external:applicable --add-group."""
        with patch("subprocess.run", return_value=_proc("1")) as mock:
            local_occ.create_local_storage("Mount", "/path", applicable_groups=["scientists"])
        calls = [c.args[0] for c in mock.call_args_list]
        applicable_cmd = next(c for c in calls if "files_external:applicable" in c)
        assert "--add-group=scientists" in applicable_cmd

    def test_create_local_storage_no_users_or_groups(self, local_occ: NextcloudOCC) -> None:
        """Omitting users and groups skips the files_external:applicable call."""
        with patch("subprocess.run", return_value=_proc("1")) as mock:
            local_occ.create_local_storage("Mount", "/path")
        calls = [c.args[0] for c in mock.call_args_list]
        assert not any("files_external:applicable" in c for c in calls)

    def test_list_storages(self, local_occ: NextcloudOCC) -> None:
        """list_storages parses and returns the JSON array from occ."""
        mounts = [{"mount_id": 1, "mount_point": "/TestMount"}]
        with patch("subprocess.run", return_value=_proc(json.dumps(mounts))):
            result = local_occ.list_storages()
        assert result == mounts

    def test_delete_storage(self, local_occ: NextcloudOCC) -> None:
        """delete_storage passes the mount ID to files_external:delete."""
        with patch("subprocess.run", return_value=_proc("")) as mock:
            local_occ.delete_storage(5)
        cmd = mock.call_args.args[0]
        assert "files_external:delete 5" in cmd

    def test_context_manager_returns_self(self, local_occ: NextcloudOCC) -> None:
        """The context manager yields the OCC instance itself."""
        with local_occ as occ:
            assert occ is local_occ

    def test_context_manager_no_error_on_exit(self, local_occ: NextcloudOCC) -> None:
        """Exiting the context manager without an SSH connection does not raise."""
        with local_occ:
            pass


class TestNextcloudOCCRemote:
    def test_connect_with_password(self, remote_occ: NextcloudOCC) -> None:
        """Password auth disables key scanning to avoid ed25519 compatibility errors."""
        with patch("paramiko.SSHClient") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            remote_occ._connect()
        mock_instance.connect.assert_called_once_with(
            "server.example.com",
            username="admin",
            port=22,
            password="secret",
            look_for_keys=False,
            allow_agent=False,
        )

    def test_connect_with_key(self) -> None:
        """Key auth sets key_filename and disables automatic key discovery."""
        occ = NextcloudOCC(host="server.example.com", user="admin", key_path="~/.ssh/id_rsa")
        with patch("paramiko.SSHClient") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            occ._connect()
        call_kwargs = mock_instance.connect.call_args.kwargs
        assert "key_filename" in call_kwargs
        assert call_kwargs["look_for_keys"] is False
        assert "password" not in call_kwargs

    def test_connect_cached(self, remote_occ: NextcloudOCC) -> None:
        """Calling _connect twice reuses the existing connection."""
        with patch("paramiko.SSHClient") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            remote_occ._connect()
            remote_occ._connect()
        mock_instance.connect.assert_called_once()

    def test_connect_sets_missing_host_key_policy(self, remote_occ: NextcloudOCC) -> None:
        """_connect installs a host key policy so unknown hosts are accepted."""
        with patch("paramiko.SSHClient") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            remote_occ._connect()
        mock_instance.set_missing_host_key_policy.assert_called_once()

    def _make_ssh_mock(self, stdout_bytes: bytes = b"output", exit_code: int = 0) -> MagicMock:
        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = exit_code
        mock_stdout.read.return_value = stdout_bytes
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        mock_ssh = MagicMock()
        mock_ssh.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)
        return mock_ssh

    def test_run_ssh_returns_stdout(self, remote_occ: NextcloudOCC) -> None:
        """_run over SSH returns the decoded, stripped stdout."""
        remote_occ._ssh = self._make_ssh_mock(b"result\n")
        result = remote_occ._run("files_external:list")
        assert result == "result"

    def test_run_ssh_includes_no_interaction(self, remote_occ: NextcloudOCC) -> None:
        """SSH commands include --no-interaction just like local ones."""
        remote_occ._ssh = self._make_ssh_mock()
        remote_occ._run("files_external:list")
        cmd = remote_occ._ssh.exec_command.call_args.args[0]
        assert "--no-interaction" in cmd

    def test_run_ssh_failure_raises(self, remote_occ: NextcloudOCC) -> None:
        """A non-zero SSH exit code raises RuntimeError with the stderr message."""
        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = 1
        mock_stdout.read.return_value = b""
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"permission denied"
        mock_ssh = MagicMock()
        mock_ssh.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)
        remote_occ._ssh = mock_ssh
        with pytest.raises(RuntimeError, match="permission denied"):
            remote_occ._run("files_external:list")

    def test_close_disconnects(self, remote_occ: NextcloudOCC) -> None:
        """close() calls SSH close and clears the cached connection."""
        mock_ssh = MagicMock()
        remote_occ._ssh = mock_ssh
        remote_occ.close()
        mock_ssh.close.assert_called_once()
        assert remote_occ._ssh is None

    def test_close_when_not_connected(self, remote_occ: NextcloudOCC) -> None:
        """close() is a no-op when no SSH connection is open."""
        remote_occ.close()

    def test_context_manager_closes_ssh(self, remote_occ: NextcloudOCC) -> None:
        """Exiting the context manager closes the SSH connection."""
        mock_ssh = MagicMock()
        remote_occ._ssh = mock_ssh
        with remote_occ:
            pass
        mock_ssh.close.assert_called_once()
