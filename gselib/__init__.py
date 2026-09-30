# SPDX-License-Identifier: MIT

import logging
import sys
from argparse import ArgumentParser
from importlib.metadata import version

from gselib.cloud import add_cloud_subparser, run_cloud_command

__version__ = version("gselib")
__all__ = ["__version__", "main"]


def make_parser() -> ArgumentParser:
    """Builds the gselib argument parser."""
    parser = ArgumentParser(f"gselib {__version__}")
    parser.add_argument("-t", "--test", action="store_true", help="runs the test suite")

    subparsers = parser.add_subparsers(dest="tool", metavar="tool")
    add_cloud_subparser(subparsers)

    return parser


def main() -> None:
    """Runs the gselib CLI."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout, force=True)
    parser = make_parser()
    args = parser.parse_args()

    if args.test:
        import pytest

        raise SystemExit(pytest.main([]))

    if args.tool == "cloud":
        run_cloud_command(args)
        return

    parser.print_help()
