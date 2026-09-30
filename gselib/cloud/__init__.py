# SPDX-License-Identifier: MIT

from gselib.cloud.nextcloud import add_nextcloud_subparser, run_nextcloud_command
from gselib.deps import available

if available("cloud"):
    from gselib.cloud.nextcloud import NextcloudClient, NextcloudOCC

__all__ = ["NextcloudClient", "NextcloudOCC"]


def add_cloud_subparser(subparsers) -> None:
    """Register the cloud subcommand on the given subparsers."""
    if not available("cloud"):
        return

    cloud = subparsers.add_parser("cloud", help="cloud storage and share management")
    services = cloud.add_subparsers(dest="cloud_service", metavar="service", required=True)
    add_nextcloud_subparser(services)


def run_cloud_command(args) -> None:
    """Dispatch a parsed cloud command to the appropriate service handler."""
    if args.cloud_service == "nextcloud":
        run_nextcloud_command(args)
