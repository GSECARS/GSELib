#!/usr/bin/python3
# ----------------------------------------------------------------------------------
# Project: GSELib
# File: version.py
# ----------------------------------------------------------------------------------
# Purpose:
# This file is used to update the version by settting/updating the .static-version
# file in the root directory of the package. It is also used to update the version
# of the application toml file.
# ----------------------------------------------------------------------------------
# Author: Christofanis Skordas
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------------

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


__all__ = ["Version"]


@dataclass
class Version:

    static_version_file: Path = field(compare=False, repr=False)
    toml_file: Optional[Path] = field(compare=False, repr=False, default=None)

    def check_static_version(self) -> str:
        """Checks for the latest static version. If not available, set it to 0.0.1."""
        try:
            # Read the static version file
            with open(self.static_version_file, "r") as file:
                version = file.read().strip()
        except FileNotFoundError:
            # If the file is not available, set it to 0.0.1
            version = "0.0.1"
        return version

    def set(self, version: str) -> None:
        """Set the version to the given version."""
        self._write_static_version(version=version)
        if self.toml_file:
            self._update_pyproject_toml_file(version=version)

    def update(self) -> None:
        """Update the version to the latest"""

        # Get the latest version prioriotizing the git tags
        version = self._check_tags()
        if not version:
            version = self.check_static_version()

        # Write the version to the static file and update the toml file if available
        self._write_static_version(version=version)
        if self.toml_file:
            self._update_pyproject_toml_file(version=version)

    def _check_tags(self) -> str | None:
        """Check if there are any git tags available."""
        try:
            # Check for the latest tag
            git_tag = subprocess.check_output(["git", "describe", "--tags"]).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            # If there is no tag available, set it to None
            git_tag = None
        return git_tag

    def _write_static_version(self, version: str) -> None:
        """Write the static version to the file."""
        with open(self.static_version_file, "w") as file:
            file.write(f"{version}\n")

    def _update_pyproject_toml_file(self, version: str) -> None:
        """Updates the version of the project in the pyproject.toml file."""
        if not self.toml_file:
            return

        # Read the toml file
        with open(self.toml_file, "r") as file:
            pyproject_toml = file.readlines()

        # Flag to check if inside the [project] section
        in_project_section = False

        if pyproject_toml:

            # Find the line with the version and update it
            for i, line in enumerate(pyproject_toml):
                stripped_line = line.strip()
                if stripped_line.startswith("[") and stripped_line.endswith("]"):
                    # We are starting a new section
                    in_project_section = stripped_line == "[project]"
                elif "version" in line and in_project_section:
                    # Update the version
                    pyproject_toml[i] = f'version = "{version}"\n'
                    break

            # Write the updated file
            with open(self.toml_file, "w") as file:
                file.writelines(pyproject_toml)


if __name__ == "__main__":
    # Set the paths
    static_version_file = Path(__file__).resolve().parent.parent / ".static-version"
    toml_file = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    # Update the version using git tags if available, with a fallback to the static version.
    version = Version(static_version_file=static_version_file, toml_file=toml_file)
    version.update()
