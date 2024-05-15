#!/usr/bin/python3
# ----------------------------------------------------------------------------------
# Project: GSELib
# File: paths.py
# ----------------------------------------------------------------------------------
# Purpose:
# This file contains the PathModel dataclass that is used to manage the directory
# paths.
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

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


@dataclass
class AssetPathModel:
    """Dataclass to manage the paths of the assets directory."""

    assets_dir: str = field(compare=False, repr=False)

    _assets_path: str = field(init=False, compare=False)
    _icon_path: str = field(init=False, compare=False)
    _style_path: str = field(init=False, compare=False)

    def __post_init__(self) -> None:
        self._assets_path = Path(self.assets_dir).absolute().as_posix()
        self._icon_path = PurePosixPath(self._assets_path).joinpath("icons").as_posix()
        self._style_path = PurePosixPath(self._assets_path).joinpath("styles").as_posix()

    @property
    def icon_path(self) -> str:
        """Return the path to the icons directory."""
        return self._icon_path

    @property
    def style_path(self) -> str:
        """Return the path to the styles directory."""
        return self._style_path
