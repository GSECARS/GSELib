# SPDX-License-Identifier: MIT

import functools
import re
from importlib.metadata import requires
from importlib.util import find_spec

__all__ = ["available", "require"]


def _load_groups() -> dict[str, tuple[str, ...]]:
    """Builds a map of extras group to package names from installed package metadata."""
    groups: dict[str, list[str]] = {}
    for req in requires("gselib") or []:
        match = re.search(r'extra == ["\'](\w+)["\']', req)
        if match:
            pkg = re.match(r"[A-Za-z0-9_.-]+", req).group(0)
            groups.setdefault(match.group(1), []).append(pkg)
    return {k: tuple(v) for k, v in groups.items()}


_GROUPS = _load_groups()


def available(group: str) -> bool:
    """Returns True if all packages for the given dependency group are installed."""
    return all(find_spec(pkg) is not None for pkg in _GROUPS.get(group, ()))


def require(group: str):
    """Decorator that raises SystemExit if any package in the dependency group is missing."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing = [pkg for pkg in _GROUPS.get(group, ()) if find_spec(pkg) is None]
            if missing:
                raise SystemExit(f"Missing packages for '{group}': {', '.join(missing)}. Run: pip install 'gselib[{group}]'")
            return func(*args, **kwargs)

        return wrapper

    return decorator
