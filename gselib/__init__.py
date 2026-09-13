# SPDX-License-Identifier: MIT

from argparse import ArgumentParser
from importlib.metadata import version

__version__ = version("gselib")
__all__ = ["__version__", "main"]


def make_parser() -> ArgumentParser:
    """Builds the gselib argument parser."""
    parser = ArgumentParser("gselib")
    parser.add_argument("-v", "--version", action="version", version=f"gselib {version('gselib')}")
    parser.add_argument("-t", "--test", action="store_true", help="runs the test suite")

    return parser


def main() -> None:
    """Runs the gselib CLI."""

    parser = make_parser()
    args = parser.parse_args()

    if args.test:
        import pytest

        raise SystemExit(pytest.main([]))

    parser.print_help()
