# SPDX-License-Identifier: MIT

import json
import os
import re
import shlex
import subprocess


class NextcloudOCC:
    def __init__(self, host: str = None, user: str = None, key_path: str = None, password: str = None, port: int = 22, occ_cmd: str = None) -> None:
        """Initializes OCC runner. Skip the host to run commands locally via subprocess."""
        self._host = host
        self._user = user
        self._key_path = key_path
        self._password = password
        self._port = port
        self._occ_cmd = occ_cmd
        self._ssh = None

    def _connect(self):
        """Opens and caches the SSH connection."""
        if self._ssh is None:
            import paramiko

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            kwargs: dict = {"username": self._user, "port": self._port}
            if self._key_path:
                kwargs["key_filename"] = os.path.expanduser(self._key_path)
                kwargs["look_for_keys"] = False
            elif self._password:
                kwargs["password"] = self._password
                kwargs["look_for_keys"] = False
                kwargs["allow_agent"] = False
            client.connect(self._host, **kwargs)
            self._ssh = client
        return self._ssh

    def _run(self, occ_args: str, env_vars: dict = None) -> str:
        """Runs an occ command locally or over SSH and returns stdout."""
        if self._occ_cmd is None:
            raise ValueError("occ_cmd is required. Pass it to NextcloudOCC() or set NEXTCLOUD_OCC_CMD.")
        cmd = f"{self._occ_cmd} --no-interaction {occ_args}"
        if self._host:
            ssh = self._connect()
            if env_vars:
                exports = " ".join(f"export {k}={shlex.quote(str(v))};" for k, v in env_vars.items())
                cmd = f"{exports} {cmd}"
            _, stdout, stderr = ssh.exec_command(cmd)
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
        else:
            run_env = {**os.environ, **(env_vars or {})}
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=run_env)
            exit_code = result.returncode
            out = result.stdout.strip()
            err = result.stderr.strip()
        if exit_code != 0:
            raise RuntimeError(f"occ failed (exit {exit_code}): {err or out}")
        return out

    def create_local_storage(self, mount_point: str, server_path: str, applicable_users: list[str] = None, applicable_groups: list[str] = None) -> dict:
        """Creates a local-path external storage mount."""
        args = ["files_external:create", "--output=json", shlex.quote(mount_point), "local", "null::null", f"--config=datadir={server_path}"]
        out = self._run(" ".join(args))
        try:
            result = json.loads(out)
            data = {"id": result, "mount_point": mount_point} if isinstance(result, int) else result
        except json.JSONDecodeError:
            match = re.search(r"\b(\d+)\b", out)
            data = {"id": int(match.group(1)) if match else None, "mount_point": mount_point}
        mount_id = data.get("id")
        if mount_id is not None:
            if applicable_users:
                user_args = " ".join(f"--add-user={shlex.quote(u)}" for u in applicable_users)
                self._run(f"files_external:applicable {mount_id} {user_args}")
            if applicable_groups:
                group_args = " ".join(f"--add-group={shlex.quote(g)}" for g in applicable_groups)
                self._run(f"files_external:applicable {mount_id} {group_args}")
        return data

    def create_user(self, uid: str, display_name: str, email: str, password: str) -> None:
        """Creates a new local Nextcloud user. Sends a welcome/activation email so the user sets their own password."""
        args = f"user:add --password-from-env --display-name={shlex.quote(display_name)} --email={shlex.quote(email)} --send-welcome-email {shlex.quote(uid)}"
        self._run(args, env_vars={"OC_PASS": password})

    def list_users(self, search: str = None) -> dict:
        """Returns Nextcloud users as {uid: display_name}. Optionally filtered by search pattern."""
        cmd = "user:list --output=json"
        if search:
            cmd += f" {shlex.quote(search)}"
        return json.loads(self._run(cmd))

    def list_storages(self) -> list:
        """Returns all configured external storage mounts."""
        return json.loads(self._run("files_external:list --output=json"))

    def delete_storage(self, mount_id: int) -> None:
        """Deletes an external storage mount by its ID."""
        self._run(f"files_external:delete {mount_id}")

    def close(self) -> None:
        """Closes the SSH connection if open."""
        if self._ssh:
            self._ssh.close()
            self._ssh = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
