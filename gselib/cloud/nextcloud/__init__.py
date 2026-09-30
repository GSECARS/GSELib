# SPDX-License-Identifier: MIT

import getpass
import logging
import os
import sys

from gselib.deps import available, require

__all__ = ["NextcloudClient", "NextcloudOCC"]

logger = logging.getLogger(__name__)

_IS_AVAILABLE = available("cloud")

if _IS_AVAILABLE:
    from gselib.cloud.nextcloud.client import NextcloudClient
    from gselib.cloud.nextcloud.occ import NextcloudOCC

    _PERMISSIONS = {
        "read": NextcloudClient.perm_read,
        "update": NextcloudClient.perm_update,
        "create": NextcloudClient.perm_create,
        "delete": NextcloudClient.perm_delete,
        "share": NextcloudClient.perm_share,
        "all": NextcloudClient.perm_all,
    }
else:
    _PERMISSIONS = {}


def add_nextcloud_subparser(subparsers) -> None:
    """Registers the nextcloud subcommand on the subparsers."""
    if not _IS_AVAILABLE:
        return

    nextcloud = subparsers.add_parser("nextcloud", help="Nextcloud storage and share management")

    occ = nextcloud.add_argument_group("OCC - storage commands (env: NEXTCLOUD_OCC_CMD)")
    occ.add_argument("--occ-cmd", metavar="CMD")

    ssh = nextcloud.add_argument_group("SSH - connect to a remote host (env: NEXTCLOUD_SSH_HOST / SSH_USER / SSH_KEY)")
    ssh.add_argument("--ssh-host", metavar="HOST")
    ssh.add_argument("--ssh-user", metavar="USER")
    ssh.add_argument("--ssh-key", metavar="PATH", help="SSH private key (skip to use a password prompt)")

    api = nextcloud.add_argument_group("REST API - share commands (env: NEXTCLOUD_URL / USER / PASSWORD)")
    api.add_argument("--url", metavar="URL")
    api.add_argument("--user", metavar="USER")
    api.add_argument("--password", metavar="PASS", help="skip to use a password prompt")

    commands = nextcloud.add_subparsers(dest="nextcloud_command", metavar="command", required=True)

    p = commands.add_parser("create-storage", help="create a local external storage mount")
    p.add_argument("--mount", required=True, metavar="NAME")
    p.add_argument("--path", required=True, metavar="PATH")
    p.add_argument("--users", nargs="+", metavar="USER")
    p.add_argument("--groups", nargs="+", metavar="GROUP")

    commands.add_parser("list-storages", help="list external storage mounts")

    p = commands.add_parser("delete-storage", help="delete an external storage mount")
    p.add_argument("--id", required=True, type=int, metavar="ID")

    p = commands.add_parser("share", help="share a path with one or more users")
    p.add_argument("--nc-path", required=True, metavar="PATH")
    p.add_argument("--recipients", required=True, nargs="+", metavar="RECIPIENT")
    p.add_argument("--permissions", nargs="+", metavar="PERM", default=["read"], choices=list(_PERMISSIONS))

    p = commands.add_parser("list-shares", help="list shares")
    p.add_argument("--nc-path", metavar="PATH")

    p = commands.add_parser("delete-share", help="remove a share")
    p.add_argument("--id", required=True, type=int, metavar="ID")


@require("cloud")
def run_nextcloud_command(args) -> None:
    """Runs the appropriate handler for the nextcloud command."""
    cmd = args.nextcloud_command

    if cmd in ("create-storage", "list-storages", "delete-storage"):
        with _occ_from_args(args) as occ:
            if cmd == "create-storage":
                mount = occ.create_local_storage(args.mount, args.path, args.users or None, args.groups or None)
                logger.info("Created storage: id=%s  mount=%s", mount.get("id"), mount.get("mount_point"))
            elif cmd == "list-storages":
                mounts = occ.list_storages()
                for m in mounts:
                    logger.info("  id=%-4s %s", m.get("mount_id") or m.get("id", "?"), m.get("mount_point") or m.get("mountPoint", "?"))
            elif cmd == "delete-storage":
                occ.delete_storage(args.id)
                logger.info("Deleted storage id=%s.", args.id)
    else:
        client = _client_from_args(args)

        if cmd == "share":
            bits = sum(_PERMISSIONS[p] for p in args.permissions)
            shares = client.share_with_many(args.nc_path, args.recipients, bits)
            for s in shares:
                logger.info("  Shared %r with %r  (id=%s)", args.nc_path, s.get("share_with") or "?", s.get("id"))
            logger.info("Created %d share(s).", len(shares))
        elif cmd == "list-shares":
            shares = client.list_shares(path=args.nc_path)
            for s in shares:
                logger.info("  id=%-4s %-22s %s", s.get("id", "?"), s.get("path", "?"), s.get("share_with") or "?")
        elif cmd == "delete-share":
            client.delete_share(args.id)
            logger.info("Deleted share id=%s.", args.id)


def _occ_from_args(args) -> "NextcloudOCC":
    """Builds a NextcloudOCC instance from CLI args and environment variables."""
    host = args.ssh_host or os.environ.get("NEXTCLOUD_SSH_HOST")
    occ_cmd = args.occ_cmd or os.environ.get("NEXTCLOUD_OCC_CMD")
    occ_kwargs = {"occ_cmd": occ_cmd} if occ_cmd else {}
    if not host:
        return NextcloudOCC(**occ_kwargs)
    user = args.ssh_user or os.environ.get("NEXTCLOUD_SSH_USER")
    if not user:
        sys.exit("error: --ssh-user is required when --ssh-host is set (or set NEXTCLOUD_SSH_USER)")
    key = args.ssh_key or os.environ.get("NEXTCLOUD_SSH_KEY")
    password = None if key else getpass.getpass(f"SSH password for {user}@{host}: ")
    return NextcloudOCC(host=host, user=user, key_path=key, password=password, **occ_kwargs)


def _client_from_args(args) -> "NextcloudClient":
    """Builds a NextcloudClient instance from CLI args and environment variables."""
    url = args.url or os.environ.get("NEXTCLOUD_URL")
    user = args.user or os.environ.get("NEXTCLOUD_USER")
    password = args.password or os.environ.get("NEXTCLOUD_PASSWORD")
    if not url:
        sys.exit("error: --url is required (or set NEXTCLOUD_URL)")
    if not user:
        sys.exit("error: --user is required (or set NEXTCLOUD_USER)")
    if not password:
        password = getpass.getpass(f"Nextcloud password for {user}: ")
    return NextcloudClient(url, user, password)
